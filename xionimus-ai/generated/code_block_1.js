// Add this debugging middleware temporarily
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  console.log('Headers:', req.headers);
  console.log('Body:', req.body);
  next();
});

// Enhanced error handler
app.use((err, req, res, next) => {
  console.error('Error Details:', {
    message: err.message,
    stack: err.stack,
    code: err.code,
    statusCode: err.statusCode,
    timestamp: new Date().toISOString(),
    path: req.path,
    method: req.method,
    body: req.body,
    headers: req.headers
  });
  
  res.status(err.statusCode || 500).json({
    error: process.env.NODE_ENV === 'production' 
      ? 'Internal Server Error' 
      : err.message,
    details: process.env.NODE_ENV !== 'production' ? err.stack : undefined
  });
});