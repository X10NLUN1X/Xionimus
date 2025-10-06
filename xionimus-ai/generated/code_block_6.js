// test-auth.js - Manual testing script
const axios = require('axios');

const API_URL = 'http://localhost:3000';

const testAuth = async () => {
  try {
    console.log('1. Testing login...');
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      email: 'test@example.com',
      password: 'testpassword'
    });
    
    console.log('Login successful:', loginResponse.data);
    const token = loginResponse.data.token;

    console.log('\n2. Testing protected route...');
    const protectedResponse = await axios.get(`${API_URL}/api/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    console.log('Protected route accessed:', protectedResponse.data);

  } catch (error) {
    console.error('Test failed:', {
      endpoint: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
  }
};

testAuth();