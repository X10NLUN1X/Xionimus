// diagnostic.routes.js
app.get('/api/diagnostics', async (req, res) => {
  const diagnostics = {
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV,
    checks: {}
  };

  // Database check
  try {
    await sequelize.authenticate();
    diagnostics.checks.database = 'OK';
  } catch (error) {
    diagnostics.checks.database = `FAIL: ${error.message}`;
  }

  // User table check
  try {
    const count = await User.count();
    diagnostics.checks.userTable = `OK (${count} users)`;
  } catch (error) {
    diagnostics.checks.userTable = `FAIL: ${error.message}`;
  }

  // JWT configuration check
  diagnostics.checks.jwt = {
    secretConfigured: !!process.env.JWT_SECRET,
    secretLength: process.env.JWT_SECRET?.length
  };

  // Test token generation
  try {
    const testToken = jwt.sign({ test: true }, process.env.JWT_SECRET);
    jwt.verify(testToken, process.env.JWT_SECRET);
    diagnostics.checks.tokenGeneration = 'OK';
  } catch (error) {
    diagnostics.checks.tokenGeneration = `FAIL: ${error.message}`;
  }

  res.json(diagnostics);
});