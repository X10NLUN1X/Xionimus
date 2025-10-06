// auth.controller.js
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { validationResult } = require('express-validator');

class AuthController {
  async login(req, res, next) {
    try {
      // 1. Validation check
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        console.log('Validation errors:', errors.array());
        return res.status(400).json({ 
          error: 'Validation failed', 
          details: errors.array() 
        });
      }

      const { email, password } = req.body;
      console.log(`Login attempt for email: ${email}`);

      // 2. Database query with error handling
      let user;
      try {
        // Check your database connection
        user = await db.query(
          'SELECT id, email, password, status FROM users WHERE email = ?',
          [email]
        );
        
        if (!user || user.length === 0) {
          console.log(`User not found: ${email}`);
          return res.status(401).json({ 
            error: 'Invalid credentials' 
          });
        }
        
        user = user[0]; // If using mysql2
      } catch (dbError) {
        console.error('Database error:', dbError);
        throw new Error(`Database query failed: ${dbError.message}`);
      }

      // 3. Check user status
      if (user.status !== 'active') {
        console.log(`User account not active: ${email}`);
        return res.status(403).json({ 
          error: 'Account is not active' 
        });
      }

      // 4. Password verification with detailed logging
      let isPasswordValid;
      try {
        isPasswordValid = await bcrypt.compare(password, user.password);
        console.log('Password validation result:', isPasswordValid);
      } catch (bcryptError) {
        console.error('Bcrypt error:', bcryptError);
        throw new Error(`Password verification failed: ${bcryptError.message}`);
      }

      if (!isPasswordValid) {
        console.log(`Invalid password for user: ${email}`);
        return res.status(401).json({ 
          error: 'Invalid credentials' 
        });
      }

      // 5. JWT generation with error handling
      let token;
      try {
        const payload = {
          userId: user.id,
          email: user.email
        };
        
        token = jwt.sign(
          payload,
          process.env.JWT_SECRET,
          { 
            expiresIn: process.env.JWT_EXPIRES_IN || '24h',
            issuer: process.env.JWT_ISSUER || 'your-app',
            audience: process.env.JWT_AUDIENCE || 'your-app-users'
          }
        );
        
        console.log('JWT generated successfully');
      } catch (jwtError) {
        console.error('JWT generation error:', jwtError);
        throw new Error(`Token generation failed: ${jwtError.message}`);
      }

      // 6. Send response
      res.status(200).json({
        success: true,
        token,
        user: {
          id: user.id,
          email: user.email
        }
      });

    } catch (error) {
      console.error('Login error:', error);
      next(error);
    }
  }
}