// Test suite for auth system
const testAuthSystem = async () => {
  console.log('\n=== RUNNING AUTH SYSTEM TESTS ===\n');
  
  // Test 1: Database Connection
  try {
    const testUser = await User.findOne();
    console.log('✅ Database query successful');
  } catch (error) {
    console.error('❌ Database query failed:', error.message);
  }
  
  // Test 2: JWT Creation and Verification
  try {
    const testToken = jwt.sign(
      { test: true, exp: Math.floor(Date.now() / 1000) + 60 },
      process.env.JWT_SECRET
    );
    const decoded = jwt.verify(testToken, process.env.JWT_SECRET);
    console.log('✅ JWT creation/verification working');
  } catch (error) {
    console.error('❌ JWT test failed:', error.message);
  }
  
  // Test 3: Bcrypt
  try {
    const hash = await bcrypt.hash('testpassword', 10);
    const match = await bcrypt.compare('testpassword', hash);
    if (match) {
      console.log('✅ Bcrypt working correctly');
    } else {
      console.error('❌ Bcrypt comparison failed');
    }
  } catch (error) {
    console.error('❌ Bcrypt test failed:', error.message);
  }
  
  // Test 4: Check for common middleware issues
  console.log('\nMiddleware Order Check:');
  console.log('- body-parser/express.json() before routes?');
  console.log('- CORS middleware configured?');
  console.log('- Error handler at the end?');
  
  console.log('\n=== TESTS COMPLETE ===\n');
};

// Run tests
testAuthSystem();