// Common fixes implementation
const authFixes = {
  // Fix 1: Ensure proper middleware order
  setupMiddleware: (app) => {
    app.use(express.json());
    app.use(express.urlencoded({ extended: true }));
    app.use(cors({
      origin: process.env.CORS_ORIGIN || '*',
      credentials: true
    }));
  },
  
  // Fix 2: Handle async errors properly
  asyncHandler: (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  },
  
  // Fix 3: Proper token extraction
  extractToken: (authHeader) => {
    if (!authHeader) return null;
    
    const parts = authHeader.split(' ');
    if (parts.length === 2 && parts[0] === 'Bearer') {
      return parts[1];
    }
    
    // Try without Bearer prefix
    return authHeader;
  },
  
  // Fix 4: Safe user object serialization
  sanitizeUser: (user) => {
    const userObj = user.toObject ? user.toObject() : user;
    delete userObj.password;
    delete userObj.__v;
    return userObj;
  }
};