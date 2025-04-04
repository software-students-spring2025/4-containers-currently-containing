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

// Create a demo user for testing
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
    "confidence_threshold": 0.85
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

print("MongoDB initialized with collections and indexes for gesture authentication system");