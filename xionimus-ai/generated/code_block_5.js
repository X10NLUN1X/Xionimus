// Replace your auth middleware temporarily with this debug version
const debugAuthMiddleware = async (req, res, next) => {
  console.log('\n=== AUTH MIDDLEWARE DEBUG ===');
  
  try {
    // Step 1: Check if token exists
    const authHeader = req.headers.authorization;
    console.log('1. Auth header present?', !!authHeader);
    
    if (!authHeader) {
      return res.status(401).json({ 
        error: 'No authorization header',
        headers: req.headers 
      });
    }
    
    // Step 2: Extract token
    const token = authHeader.replace('Bearer ', '');
    console.log('2. Token extracted?', !!token);
    console.log('   Token length:', token.length);
    console.log('   Token preview:', token.substring(0, 20) + '...');
    
    // Step 3: Verify token
    const jwt = require('jsonwebtoken');
    let decoded;
    try {
      decoded = jwt.verify(token, process.env.JWT_SECRET);
      console.log('3. Token verified successfully:', decoded);
    } catch (jwtError) {
      console.error('3. JWT verification failed:', jwtError.message);
      return res.status(401).json({ 
        error: 'Invalid token',
        details: jwtError.message 
      });
    }
    
    // Step 4: Fetch user from database
    console.log('4. Looking up user ID:', decoded.userId || decoded.id);
    
    const user = await db.query(
      'SELECT * FROM users WHERE id = $1',
      [decoded.userId || decoded.id]
    );
    
    console.log('5. User found?', user.rows.length > 0);
    
    if (user.rows.length === 0) {
      return res.status(401).json({ 
        error: 'User not found',
        userId: decoded.userId || decoded.id 
      });
    }
    
    // Step 5: Attach user to request
    req.user = user.rows[0];
    console.log('6. User attached to request:', req.user.email);
    console.log('=========================\n');
    
    next();
  } catch (error) {
    console.error('Unexpected error in auth middleware:', error);
    res.status(500).json({ 
      error: 'Authentication error',
      details: error.message,
      stack: error.stack 
    });
  }
};