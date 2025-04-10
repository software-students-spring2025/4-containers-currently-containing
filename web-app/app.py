from flask import Flask, request, jsonify, send_from_directory, redirect, render_template
import requests
from database import (
    init_app, create_user, get_user_by_username,
    create_gesture_password, get_user_gesture_password,
    verify_gesture, log_authentication,
    get_user_documents, get_document, update_document, create_document
)
import os

app = Flask(__name__)
mongo = init_app(app)

@app.route('/')
def root():
    return redirect('/home')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/loginregister')
def serve_index():
    return send_from_directory('./templates', 'registerlogin.html')

@app.route('/api/hand-angles')
def proxy_hand_angles():
    try:
        # Internal Docker hostname works here
        response = requests.get("http://gesture_ml_client:5050/hand-angles", timeout=1)
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Could not reach ML client',
            'details': str(e)
        }), 500

# Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    gesture_name = data.get('gesture_name')
    angle_data = data.get('angle_data')

    if not username or not gesture_name or not angle_data:
        return jsonify({'error': 'Missing required fields (username, gesture_name, or angle_data)'}), 400

    if get_user_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    user_id = create_user(username, f"{username}@placeholder.com")
    gesture_id = create_gesture_password(user_id, gesture_name, angle_data=angle_data)

    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(user_id),
        'gesture_password_id': str(gesture_id)
    })

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    angle_data = data.get('angle_data')  # Can be dictionary of angles or confidence score
    gesture_password_id = data.get('gesture_password_id')  # Legacy support

    if not username or (not angle_data and not gesture_password_id):
        return jsonify({'error': 'Missing username or gesture data'}), 400

    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get client info for logging
    client_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    # Method 1: Legacy ID-based authentication
    if gesture_password_id and not angle_data:
        gesture_record = get_user_gesture_password(user['_id'])
        if not gesture_record:
            return jsonify({'error': 'No gesture password found'}), 404
        
        expected_id = str(gesture_record['_id'])
        success = (gesture_password_id == expected_id)
        
        # Log the authentication attempt
        log_authentication(user['_id'], success, 1.0 if success else 0.0, client_ip, user_agent)
        
        if success:
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Gesture does not match'}), 401
    
    # Method 2: Angle-based authentication
    if angle_data:
        success, confidence = verify_gesture(user['_id'], angle_data)
        
        # Log the authentication attempt
        log_authentication(user['_id'], success, confidence, client_ip, user_agent)
        
        if success:
            return jsonify({
                'message': 'Login successful',
                'confidence': confidence
            })
        else:
            return jsonify({
                'error': 'Gesture verification failed',
                'confidence': confidence
            }), 401
    
    # Should not reach here
    return jsonify({'error': 'Invalid request format'}), 400

# Document routes
@app.route('/documents', methods=['GET'])
def get_documents():
    # Check for authentication (this would normally use sessions)
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    documents = get_user_documents(user['_id'])
    
    # Format for JSON response
    doc_list = []
    for doc in documents:
        doc_list.append({
            'id': str(doc['_id']),
            'title': doc['title'],
            'created_at': doc['created_at'].isoformat(),
            'updated_at': doc['updated_at'].isoformat()
        })
    
    return jsonify({'documents': doc_list})

@app.route('/documents', methods=['POST'])
def create_new_document():
    # Check for authentication (this would normally use sessions)
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    title = data.get('title')
    content = data.get('content', '')
    
    if not title:
        return jsonify({'error': 'Missing title'}), 400
    
    doc_id = create_document(user['_id'], title, content)
    
    return jsonify({
        'message': 'Document created successfully',
        'document_id': str(doc_id)
    })

@app.route('/documents/<doc_id>', methods=['GET'])
def view_document(doc_id):
    # Check for authentication (this would normally use sessions)
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    document = get_document(doc_id, user['_id'])
    if not document:
        return jsonify({'error': 'Document not found or access denied'}), 404
    
    return jsonify({
        'id': str(document['_id']),
        'title': document['title'],
        'content': document['content'],
        'created_at': document['created_at'].isoformat(),
        'updated_at': document['updated_at'].isoformat()
    })

@app.route('/documents/<doc_id>', methods=['PUT'])
def update_doc(doc_id):
    # Check for authentication (this would normally use sessions)
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Missing content'}), 400
    
    update_document(doc_id, content, user['_id'])
    
    return jsonify({'message': 'Document updated successfully'})

@app.route('/capture-gesture', methods=['POST'])
def capture_gesture():
    """Endpoint to receive hand angle data from ML client"""
    data = request.get_json()
    username = data.get('username')
    angle_data = data.get('angle_data')
    
    if not username or not angle_data:
        return jsonify({'error': 'Missing username or angle data'}), 400
    
    # Store this data temporarily or use it for training
    # This is a simplified example - you'd typically have more logic here
    
    return jsonify({
        'message': 'Gesture captured successfully',
        'angle_data': angle_data
    })

@app.route('/data')
def get_all_users():
    try:
        users = list(mongo.db.users.find())
        for user in users:
            user['_id'] = str(user['_id'])
            if 'gesture_password_id' in user:
                user['gesture_password_id'] = str(user['gesture_password_id'])
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": "Database fetch failed", "details": str(e)}), 500

@app.route('/view')
def view_data_page():
    return send_from_directory('.', 'database_view.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  
