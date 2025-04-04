from flask_pymongo import PyMongo
import os
from bson.objectid import ObjectId
from datetime import datetime

# MongoDB client will be initialized with the Flask app
mongo = None

def init_app(app):
    """Initialize the MongoDB connection with the Flask app"""
    global mongo
    app.config['MONGO_URI'] = os.environ.get('MONGODB_URI', 
                                          'mongodb://admin:secretpassword@localhost:27017/gesture_auth?authSource=admin')
    mongo = PyMongo(app)
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
def create_gesture_password(user_id, gesture_name, model_path, confidence_threshold=0.85):
    """Create a gesture password for a user"""
    gesture_id = mongo.db.gesture_passwords.insert_one({
        'user_id': ObjectId(user_id),
        'gesture_data': {
            'model_type': 'teachable_machine',
            'gesture_name': gesture_name,
            'gesture_model_path': model_path,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'confidence_threshold': confidence_threshold
        },
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