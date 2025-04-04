from flask import Flask
from utils.database import init_app, create_user, get_user_by_username

app = Flask(__name__)
mongo = init_app(app)

# Test creating a user
with app.app_context():
    try:
        # Create a test user
        user_id = create_user('test_user', 'test@example.com')
        print(f"Created user with ID: {user_id}")
        
        # Retrieve the user
        user = get_user_by_username('test_user')
        if user:
            print(f"Found user: {user['username']} ({user['email']})")
        else:
            print("User not found")
            
        print("Database connection test successful!")
    except Exception as e:
        print(f"Database test failed: {e}")