// auth.middleware.js - Enhanced JWT verification
const jwt = require('jsonwebtoken');

const authenticateToken = async (req, res, next) => {
  console.log('=== JWT AUTHENTICATION ===');
  
  try {
    // Check for token in different locations
    const authHeader = req.headers['authorization'];
    const tokenFromHeader = authHeader && authHeader.split(' ')[1];
    const tokenFromCookie = req.cookies?.token;
    const tokenFromBody = req.body?.token;
    
    console.log('Token sources:', {
      header: !!tokenFromHeader,
      cookie: !!tokenFromCookie,
      body: !!tokenFromBody
    });
    
    const token = tokenFromHeader || tokenFromCookie || tokenFromBody;
    
    if (!token) {
      console.log('❌ No token provided');
      return res.status(401).json({ error: 'Access token required' });
    }
    
    console.log('Token found:', token.substring(0, 50) + '...');
    console.log('JWT_SECRET exists:', !!process.env.JWT_SECRET);
    
    // Verify token
    jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
      if (err) {
        console.error('❌ Token verification failed:', err.message);
        console.error('Error name:', err.name);
        
        if (err.name === 'TokenExpiredError') {
          return res.status(401).json({ error: 'Token expired' });
        }
        if (err.name === 'JsonWebTokenError') {
          return res.status(401).json({ error: 'Invalid token' });
        }
        
        return res.status(401).json({ error: 'Token verification failed' });
      }
      
      console.log('✅ Token verified:', decoded);
      req.user = decoded;
      next();
    });
    
  } catch (error) {
    console.error('❌ Authentication middleware error:', error);
    res.status(500).json({ error: 'Authentication error' });
  }
};