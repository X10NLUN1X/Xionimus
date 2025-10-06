function enhancedJWTMiddleware(req, res, next) {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ 
      error: 'No token provided',
      hint: 'Ensure Authorization header is set'
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    console.log('Token Decoded:', {
      userId: decoded.userId,
      expiration: new Date(decoded.exp * 1000)
    });

    req.user = decoded;
    next();
  } catch (error) {
    console.error('JWT Verification Error:', {
      name: error.name,
      message: error.message
    });

    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ 
        error: 'Token expired',
        action: 'Please re-authenticate'
      });
    }

    res.status(403).json({ 
      error: 'Invalid token',
      details: error.message 
    });
  }
}