from flask import Flask
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import init_app, create_user, get_user_by_username

app = Flask(__name__)
mongo = init_app(app)

# Test creating a user
with app.app_context():
    try:
        # Check if the test user already exists
        existing_user = get_user_by_username('test_user')
        
        if existing_user:
            print(f"Test user already exists with ID: {existing_user['_id']}")
            user_id = existing_user['_id']
        else:
            # Create the test user only if it doesn't exist
            user_id = create_user('test_user', 'test@example.com')
            print(f"Created new test user with ID: {user_id}")
        
        # Retrieve the user
        user = get_user_by_username('test_user')
        if user:
            print(f"Found user: {user['username']} ({user['email']})")
        else:
            print("User not found")
            
        print("Database connection test successful!")
    except Exception as e:
        print(f"Database test failed: {e}")