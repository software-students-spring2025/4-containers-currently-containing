from flask import Flask
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import init_app, create_user, get_user_by_username, create_gesture_password, verify_gesture
import json

app = Flask(__name__)
mongo = init_app(app)

# Test data - based on your image
test_angles = {
    "Thumb MCP→IP": 161.44,
    "Thumb IP→Tip": 133.85,
    "Index MCP→PIP": 152.81,
    "Index PIP→DIP": 70.18,
    "Middle MCP→PIP": 148.49,
    "Middle PIP→DIP": 69.31,
    "Ring MCP→PIP": 168.76,
    "Ring PIP→DIP": 40.95,
    "Pinky MCP→PIP": 177.22,
    "Pinky PIP→DIP": 47.28
}

# Slightly different angles to test verification
test_angles_similar = {
    "Thumb MCP→IP": 165.23,
    "Thumb IP→Tip": 137.64,
    "Index MCP→PIP": 155.32,
    "Index PIP→DIP": 73.45,
    "Middle MCP→PIP": 150.11,
    "Middle PIP→DIP": 71.95,
    "Ring MCP→PIP": 170.32,
    "Ring PIP→DIP": 43.18,
    "Pinky MCP→PIP": 175.45,
    "Pinky PIP→DIP": 45.89
}

# Very different angles to test verification failure
test_angles_different = {
    "Thumb MCP→IP": 100.44,
    "Thumb IP→Tip": 83.85,
    "Index MCP→PIP": 102.81,
    "Index PIP→DIP": 130.18,
    "Middle MCP→PIP": 98.49,
    "Middle PIP→DIP": 129.31,
    "Ring MCP→PIP": 108.76,
    "Ring PIP→DIP": 110.95,
    "Pinky MCP→PIP": 117.22,
    "Pinky PIP→DIP": 127.28
}

# Run test in app context
with app.app_context():
    try:
        # Create a test user
        test_username = "angle_test_user"
        print(f"Creating test user: {test_username}")
        
        # Check if user already exists and delete if needed
        existing_user = get_user_by_username(test_username)
        if existing_user:
            print(f"User {test_username} already exists, will use existing account")
            user_id = existing_user['_id']
        else:
            user_id = create_user(test_username, f"{test_username}@example.com")
            print(f"Created user with ID: {user_id}")
        
        # Create gesture password
        print("Creating gesture password with test angles")
        gesture_id = create_gesture_password(user_id, "test_gesture", angle_data=test_angles)
        print(f"Created gesture password with ID: {gesture_id}")
        
        # Test verification with identical angles (should be 100% match)
        success, confidence = verify_gesture(user_id, test_angles)
        print(f"Verification with identical angles: {'SUCCESS' if success else 'FAILED'} (confidence: {confidence:.2f})")
        
        # Test verification with similar angles (should pass with high confidence)
        success, confidence = verify_gesture(user_id, test_angles_similar)
        print(f"Verification with similar angles: {'SUCCESS' if success else 'FAILED'} (confidence: {confidence:.2f})")
        
        # Test verification with different angles (should fail)
        success, confidence = verify_gesture(user_id, test_angles_different)
        print(f"Verification with different angles: {'SUCCESS' if success else 'FAILED'} (confidence: {confidence:.2f})")
        
        print("Database and verification tests completed!")
    except Exception as e:
        print(f"Test failed: {e}")