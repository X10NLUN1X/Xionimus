// Debug version of login endpoint
app.post('/auth/login', async (req, res) => {
  console.log('\n=== LOGIN ATTEMPT DEBUG ===');
  
  try {
    const { email, password } = req.body;
    console.log('1. Login attempt for:', email);
    
    // Check if user exists
    const userResult = await db.query(
      'SELECT * FROM users WHERE email = $1',
      [email]
    );
    
    console.log('2. User found?', userResult.rows.length > 0);
    
    if (userResult.rows.length === 0) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    const user = userResult.rows[0];
    console.log('3. User data retrieved:', {
      id: user.id,
      email: user.email,
      hasPassword: !!user.password
    });
    
    // Verify password
    const bcrypt = require('bcrypt');
    console.log('4. Comparing passwords...');
    console.log('   Password provided?', !!password);
    console.log('   Stored hash exists?', !!user.password);
    
    const isValid = await bcrypt.compare(password, user.password);
    console.log('5. Password valid?', isValid);
    
    if (!isValid) {
      return res.status(401).json({ error: 'Invalid password' });
    }
    
    // Generate token
    const jwt = require('jsonwebtoken');
    const token = jwt.sign(
      { 
        userId: user.id, 
        email: user.email 
      },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    console.log('6. Token generated successfully');
    console.log('   Token length:', token.length);
    console.log('=========================\n');
    
    res.json({
      token,
      user: {
        id: user.id,
        email: user.email
      }
    });
    
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      error: 'Login failed',
      details: error.message,
      stack: error.stack 
    });
  }
});