// config/auth-check.js
const checkConfiguration = () => {
  const issues = [];
  
  // Check JWT Secret
  if (!process.env.JWT_SECRET) {
    issues.push('JWT_SECRET is not set');
  } else if (process.env.JWT_SECRET.length < 32) {
    issues.push('JWT_SECRET should be at least 32 characters');
  }
  
  // Check Database URL
  if (!process.env.DATABASE_URL && !process.env.MONGODB_URI) {
    issues.push('Database connection string not found');
  }
  
  // Check Node Environment
  if (!process.env.NODE_ENV) {
    issues.push('NODE_ENV is not set');
  }
  
  // Check CORS settings
  if (!process.env.CLIENT_URL && process.env.NODE_ENV === 'production') {
    issues.push('CLIENT_URL not set for CORS');
  }
  
  if (issues.length > 0) {
    console.error('=== CONFIGURATION ISSUES ===');
    issues.forEach(issue => console.error('❌', issue));
    return false;
  }
  
  console.log('✅ Configuration check passed');
  return true;
};

// Run check on startup
checkConfiguration();