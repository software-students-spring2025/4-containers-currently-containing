![Lint-free](https://github.com/nyu-software-engineering/containerized-app-exercise/actions/workflows/lint.yml/badge.svg)
![ML Client - CI](https://github.com/software-students-spring2025/4-containers-currently-containing/actions/workflows/ml-client.yml/badge.svg)
![Web App - CI](https://github.com/software-students-spring2025/4-containers-currently-containing/actions/workflows/web-app.yml/badge.svg)

# Containerized App Exercise

## Database Setup

The system uses MongoDB as its primary database, running in a Docker container. The database stores user accounts, gesture passwords, protected documents, and authentication logs.

### Database Structure

The MongoDB database consists of the following collections:

1. **users** - Stores user account information
   - Contains basic user profile data
   - References to gesture passwords
   - List of documents owned by the user

2. **gesture_passwords** - Stores gesture authentication models
   - Links to the user who created the gesture
   - Contains paths to the trained model files
   - Stores configuration like confidence thresholds

3. **documents** - Stores protected documents
   - Contains the actual document content
   - Tracks document creation and modification dates
   - Logs access attempts

4. **authentication_logs** - Records authentication attempts
   - Tracks successful and failed authentication attempts
   - Stores confidence levels for gesture recognition
   - Records device information and timestamps

5. **gesture_training_sessions** - Tracks model training activities
   - Records when users train or update their gesture passwords
   - Stores training metadata such as sample counts

### Running the Database

To start the MongoDB container:

1. Make sure Docker Desktop is running
2. From the project root directory, run: docker compose up -d mongodb
3. The database will be available at `localhost:27017`

### Connecting to the Database

The database connection is handled by the `utils/database.py` module in the web app. This module provides functions for all database operations. 
The connection string is: mongodb://admin@localhost:27017/gesture_auth?authSource=admin

### Available Database Functions

The `utils/database.py` module provides the following functions:

#### User Management
- `create_user(username, email)` - Create a new user
- `get_user_by_id(user_id)` - Find a user by ID
- `get_user_by_username(username)` - Find a user by username

#### Gesture Password Management
- `create_gesture_password(user_id, gesture_name, model_path, confidence_threshold)` - Create a gesture password
- `get_user_gesture_password(user_id)` - Get a user's active gesture password

#### Document Management
- `create_document(user_id, title, content)` - Create a new document
- `get_user_documents(user_id)` - Get all documents for a user
- `get_document(doc_id, user_id)` - Get a document by ID
- `update_document(doc_id, content, user_id)` - Update a document's content

#### Authentication Logging
- `log_authentication(user_id, success, confidence, ip_address, user_agent, document_id)` - Log an authentication attempt

### Testing the Database Connection

A test script is provided at `web-app/test_db.py`. To run it:

1. Activate the virtual environment: source venv/bin/activate
2. Navigate to the web-app directory: cd web-app
3. Run the test script: python test_db.py


