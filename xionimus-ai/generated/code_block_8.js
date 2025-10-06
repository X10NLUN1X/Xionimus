// Test different token formats
function testTokenFormats(token) {
  const tests = [
    { name: 'Raw token', value: token },
    { name: 'With Bearer', value: `Bearer ${token}` },
    { name: 'Trimmed', value: token.trim() },
    { name: 'No Bearer prefix', value: token.replace('Bearer ', '') }
  ];
  
  const jwt = require('jsonwebtoken');
  tests.forEach(test => {
    try {
      const decoded = jwt.verify(test.value, process.env.JWT_SECRET);
      console.log(`✅ ${test.name} works:`, decoded);
    } catch (error) {
      console.log(`❌ ${test.name} fails:`, error.message);
    }
  });
}