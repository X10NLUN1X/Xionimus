// Test file: debug-auth.js
const debugAuth = {
  // 1. Test Database Connection
  async testDatabaseConnection() {
    console.log('Testing database connection...');
    try {
      // For MongoDB
      const mongoose = require('mongoose');
      const state = mongoose.connection.readyState;
      console.log('MongoDB State:', ['disconnected', 'connected', 'connecting', 'disconnecting'][state]);
      
      // Test query
      const User = require('./models/User');
      const count = await User.countDocuments();
      console.log('User count:', count);
      
      return { success: true, userCount: count };
    } catch (error) {
      console.error('DB Test Failed:', error);
      return { success: false, error: error.message };
    }
  },

  // 2. Test JWT Token Generation and Validation
  async testJWT() {
    console.log('Testing JWT...');
    const jwt = require('jsonwebtoken');
    
    try {
      // Generate test token
      const payload = { userId: 'test123', email: 'test@example.com' };
      const token = jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' });
      console.log('Generated token:', token.substring(0, 50) + '...');
      
      // Verify token
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      console.log('Decoded payload:', decoded);
      
      return { success: true, token, decoded };
    } catch (error) {
      console.error('JWT Test Failed:', error);
      return { success: false, error: error.message };
    }
  },

  // 3. Test User Lookup
  async testUserLookup(email) {
    console.log('Testing user lookup for:', email);
    try {
      const User = require('./models/User');
      const user = await User.findOne({ email }).select('+password');
      
      if (!user) {
        console.log('User not found');
        return { success: false, error: 'User not found' };
      }
      
      console.log('User found:', {
        id: user._id,
        email: user.email,
        hasPassword: !!user.password,
        passwordLength: user.password?.length
      });
      
      return { success: true, user };
    } catch (error) {
      console.error('User Lookup Failed:', error);
      return { success: false, error: error.message };
    }
  },

  // 4. Test Password Validation
  async testPasswordValidation(email, password) {
    console.log('Testing password validation...');
    try {
      const bcrypt = require('bcryptjs');
      const User = require('./models/User');
      
      const user = await User.findOne({ email }).select('+password');
      if (!user) {
        return { success: false, error: 'User not found' };
      }
      
      // Direct bcrypt test
      const isValid = await bcrypt.compare(password, user.password);
      console.log('Password valid:', isValid);
      
      // Also test the user method if it exists
      if (user.comparePassword) {
        const methodValid = await user.comparePassword(password);
        console.log('Method validation:', methodValid);
      }
      
      return { success: isValid };
    } catch (error) {
      console.error('Password Test Failed:', error);
      return { success: false, error: error.message };
    }
  },

  // Run all tests
  async runAllTests(email = 'test@example.com', password = 'testpassword') {
    console.log('=== RUNNING AUTHENTICATION DIAGNOSTICS ===\n');
    
    const results = {
      database: await this.testDatabaseConnection(),
      jwt: await this.testJWT(),
      userLookup: await this.testUserLookup(email),
      password: await this.testPasswordValidation(email, password)
    };
    
    console.log('\n=== RESULTS SUMMARY ===');
    console.log(JSON.stringify(results, null, 2));
    
    return results;
  }
};

module.exports = debugAuth;