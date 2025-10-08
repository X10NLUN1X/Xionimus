// utils/db-health-check.js
const checkDatabaseHealth = async () => {
  try {
    // For Sequelize
    await sequelize.authenticate();
    console.log('[DB] Connection established successfully');
    
    // Test query
    const result = await sequelize.query('SELECT 1+1 AS result');
    console.log('[DB] Test query successful:', result[0][0]);
    
    // Check user table
    const userCount = await User.count();
    console.log('[DB] User count:', userCount);
    
    return true;
  } catch (error) {
    console.error('[DB] Health check failed:', error);
    return false;
  }
};

// Run before starting server
app.listen(PORT, async () => {
  const dbHealthy = await checkDatabaseHealth();
  if (!dbHealthy) {
    console.error('Database is not healthy. Exiting...');
    process.exit(1);
  }
  console.log(`Server running on port ${PORT}`);
});