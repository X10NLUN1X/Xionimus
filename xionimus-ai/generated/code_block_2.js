function authDiagnostics(req, res, next) {
  console.log('Authentication Diagnostics:');
  console.log('Request Body:', req.body);
  console.log('Headers:', req.headers);
  
  // Validate input basics
  if (!req.body.username || !req.body.password) {
    return res.status(400).json({ 
      error: 'Missing credentials' 
    });
  }

  next();
}