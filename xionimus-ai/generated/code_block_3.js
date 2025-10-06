// Isolated JWT validation test
function testJWTValidation() {
  const jwt = require('jsonwebtoken');
  
  // Create a test token
  const testPayload = { userId: 1, email: 'test@example.com' };
  const testToken = jwt.sign(testPayload, process.env.JWT_SECRET, {
    expiresIn: '1h'
  });
  
  console.log('Test token created:', testToken);
  
  // Try to verify it
  try {
    const decoded = jwt.verify(testToken, process.env.JWT_SECRET);
    console.log('✅ JWT verification works:', decoded);
  } catch (error) {
    console.error('❌ JWT verification failed:', error);
  }
}