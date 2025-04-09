from flask_pymongo import PyMongo
import os
from bson.objectid import ObjectId
from datetime import datetime
import json

# MongoDB client will be initialized with the Flask app
mongo = None
mock_db = None

def init_app(app):
    """Initialize the MongoDB connection with the Flask app"""
    global mongo, mock_db
    
    # Toggle between real and mock database by commenting/uncommenting
    
    # REAL DATABASE CONNECTION
    app.config['MONGO_URI'] = os.environ.get('MONGODB_URI', 
                                         'mongodb://admin:secretpassword@localhost:27017/gesture_auth?authSource=admin')
    
    
    mongo = PyMongo(app)
    print("Connected to:", mongo.db.name)
    return mongo

# User-related functions
def create_user(username, email):
    """Create a new user in the database"""
    user_id = mongo.db.users.insert_one({
        'username': username,
        'email': email,
        'created_at': datetime.utcnow(),
        'last_login': datetime.utcnow(),
        'documents': []
    }).inserted_id
    return user_id

def get_user_by_id(user_id):
    """Get a user by their ID"""
    return mongo.db.users.find_one({'_id': ObjectId(user_id)})

def get_user_by_username(username):
    """Get a user by their username"""
    return mongo.db.users.find_one({'username': username})

# Gesture password functions
def create_gesture_password(user_id, gesture_name, model_path=None, confidence_threshold=0.85, hand_positions=None):
    """
    Create a gesture password for a user
    
    Parameters:
    - user_id: User ID
    - gesture_name: Name for this gesture
    - model_path: Path to teachable machine model (optional)
    - confidence_threshold: Minimum confidence level to accept the gesture
    - hand_positions: List of dictionaries with joint_id, x, y, z coordinates (optional)
    """
    gesture_data = {
        'gesture_name': gesture_name,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'confidence_threshold': confidence_threshold
    }
    
    # Add either model path or hand positions depending on what's provided
    if hand_positions:
        gesture_data['hand_positions'] = hand_positions
        gesture_data['storage_type'] = 'positions'
    else:
        gesture_data['model_type'] = 'teachable_machine'
        gesture_data['gesture_model_path'] = model_path
        gesture_data['storage_type'] = 'model'
    
    gesture_id = mongo.db.gesture_passwords.insert_one({
        'user_id': ObjectId(user_id),
        'gesture_data': gesture_data,
        'active': True
    }).inserted_id
    
    # Update user with gesture password reference
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'gesture_password_id': gesture_id}}
    )
    
    return gesture_id

def get_user_gesture_password(user_id):
    """Get a user's active gesture password"""
    return mongo.db.gesture_passwords.find_one({
        'user_id': ObjectId(user_id),
        'active': True
    })

def verify_gesture_positions(stored_positions, current_positions, threshold):
    """
    Verify hand positions against stored positions
    
    Parameters:
    - stored_positions: List of dictionaries with joint_id, x, y, z from database
    - current_positions: List of dictionaries with joint_id, x, y, z from user
    - threshold: Similarity threshold (0.0-1.0) for authentication
    
    Returns:
    - (success, confidence): Tuple with boolean success and float confidence score
    """
    # Convert lists to dictionaries for easier comparison
    stored_pos_dict = {pos['joint_id']: pos for pos in stored_positions}
    current_pos_dict = {pos['joint_id']: pos for pos in current_positions}
    
    # Calculate similarity score
    total_distance = 0
    joint_count = 0
    
    for joint_id, stored_pos in stored_pos_dict.items():
        if joint_id in current_pos_dict:
            current_pos = current_pos_dict[joint_id]
            
            # Calculate Euclidean distance between points
            distance = (
                (stored_pos['x'] - current_pos['x'])**2 +
                (stored_pos['y'] - current_pos['y'])**2 +
                (stored_pos.get('z', 0) - current_pos.get('z', 0))**2
            )**0.5
            
            total_distance += distance
            joint_count += 1
    
    if joint_count == 0:
        return False, 0.0
    
    # Calculate average distance and convert to similarity score (1.0 = identical)
    avg_distance = total_distance / joint_count
    
    # Normalize distance to confidence score (assuming max distance of 2.0 for fully normalized coordinates)
    max_possible_distance = 2.0  # Maximum possible distance in a normalized 3D space
    confidence = max(0.0, 1.0 - (avg_distance / max_possible_distance))
    
    # Check if confidence exceeds threshold
    success = confidence >= threshold
    
    return success, confidence

def verify_gesture(user_id, gesture_data):
    """
    Verify a gesture against the stored gesture password
    
    Parameters:
    - user_id: User ID
    - gesture_data: Either model result confidence or hand positions
    
    Returns:
    - (success, confidence): Tuple with boolean success and float confidence score
    """
    # Get user's active gesture password
    gesture_password = get_user_gesture_password(user_id)
    if not gesture_password:
        return False, 0.0
    
    threshold = gesture_password['gesture_data']['confidence_threshold']
    storage_type = gesture_password['gesture_data'].get('storage_type', 'model')
    
    if storage_type == 'positions' and isinstance(gesture_data, list):
        # We have position data
        stored_positions = gesture_password['gesture_data']['hand_positions']
        return verify_gesture_positions(stored_positions, gesture_data, threshold)
    elif storage_type == 'model' and isinstance(gesture_data, (int, float)):
        # We have a model confidence score directly
        confidence = float(gesture_data)
        success = confidence >= threshold
        return success, confidence
    else:
        # Incompatible data types
        return False, 0.0

# Document functions
def create_document(user_id, title, content=""):
    """Create a new document for a user"""
    doc_id = mongo.db.documents.insert_one({
        'user_id': ObjectId(user_id),
        'title': title,
        'content': content,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'access_logs': []
    }).inserted_id
    
    # Add reference to the user's document list
    mongo.db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'documents': {
            'document_id': doc_id,
            'title': title,
            'last_accessed': datetime.utcnow()
        }}}
    )
    
    return doc_id

def get_user_documents(user_id):
    """Get all documents for a user"""
    return list(mongo.db.documents.find({'user_id': ObjectId(user_id)}))

def get_document(doc_id, user_id=None):
    """Get a document by ID, optionally checking user_id"""
    query = {'_id': ObjectId(doc_id)}
    if user_id:
        query['user_id'] = ObjectId(user_id)
    return mongo.db.documents.find_one(query)

def update_document(doc_id, content, user_id=None):
    """Update a document's content"""
    query = {'_id': ObjectId(doc_id)}
    if user_id:
        query['user_id'] = ObjectId(user_id)
    
    mongo.db.documents.update_one(
        query,
        {
            '$set': {
                'content': content,
                'updated_at': datetime.utcnow()
            },
            '$push': {
                'access_logs': {
                    'timestamp': datetime.utcnow(),
                    'access_type': 'edit',
                    'gesture_confidence': 1.0  # This would be set from the authentication
                }
            }
        }
    )

# Authentication logs
def log_authentication(user_id, success, confidence, ip_address, user_agent, document_id=None):
    """Log an authentication attempt"""
    log_id = mongo.db.authentication_logs.insert_one({
        'user_id': ObjectId(user_id),
        'timestamp': datetime.utcnow(),
        'success': success,
        'gesture_confidence': confidence,
        'device_info': {
            'ip': ip_address,
            'user_agent': user_agent,
            'device_type': 'unknown'  # Could determine this from user agent
        },
        'document_accessed': ObjectId(document_id) if document_id else None
    }).inserted_id
    
    return log_id