// config/auth.config.js
require('dotenv').config();

const authConfig = {
  jwt: {
    secret: process.env.JWT_SECRET,
    expiry: process.env.JWT_EXPIRY || '24h',
    algorithm: 'HS256'
  },
  bcrypt: {
    saltRounds: parseInt(process.env.BCRYPT_ROUNDS) || 10
  },
  session: {
    secret: process.env.SESSION_SECRET,
    name: 'sessionId',
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 24 * 60 * 60 * 1000 // 24 hours
    }
  }
};

// Validation
const validateConfig = () => {
  const errors = [];
  
  if (!authConfig.jwt.secret) {
    errors.push('JWT_SECRET is not defined');
  }
  
  if (authConfig.jwt.secret && authConfig.jwt.secret.length < 32) {
    errors.push('JWT_SECRET should be at least 32 characters');
  }
  
  if (!process.env.DATABASE_URL && !process.env.DB_HOST) {
    errors.push('Database configuration missing');
  }
  
  if (errors.length > 0) {
    console.error('=== Configuration Errors ===');
    errors.forEach(err => console.error(`- ${err}`));
    console.error('===========================');
    process.exit(1);
  }
  
  console.log('[CONFIG] Authentication configuration validated');
};

validateConfig();
module.exports = authConfig;