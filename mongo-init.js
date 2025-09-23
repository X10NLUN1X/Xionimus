// Initialize the Xionimus AI database with required collections
db = db.getSiblingDB('xionimus_ai');

// Create collections with initial structure
db.createCollection('projects');
db.createCollection('chat_sessions');
db.createCollection('uploaded_files');
db.createCollection('api_keys');
db.createCollection('agents');
db.createCollection('code_files');

// Create indexes for better performance
db.projects.createIndex({ "created_at": -1 });
db.chat_sessions.createIndex({ "project_id": 1 });
db.uploaded_files.createIndex({ "project_id": 1 });
db.api_keys.createIndex({ "service": 1 });
db.code_files.createIndex({ "project_id": 1 });

print('Xionimus AI database initialized successfully');