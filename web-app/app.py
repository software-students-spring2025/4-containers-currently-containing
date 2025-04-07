from flask import Flask, request, jsonify, send_from_directory
from database import (
    init_app, create_user, get_user_by_username,
    create_gesture_password, get_user_gesture_password, verify_gesture
)
import os

app = Flask(__name__)
mongo = init_app(app)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')


# -------------------- REGISTER --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    gesture_name = data.get('gesture_name')
    hand_positions = data.get('hand_positions')

    if not username or not gesture_name or not hand_positions:
        return jsonify({'error': 'Missing required fields (username, gesture_name, or hand_positions)'}), 400

    if get_user_by_username(username):
        return jsonify({'error': 'User already exists'}), 400

    user_id = create_user(username, f"{username}@placeholder.com")
    gesture_id = create_gesture_password(user_id, gesture_name, hand_positions=hand_positions)

    return jsonify({
        'message': 'User registered successfully',
        'user_id': str(user_id),
        'gesture_password_id': str(gesture_id)
    })



# -------------------- LOGIN --------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    gesture_data = data.get('gesture_data')  # can be confidence score or hand positions

    if not username or not gesture_data:
        return jsonify({'error': 'Missing username or gesture data'}), 400

    user = get_user_by_username(username)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_id = str(user['_id'])
    success, confidence = verify_gesture(user_id, gesture_data)

    if success:
        return jsonify({'message': 'Login successful', 'confidence': confidence})
    else:
        return jsonify({'error': 'Gesture verification failed', 'confidence': confidence}), 401

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
    app.run(debug=True, port=5000)
