// minimal-auth.js - Bare minimum working authentication
const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const app = express();

app.use(express.json());

// Hardcoded for testing
const JWT_SECRET = 'emergency-secret-change-this';
const users = new Map();

app.post('/api/auth/register', async (req, res) => {
  const { email, password } = req.body;
  const hashedPassword = await bcrypt.hash(password, 10);
  users.set(email, { email, password: hashedPassword });
  res.json({ message: 'User created' });
});

app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = users.get(email);
  
  if (!user || !await bcrypt.compare(password, user.password)) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  const token = jwt.sign({ email }, JWT_SECRET);
  res.json({ token, user: { email } });
});

app.listen(5000, () => console.log('Minimal auth running on :5000'));