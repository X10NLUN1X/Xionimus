// Fixed login endpoint
app.post('/api/auth/login', async (req, res) => {
  console.log('=== LOGIN ATTEMPT ===');
  
  try {
    const { email, password } = req.body;
    
    // Validation
    if (!email || !password) {
      console.log('Missing credentials');
      return res.status(400).json({ 
        error: 'Email and password are required',
        received: { email: !!email, password: !!password }
      });
    }
    
    console.log('Looking up user:', email);
    
    // Find user (explicitly select password field)
    const user = await User.findOne({ email: email.toLowerCase() })
      .select('+password'); // MongoDB/Mongoose specific
    
    if (!user) {
      console.log('User not found:', email);
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    console.log('User found, checking password...');
    
    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.password);
    
    if (!isValidPassword) {
      console.log('Invalid password for user:', email);
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    console.log('Password valid, generating token...');
    
    // Generate JWT
    const tokenPayload = {
      userId: user._id,
      email: user.email,
      role: user.role // if applicable
    };
    
    const token = jwt.sign(
      tokenPayload,
      process.env.JWT_SECRET,
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );
    
    console.log('Token generated successfully');
    
    // Remove password from response
    const userResponse = user.toObject();
    delete userResponse.password;
    
    // Send response with multiple token delivery methods
    res
      .cookie('token', token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
        maxAge: 24 * 60 * 60 * 1000 // 24 hours
      })
      .json({
        success: true,
        token,
        user: userResponse
      });
      
    console.log('Login successful for:', email);
    
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ 
      error: 'Login failed',
      message: process.env.NODE_ENV === 'development' ? error.message : 'Internal server error',
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
});