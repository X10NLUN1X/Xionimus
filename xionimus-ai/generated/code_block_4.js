// Verify all required env vars are present
function checkEnvironmentVariables() {
  const required = [
    'JWT_SECRET',
    'DATABASE_URL',
    'NODE_ENV',
    'BCRYPT_ROUNDS'
  ];
  
  const missing = [];
  required.forEach(varName => {
    if (!process.env[varName]) {
      missing.push(varName);
    } else {
      console.log(`✅ ${varName}: ${varName.includes('SECRET') ? '[HIDDEN]' : process.env[varName]}`);
    }
  });
  
  if (missing.length > 0) {
    console.error('❌ Missing environment variables:', missing);
  }
  
  // Check for common issues
  if (process.env.JWT_SECRET && process.env.JWT_SECRET.length < 32) {
    console.warn('⚠️ JWT_SECRET seems too short');
  }
}