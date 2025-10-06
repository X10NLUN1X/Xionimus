// Enhanced login endpoint with debugging
app.post('/auth/login', async (req, res) => {
  console.log('\n=== LOGIN ATTEMPT ===');
  
  try {
    const { email, password } = req.body;
    console.log('1. Login attempt for:', email);
    
    // Validate input
    if (!email || !password) {
      console.log('❌ Missing credentials');
      return res.status(400).json({ 
        error: 'Missing credentials',
        debug: { email: !!email, password: !!password }
      });
    }
    
    // Find user
    const user = await User.findOne({ email }).select('+password');
    console.log('2. User found:', !!user);
    
    if (!user) {
      console.log('❌ User not found');
      return res.status(401).json({ 
        error: 'Invalid credentials',
        debug: 'User not found in database'
      });
    }
    
    // Check password
    const isPasswordValid = await bcrypt.compare(password, user.password);
    console.log('3. Password valid:', isPasswordValid);
    
    if (!isPasswordValid) {
      console.log('❌ Invalid password');
      return res.status(401).json({ 
        error: 'Invalid credentials',
        debug: 'Password mismatch'
      });
    }
    
    // Generate token
    const payload = {
      id: user._id.toString(),
      email: user.email,
      role: user.role
    };
    
    console.log('4. Token payload:', payload);
    
    const token = jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    console.log('5. Token generated:', token.substring(0, 20) + '...');
    
    // Test verify immediately
    try {
      const verified = jwt.verify(token, process.env.JWT_SECRET);
      console.log('6. Token verification test passed');
    } catch (verifyError) {
      console.error('❌ Token verification test failed:', verifyError);
    }
    
    console.log('=== LOGIN SUCCESS ===\n');
    
    res.json({
      success: true,
      token,
      user: {
        id: user._id,
        email: user.email,
        role: user.role
      }
    });
    
  } catch (error) {
    console.error('=== LOGIN ERROR ===');
    console.error(error);
    res.status(500).json({ 
      error: 'Login failed',
      debug: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});