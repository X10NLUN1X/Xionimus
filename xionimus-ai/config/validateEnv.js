// config/validateEnv.js
const required = [
  'JWT_SECRET',
  'DATABASE_URL',
  'NODE_ENV'
];

const validateEnv = () => {
  const missing = [];
  
  required.forEach(key => {
    if (!process.env[key]) {
      missing.push(key);
    }
  });

  if (missing.length > 0) {
    console.error('Missing environment variables:', missing);
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }

  // Validate JWT_SECRET strength
  if (process.env.JWT_SECRET.length < 32) {
    console.warn('WARNING: JWT_SECRET should be at least 32 characters');
  }

  console.log('✓ Environment variables validated');
  console.log('  NODE_ENV:', process.env.NODE_ENV);
  console.log('  JWT_SECRET length:', process.env.JWT_SECRET.length);
  console.log('  DATABASE_URL:', process.env.DATABASE_URL?.substring(0, 20) + '...');
};

// Call at startup
validateEnv();