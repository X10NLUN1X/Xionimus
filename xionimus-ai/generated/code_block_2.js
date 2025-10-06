// Database connection test utility
async function testDatabaseConnection() {
  try {
    // For PostgreSQL
    const result = await db.query('SELECT NOW()');
    console.log('✅ Database connected:', result.rows[0]);
    
    // Test user table access
    const userTest = await db.query('SELECT COUNT(*) FROM users');
    console.log('✅ User table accessible:', userTest.rows[0].count, 'users');
    
    return true;
  } catch (error) {
    console.error('❌ Database connection failed:', error);
    return false;
  }
}

// For MongoDB
async function testMongoConnection() {
  try {
    await mongoose.connection.db.admin().ping();
    console.log('✅ MongoDB connected');
    
    const userCount = await User.countDocuments();
    console.log('✅ User collection accessible:', userCount, 'users');
    
    return true;
  } catch (error) {
    console.error('❌ MongoDB connection failed:', error);
    return false;
  }
}