async function testDatabaseConnection() {
  try {
    await sequelize.authenticate();
    console.log('Database connection successful');
    
    // Check user table
    const userCount = await User.count();
    console.log('Total Users:', userCount);
  } catch (error) {
    console.error('Database Connection Failed:', error);
  }
}