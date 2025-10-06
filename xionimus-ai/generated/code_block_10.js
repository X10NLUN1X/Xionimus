// Run this to test the entire auth flow
async function testAuthFlow() {
  console.log('Starting complete auth flow test...\n');
  
  // 1. Test database
  await testDatabaseConnection();
  
  // 2. Check environment
  checkEnvironmentVariables();
  
  // 3. Test JWT
  testJWTValidation();
  
  // 4. Try a complete login flow
  const testCredentials = {
    email: 'test@example.com',  // Use a known good user
    password: 'testpassword'
  };
  
  try {
    // Simulate login
    const loginResponse = await fetch('http://localhost:3000/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testCredentials)
    });
    
    const loginData = await loginResponse.json();
    console.log('Login response:', loginResponse.status, loginData);
    
    if (loginData.token) {
      // Test protected route
      const protectedResponse = await fetch('http://localhost:3000/api/profile', {
        headers: {
          'Authorization': `Bearer ${loginData.token}`
        }
      });
      
      const protectedData = await protectedResponse.json();
      console.log('Protected route response:', protectedResponse.status, protectedData);
    }
  } catch (error) {
    console.error('Flow test failed:', error);
  }
}

// Run the test
testAuthFlow();