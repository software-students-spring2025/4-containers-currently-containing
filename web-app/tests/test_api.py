import requests
import json

# Base URL for the API
BASE_URL = "http://127.0.0.1:5001"

# Test angles from the image
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

# Slightly different angles for testing
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

def test_register():
    """Test user registration with angle data"""
    print("\n=== Testing Registration ===")
    
    payload = {
        "username": "api_test_user",
        "gesture_name": "peace_sign",
        "angle_data": test_angles
    }
    
    response = requests.post(f"{BASE_URL}/register", json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.json().get("user_id") if response.status_code == 200 else None

def test_login_success():
    """Test login with matching angles"""
    print("\n=== Testing Login (Success) ===")
    
    payload = {
        "username": "api_test_user",
        "angle_data": test_angles
    }
    
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_login_similar():
    """Test login with similar angles (should pass)"""
    print("\n=== Testing Login (Similar Angles) ===")
    
    payload = {
        "username": "api_test_user",
        "angle_data": test_angles_similar
    }
    
    response = requests.post(f"{BASE_URL}/login", json=payload)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

def test_get_documents():
    """Test fetching documents for a user"""
    print("\n=== Testing Document Access ===")
    
    response = requests.get(f"{BASE_URL}/documents?username=api_test_user")
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    return response.status_code == 200

if __name__ == "__main__":
    # Run the test sequence
    try:
        print("🧪 Starting API tests...")
        
        # First try to register (might fail if user already exists)
        #user_id = test_register()
        
        # Test login with exact angles
        login_success = test_login_success()
        
        # Test login with similar angles
        login_similar = test_login_similar()
        
        # Test document access
        docs_success = test_get_documents()
        
        print("\n=== Test Summary ===")
        #print(f"Registration: {'✅ SUCCESS' if user_id else '⚠️ FAILED/EXISTS'}")
        print(f"Login (exact): {'✅ SUCCESS' if login_success else '❌ FAILED'}")
        print(f"Login (similar): {'✅ SUCCESS' if login_similar else '❌ FAILED'}")
        print(f"Document access: {'✅ SUCCESS' if docs_success else '❌ FAILED'}")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")