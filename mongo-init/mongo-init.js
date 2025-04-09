// mongo-init.js
db = db.getSiblingDB('gesture_auth');

// Create admin user for the gesture_auth database
db.createUser({
  user: "admin",
  pwd: "secretpassword",
  roles: [{ role: "readWrite", db: "gesture_auth" }]
});

// Create collections
db.createCollection('users');
db.createCollection('gesture_passwords');
db.createCollection('documents');
db.createCollection('authentication_logs');
db.createCollection('gesture_training_sessions');

// Create indexes for better query performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.gesture_passwords.createIndex({ "user_id": 1 });
db.documents.createIndex({ "user_id": 1 });
db.documents.createIndex({ "updated_at": 1 });
db.authentication_logs.createIndex({ "user_id": 1, "timestamp": 1 });
db.authentication_logs.createIndex({ "success": 1 });
db.gesture_training_sessions.createIndex({ "user_id": 1 });

// Create a demo user with model-based authentication
const demoUserId = ObjectId();
const demoGestureId = ObjectId();
const demoDocId = ObjectId();

db.users.insertOne({
  "_id": demoUserId,
  "username": "demo_user",
  "email": "demo@example.com",
  "created_at": new Date(),
  "last_login": new Date(),
  "gesture_password_id": demoGestureId,
  "documents": [
    {
      "document_id": demoDocId,
      "title": "Demo Document",
      "last_accessed": new Date()
    }
  ]
});

db.gesture_passwords.insertOne({
  "_id": demoGestureId,
  "user_id": demoUserId,
  "gesture_data": {
    "model_type": "teachable_machine",
    "gesture_name": "demo_auth_gesture",
    "gesture_model_path": "/models/demo/auth_gesture",
    "created_at": new Date(),
    "updated_at": new Date(),
    "confidence_threshold": 0.85,
    "storage_type": "model"
  },
  "active": true
});

db.documents.insertOne({
  "_id": demoDocId,
  "user_id": demoUserId,
  "title": "Demo Document",
  "content": "<h1>Welcome to Gesture Auth</h1><p>This is a demo document protected by gesture authentication.</p>",
  "created_at": new Date(),
  "updated_at": new Date(),
  "access_logs": []
});

// Add a demo user with ANGLE-based authentication (new format!)
const angleUserIdDemo = ObjectId();
const angleGestureIdDemo = ObjectId();
const angleDocIdDemo = ObjectId();

db.users.insertOne({
  "_id": angleUserIdDemo,
  "username": "angles_user",
  "email": "angles@example.com",
  "created_at": new Date(),
  "last_login": new Date(),
  "gesture_password_id": angleGestureIdDemo,
  "documents": [
    {
      "document_id": angleDocIdDemo,
      "title": "Hand Angles Demo Document",
      "last_accessed": new Date()
    }
  ]
});

db.gesture_passwords.insertOne({
  "_id": angleGestureIdDemo,
  "user_id": angleUserIdDemo,
  "gesture_data": {
    "storage_type": "angles",
    "gesture_name": "peace_sign",
    "angle_data": {
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
    },
    "created_at": new Date(),
    "updated_at": new Date(),
    "confidence_threshold": 0.85
  },
  "active": true
});

db.documents.insertOne({
  "_id": angleDocIdDemo,
  "user_id": angleUserIdDemo,
  "title": "Hand Angles Demo Document",
  "content": "<h1>Hand Angle Authentication</h1><p>This document demonstrates authentication using hand angle data instead of positions.</p>",
  "created_at": new Date(),
  "updated_at": new Date(),
  "access_logs": []
});

print("MongoDB initialized with collections and indexes for gesture authentication system");