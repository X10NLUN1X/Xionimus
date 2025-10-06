// Debug authentication middleware
const debugAuth = async (req, res, next) => {
  console.log('\n=== AUTH DEBUG START ===');
  
  try {
    // 1. Check if token exists
    const authHeader = req.headers.authorization;
    console.log('1. Auth Header Present:', !!authHeader);
    
    if (!authHeader) {
      console.log('❌ No authorization header');
      return res.status(401).json({ 
        error: 'No authorization header',
        debug: 'Token missing from request'
      });
    }
    
    // 2. Extract token
    const token = authHeader.replace('Bearer ', '');
    console.log('2. Token extracted:', token.substring(0, 20) + '...');
    
    // 3. Verify token structure
    const parts = token.split('.');
    console.log('3. Token parts:', parts.length, '(should be 3)');
    
    if (parts.length !== 3) {
      return res.status(401).json({ 
        error: 'Invalid token format',
        debug: `Token has ${parts.length} parts, expected 3`
      });
    }
    
    // 4. Decode without verification first
    const decoded = jwt.decode(token);
    console.log('4. Decoded payload:', decoded);
    
    // 5. Check token expiration
    if (decoded.exp) {
      const isExpired = Date.now() >= decoded.exp * 1000;
      console.log('5. Token expired:', isExpired);
      console.log('   Current time:', new Date().toISOString());
      console.log('   Token expires:', new Date(decoded.exp * 1000).toISOString());
      
      if (isExpired) {
        return res.status(401).json({ 
          error: 'Token expired',
          debug: `Expired at ${new Date(decoded.exp * 1000).toISOString()}`
        });
      }
    }
    
    // 6. Verify token with secret
    let verified;
    try {
      verified = jwt.verify(token, process.env.JWT_SECRET);
      console.log('6. Token verified successfully');
    } catch (verifyError) {
      console.log('6. Token verification failed:', verifyError.message);
      return res.status(401).json({ 
        error: 'Token verification failed',
        debug: verifyError.message
      });
    }
    
    // 7. Check user exists in database
    const user = await User.findById(verified.userId || verified.id);
    console.log('7. User found in DB:', !!user);
    
    if (!user) {
      return res.status(401).json({ 
        error: 'User not found',
        debug: `No user with ID: ${verified.userId || verified.id}`
      });
    }
    
    // 8. Check user status
    console.log('8. User status:', {
      active: user.active,
      verified: user.verified,
      banned: user.banned
    });
    
    if (user.banned || !user.active) {
      return res.status(403).json({ 
        error: 'Account restricted',
        debug: `Account status - Active: ${user.active}, Banned: ${user.banned}`
      });
    }
    
    // 9. Attach user to request
    req.user = user;
    console.log('9. User attached to request');
    console.log('=== AUTH DEBUG SUCCESS ===\n');
    
    next();
    
  } catch (error) {
    console.error('=== AUTH DEBUG ERROR ===');
    console.error(error);
    res.status(500).json({ 
      error: 'Authentication error',
      debug: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
};