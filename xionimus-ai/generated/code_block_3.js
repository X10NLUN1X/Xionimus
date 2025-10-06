// auth.controller.js - Enhanced with debugging
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

class AuthController {
  async login(req, res, next) {
    console.log('=== LOGIN ATTEMPT ===');
    console.log('Request body:', JSON.stringify(req.body, null, 2));
    
    try {
      // Step 1: Validate input
      const { email, password } = req.body;
      
      if (!email || !password) {
        console.log('❌ Missing credentials');
        return res.status(400).json({ 
          error: 'Email and password are required',
          received: { email: !!email, password: !!password }
        });
      }
      
      console.log('✅ Input validation passed');
      
      // Step 2: Find user
      console.log('Searching for user:', email);
      const user = await User.findOne({ email: email.toLowerCase() });
      
      if (!user) {
        console.log('❌ User not found:', email);
        return res.status(401).json({ error: 'Invalid credentials' });
      }
      
      console.log('✅ User found:', { 
        id: user._id || user.id, 
        email: user.email,
        hasPassword: !!user.password 
      });
      
      // Step 3: Verify password
      console.log('Verifying password...');
      console.log('Password from request:', password);
      console.log('Hashed password from DB:', user.password?.substring(0, 20) + '...');
      
      const isPasswordValid = await bcrypt.compare(password, user.password);
      console.log('Password validation result:', isPasswordValid);
      
      if (!isPasswordValid) {
        console.log('❌ Invalid password');
        return res.status(401).json({ error: 'Invalid credentials' });
      }
      
      console.log('✅ Password verified');
      
      // Step 4: Generate JWT
      console.log('Generating JWT token...');
      
      const tokenPayload = {
        userId: user._id || user.id,
        email: user.email,
        role: user.role || 'user'
      };
      
      console.log('Token payload:', tokenPayload);
      console.log('JWT_SECRET exists:', !!process.env.JWT_SECRET);
      console.log('JWT_SECRET length:', process.env.JWT_SECRET?.length);
      
      const token = jwt.sign(
        tokenPayload,
        process.env.JWT_SECRET,
        { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
      );
      
      console.log('✅ Token generated:', token.substring(0, 50) + '...');
      
      // Step 5: Send response
      const response = {
        success: true,
        token,
        user: {
          id: user._id || user.id,
          email: user.email,
          name: user.name,
          role: user.role
        }
      };
      
      console.log('✅ Login successful, sending response');
      res.status(200).json(response);
      
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('Error name:', error.name);
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
      next(error);
    }
  }
}