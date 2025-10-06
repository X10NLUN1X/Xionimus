// Fix 1: Async middleware wrapper (prevents unhandled promise rejections)
const asyncHandler = fn => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Use it like this:
app.post('/api/auth/login', asyncHandler(async (req, res) => {
  // Your async code
}));

// Fix 2: CORS issues
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true, // Important for cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-auth-token']
}));

// Fix 3: Body parser issues
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));