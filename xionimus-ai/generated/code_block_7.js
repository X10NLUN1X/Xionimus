// test-auth.js - Run this to test each component
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
require('dotenv').config();

async function testAuth() {
  console.log('=== Authentication System Test ===\n');

  // 1. Test environment variables
  console.log('1. Environment Variables:');
  console.log('   JWT_SECRET exists:', !!process.env.JWT_SECRET);
  console.log('   DATABASE_URL exists:', !!process.env.DATABASE_URL);
  
  // 2. Test password hashing
  console.log('\n2. Password Hashing:');
  const testPassword = 'TestPassword123';
  const hash = await bcrypt.hash(testPassword, 10);
  console.log('   Hash generated:', hash.substring(0, 20) + '...');
  const isMatch = await bcrypt.compare(testPassword, hash);
  console.log('   Password verification:', isMatch ? '✓ PASS' : '✗ FAIL');

  // 3. Test JWT
  console.log('\n3. JWT Generation and Verification:');
  try {
    const payload = { userId: 'test123', email: 'test@example.com' };
    const token = jwt.sign(payload, process.env.JWT_SECRET || 'test-secret', { expiresIn: '1h' });
    console.log('   Token generated:', token.substring(0, 20) + '...');
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'test-secret');
    console.log('   Token verification:', '✓ PASS');
    console.log('   Decoded payload:', decoded);
  } catch (error) {
    console.log('   Token verification:', '✗ FAIL');
    console.log('   Error:', error.message);
  }

  // 4. Test database connection
  console.log('\n4. Database Connection:');
  try {
    const mongoose = require('mongoose');
    await mongoose.connect(process.env.DATABASE_URL);
    console.log('   Connection:', '✓ PASS');
    
    // Test user query
    const User = require('./models/User');
    const userCount = await User.countDocuments();
    console.log('   User count:', userCount);
    
    await mongoose.disconnect();
  } catch (error) {
    console.log('   Connection:', '✗ FAIL');
    console.log('   Error:', error.message);
  }
}

testAuth().catch(console.error);