// Comprehensive auth controller with all common fixes
const authController = {
  login: async (req, res, next) => {
    try {
      console.log('Login attempt:', { email: req.body.email });
      
      // 1. Input validation
      const { email, password } = req.body;
      
      if (!email || !password) {
        return res.status(400).json({ 
          error: 'Email and password are required' 
        });
      }

      // 2. User lookup with proper error handling
      const user = await User.findOne({ 
        email: email.toLowerCase().trim() // Normalize email
      }).select('+password'); // Ensure password is included
      
      console.log('User found:', !!user);
      
      if (!user) {
        return res.status(401).json({ 
          error: 'Invalid credentials' 
        });
      }

      // 3. Password verification with detailed logging
      console.log('Comparing passwords...');
      const isValidPassword = await bcrypt.compare(
        password,
        user.password
      );
      
      console.log('Password valid:', isValidPassword);
      
      if (!isValidPassword) {
        return res.status(401).json({ 
          error: 'Invalid credentials' 
        });
      }

      // 4. JWT generation with proper error handling
      if (!process.env.JWT_SECRET) {
        throw new Error('JWT_SECRET is not configured');
      }

      const token = jwt.sign(
        { 
          userId: user._id.toString(), // Convert ObjectId to string
          email: user.email 
        },
        process.env.JWT_SECRET,
        { 
          expiresIn: '24h',
          algorithm: 'HS256' // Explicitly specify algorithm
        }
      );

      // 5. Remove password from response
      const userResponse = user.toObject();
      delete userResponse.password;

      // 6. Send response with multiple options for token storage
      res
        .cookie('token', token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === 'production',
          sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
          maxAge: 24 * 60 * 60 * 1000 // 24 hours
        })
        .status(200)
        .json({
          success: true,
          token, // Also send in body for localStorage option
          user: userResponse
        });

    } catch (error) {
      console.error('Login error:', error);
      next(error);
    }
  }
};