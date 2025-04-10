
from flask_pymongo import PyMongo
import os
from bson.objectid import ObjectId
from datetime import datetime
import json
import numpy as np

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
def create_gesture_password(user_id, gesture_name, angle_data=None, confidence_threshold=0.85):
    """
    Create a gesture password for a user using hand angle data
    
    Parameters:
    - user_id: User ID
    - gesture_name: Name for this gesture
    - angle_data: Dictionary with angle measurements for all joints
    - confidence_threshold: Minimum confidence level to accept the gesture
    """
    gesture_data = {
        'gesture_name': gesture_name,
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow(),
        'confidence_threshold': confidence_threshold,
        'storage_type': 'angles'
    }
    
    # Store the angle data
    if angle_data:
        # Ensure we have all 10 required angles
        required_angles = [
            "Thumb MCP→IP", "Thumb IP→Tip",
            "Index MCP→PIP", "Index PIP→DIP",
            "Middle MCP→PIP", "Middle PIP→DIP",
            "Ring MCP→PIP", "Ring PIP→DIP",
            "Pinky MCP→PIP", "Pinky PIP→DIP"
        ]
        
        # Clean up and validate angle data
        clean_angles = {}
        for angle_name in required_angles:
            if angle_name in angle_data:
                clean_angles[angle_name] = float(angle_data[angle_name])
            else:
                # Use a default value or raise an error
                clean_angles[angle_name] = 0.0
                
        gesture_data['angle_data'] = clean_angles
    else:
        raise ValueError("Angle data is required for gesture password creation")
    
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

def verify_gesture_angles(stored_angles, current_angles, threshold):
    """
    Verify hand angles against stored angles
    
    Parameters:
    - stored_angles: Dictionary with angle values from database
    - current_angles: Dictionary with angle values from user
    - threshold: Similarity threshold (0.0-1.0) for authentication
    
    Returns:
    - (success, confidence): Tuple with boolean success and float confidence score
    """
    # Calculate the difference between stored and current angles
    angle_differences = []
    max_possible_difference = 180.0  # Maximum possible angle difference in degrees
    
    # Compare each angle
    for angle_name, stored_value in stored_angles.items():
        if angle_name in current_angles:
            current_value = float(current_angles[angle_name])
            
            # Calculate absolute difference in degrees
            diff = abs(stored_value - current_value)
            # Handle wrap-around (e.g., 350° vs 10° should be 20° difference, not 340°)
            if diff > 180.0:
                diff = 360.0 - diff
                
            angle_differences.append(diff)
    
    if not angle_differences:
        return False, 0.0
    
    # Calculate average difference and convert to similarity score
    avg_difference = sum(angle_differences) / len(angle_differences)
    
    # Normalize difference to confidence score (1.0 = identical)
    # Assuming max allowable difference is 45 degrees for a "match"
    max_allowable_diff = 45.0
    confidence = max(0.0, 1.0 - (avg_difference / max_allowable_diff))
    
    # Cap confidence at 1.0
    confidence = min(1.0, confidence)
    
    # Check if confidence exceeds threshold
    success = confidence >= threshold
    
    return success, confidence

def verify_gesture(user_id, gesture_data):
    """
    Verify a gesture against the stored gesture password
    
    Parameters:
    - user_id: User ID
    - gesture_data: Dictionary with angle measurements or numerical confidence score
    
    Returns:
    - (success, confidence): Tuple with boolean success and float confidence score
    """
    # Get user's active gesture password
    gesture_password = get_user_gesture_password(user_id)
    if not gesture_password:
        return False, 0.0
    
    threshold = gesture_password['gesture_data']['confidence_threshold']
    storage_type = gesture_password['gesture_data'].get('storage_type', 'model')
    
    if storage_type == 'angles' and isinstance(gesture_data, dict):
        # We have angle data
        stored_angles = gesture_password['gesture_data']['angle_data']
        return verify_gesture_angles(stored_angles, gesture_data, threshold)
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