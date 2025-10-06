// Test database connection explicitly
async function testDatabaseConnection() {
  try {
    // For PostgreSQL
    const result = await db.query('SELECT NOW()');
    console.log('✅ Database connected:', result.rows[0]);
    
    // Test user table specifically
    const userTest = await db.query('SELECT COUNT(*) FROM users');
    console.log('✅ Users table accessible:', userTest.rows[0].count, 'users');
    
    // Test a specific user lookup
    const testUser = await db.query('SELECT id, email FROM users LIMIT 1');
    console.log('✅ Can query users:', testUser.rows[0]);
    
  } catch (error) {
    console.error('❌ Database test failed:', error);
  }
}