// test-auth.js
const axios = require('axios');
const colors = require('colors');

const BASE_URL = 'http://localhost:3000';

async function testAuth() {
  console.log('\n=== Starting Authentication Test ===\n'.cyan);
  
  // Test 1: Server Health
  try {
    const health = await axios.get(`${BASE_URL}/health`);
    console.log('✓ Server is running'.green);
  } catch (error) {
    console.log('✗ Server is not responding'.red);
    return;
  }
  
  // Test 2: Database Connection
  try {
    const db = await axios.get(`${BASE_URL}/api/health/db`);
    console.log('✓ Database connected'.green);
  } catch (error) {
    console.log('✗ Database connection failed'.red, error.response?.data);
  }
  
  // Test 3: Login
  let token;
  try {
    const loginResponse = await axios.post(`${BASE_URL}/api/auth/login`, {
      email: 'test@example.com',
      password: 'password123'
    });
    token = loginResponse.data.token;
    console.log('✓ Login successful'.green);
    console.log('  Token:', token.substring(0, 20) + '...');
  } catch (error) {
    console.log('✗ Login failed'.red);
    console.log('  Status:', error.response?.status);
    console.log('  Error:', error.response?.data);
    return;
  }
  
  // Test 4: Authenticated Request
  try {
    const protectedResponse = await axios.get(`${BASE_URL}/api/user/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('✓ Authenticated request successful'.green);
    console.log('  User:', protectedResponse.data);
  } catch (error) {
    console.log('✗ Authenticated request failed'.red);
    console.log('  Status:', error.response?.status);
    console.log('  Error:', error.response?.data);
  }
  
  console.log('\n=== Test Complete ===\n'.cyan);
}

testAuth();