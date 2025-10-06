# Create a test script: test-auth.js
node -e "
const debugAuth = require('./debug-auth');
debugAuth.runAllTests('your-test-email@example.com', 'your-test-password')
  .then(results => {
    console.log('Tests completed');
    process.exit(results.password.success ? 0 : 1);
  })
  .catch(err => {
    console.error('Test failed:', err);
    process.exit(1);
  });
"