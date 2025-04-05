from flask import Flask, request, jsonify, send_from_directory
from utils.database import (
    init_app, create_user, get_user_by_username,
    create_gesture_password, get_user_gesture_password
)
import os
from bson import ObjectId

app = Flask(__name__)
mongo = init_app(app)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


# Register Route
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    gesture_name = data.get('gesture_name')
    gesture_model_path = data.get('gesture_model_path', 'model.tflite') 

    if not username or not gesture_name:
        return jsonify({'error': 'Missing username or gesture name'}), 400

    if get_user_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    user_id = create_user(username, f'{username}@placeholder.com')
    gesture_id = create_gesture_password(user_id, gesture_name, gesture_model_path)

    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(user_id),
        'gesture_password_id': str(gesture_id)
    })


#Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    gesture_password_id = data.get('gesture_password_id')

    print("Received login data:", data)

    if not username or not gesture_password_id:
        return jsonify({'error': 'Missing username or gesture_password_id'}), 400

    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    stored_id = user.get('gesture_password_id')
    if stored_id and str(stored_id) == gesture_password_id:
        return jsonify({'message': 'Login successful'})
    else:
        return jsonify({'error': 'Gesture does not match'}), 401


# just used to check data 
@app.route('/data')
def get_all_users():
    users = list(mongo.db.users.find())
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        if 'gesture_password_id' in user:
            user['gesture_password_id'] = str(user['gesture_password_id'])
    return jsonify(users)

@app.route('/view')
def view_data_page():
    return send_from_directory('.', 'database_view.html')


if __name__ == '__main__':
    app.run(debug=True, port=5000)
