// server.js - Correct middleware order
const express = require('express');
const app = express();

// 1. Body parsing MUST come first
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 2. CORS
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3001',
  credentials: true
}));

// 3. Logging
app.use(morgan('dev'));

// 4. Routes
app.use('/api/auth', authRoutes);
app.use('/api/user', authenticateToken, userRoutes);

// 5. Error handling MUST come last
app.use(errorHandler);