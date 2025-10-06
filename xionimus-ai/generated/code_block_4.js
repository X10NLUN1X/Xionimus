// Configuration validator
const validateAuthConfig = () => {
  const issues = [];
  
  // 1. JWT Secret
  if (!process.env.JWT_SECRET) {
    issues.push('❌ JWT_SECRET not set');
  } else if (process.env.JWT_SECRET.length < 32) {
    issues.push('⚠️ JWT_SECRET too short (< 32 chars)');
  } else {
    console.log('✅ JWT_SECRET configured');
  }
  
  // 2. Database connection
  if (!mongoose.connection.readyState) {
    issues.push('❌ Database not connected');
  } else {
    console.log('✅ Database connected');
  }
  
  // 3. Bcrypt rounds
  const saltRounds = parseInt(process.env.BCRYPT_ROUNDS || 10);
  if (saltRounds < 10) {
    issues.push('⚠️ Bcrypt rounds too low');
  } else {
    console.log('✅ Bcrypt rounds:', saltRounds);
  }
  
  // 4. CORS configuration
  const corsOrigin = process.env.CORS_ORIGIN || '*';
  console.log('✅ CORS origin:', corsOrigin);
  
  // 5. Node environment
  console.log('✅ Environment:', process.env.NODE_ENV);
  
  if (issues.length > 0) {
    console.error('\n=== CONFIGURATION ISSUES ===');
    issues.forEach(issue => console.error(issue));
    console.error('========================\n');
  }
  
  return issues.length === 0;
};

// Run validation on startup
validateAuthConfig();