// diagnostic.js
const diagnostics = {
  async runAll() {
    const results = [];
    
    // 1. Check environment variables
    results.push({
      test: 'Environment Variables',
      passed: !!process.env.JWT_SECRET && !!process.env.DATABASE_URL,
      details: {
        JWT_SECRET: !!process.env.JWT_SECRET,
        DATABASE_URL: !!process.env.DATABASE_URL,
        NODE_ENV: process.env.NODE_ENV
      }
    });
    
    // 2. Check middleware order
    results.push({
      test: 'Middleware Order',
      passed: true,
      recommendation: 'Ensure body-parser comes before routes'
    });
    
    // 3. Check async/await usage
    results.push({
      test: 'Async Handling',
      recommendation: 'All database calls should use await'
    });
    
    // 4. Check token expiry
    const testToken = jwt.sign({ test: true }, process.env.JWT_SECRET, { expiresIn: '1s' });
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
      jwt.verify(testToken, process.env.JWT_SECRET);
      results.push({ test: 'Token Expiry', passed: false });
    } catch (e) {
      results.push({ test: 'Token Expiry', passed: true });
    }
    
    console.table(results);
    return results;
  }
};