// fixes.js - Common authentication fixes

// 1. Password hashing fix
const fixPasswordHashing = async () => {
  // Ensure passwords are properly hashed
  const users = await User.findAll();
  for (const user of users) {
    if (user.password && user.password.length < 50) {
      // Password likely not hashed
      const hashedPassword = await bcrypt.hash(user.password, 10);
      await user.update({ password: hashedPassword });
      console.log(`Fixed password for user ${user.email}`);
    }
  }
};

// 2. CORS configuration
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3001',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 3. Body parser middleware (ensure it's before routes)
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 4. Session cleanup (if using sessions)
app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    maxAge: 1000 * 60 * 60 * 24 // 24 hours
  }
}));