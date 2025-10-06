// Fixed authentication middleware with debugging
const authMiddleware = async (req, res, next) => {
  console.log('Auth Middleware: Starting');
  
  try {
    // 1. Check token presence (multiple sources)
    let token = null;
    
    // Check Authorization header
    if (req.headers.authorization?.startsWith('Bearer ')) {
      token = req.headers.authorization.substring(7);
      console.log('Token from Authorization header');
    }
    // Check cookies
    else if (req.cookies?.token) {
      token = req.cookies.token;
      console.log('Token from cookies');
    }
    // Check custom header
    else if (req.headers['x-auth-token']) {
      token = req.headers['x-auth-token'];
      console.log('Token from x-auth-token header');
    }
    
    if (!token) {
      console.log('No token found');
      return res.status(401).json({ error: 'No authentication token provided' });
    }
    
    console.log('Token found:', token.substring(0, 20) + '...');
    
    // 2. Verify token
    const jwt = require('jsonwebtoken');
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    console.log('Token decoded successfully:', decoded);
    
    // 3. Check if user still exists
    const User = require('./models/User');
    const user = await User.findById(decoded.userId || decoded.id || decoded._id)
      .select('-password'); // Don't include password
    
    if (!user) {
      console.log('User from token not found in database');
      return res.status(401).json({ error: 'User no longer exists' });
    }
    
    // 4. Check if user is active (if you have this field)
    if (user.isActive === false || user.deleted) {
      console.log('User account is inactive or deleted');
      return res.status(401).json({ error: 'Account is inactive' });
    }
    
    // 5. Attach user to request
    req.user = user;
    req.userId = user._id;
    req.token = token;
    
    console.log('Auth Middleware: Success - User authenticated:', user.email);
    next();
    
  } catch (error) {
    console.error('Auth Middleware Error:', error);
    
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Invalid token' });
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    
    return res.status(500).json({ error: 'Authentication error', details: error.message });
  }
};