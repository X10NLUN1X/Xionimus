async function loginHandler(req, res) {
  try {
    // Detailed logging
    console.log('Login Attempt:', {
      username: req.body.username,
      timestamp: new Date()
    });

    // Validate input
    const { username, password } = req.body;
    
    // Find user with extensive logging
    const user = await User.findOne({ 
      where: { username },
      raw: true  // Get plain object
    });

    if (!user) {
      return res.status(404).json({ 
        error: 'User not found',
        debugInfo: {
          searchUsername: username,
          usernameLength: username.length
        }
      });
    }

    // Secure password comparison
    const isPasswordValid = await bcrypt.compare(
      password, 
      user.passwordHash
    );

    if (!isPasswordValid) {
      console.warn('Invalid Password Attempt', {
        username,
        ipAddress: req.ip
      });
      return res.status(401).json({ 
        error: 'Invalid credentials' 
      });
    }

    // Generate JWT with detailed payload
    const token = jwt.sign(
      { 
        userId: user.id, 
        role: user.role,
        loginTimestamp: Date.now()
      }, 
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        username: user.username,
        role: user.role
      }
    });

  } catch (error) {
    console.error('Login Process Error:', {
      message: error.message,
      stack: error.stack,
      name: error.name
    });

    res.status(500).json({ 
      error: 'Authentication system failure',
      systemMessage: error.message
    });
  }
}