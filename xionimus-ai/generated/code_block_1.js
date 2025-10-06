// Add detailed logging middleware
const authDebugger = (req, res, next) => {
  console.log('=== AUTH REQUEST ===');
  console.log('Method:', req.method);
  console.log('Path:', req.path);
  console.log('Headers:', req.headers);
  console.log('Body:', req.body ? Object.keys(req.body) : 'No body');
  console.log('Cookies:', req.cookies);
  next();
};

// Error handler with full stack trace
app.use((err, req, res, next) => {
  console.error('=== ERROR DETAILS ===');
  console.error('Message:', err.message);
  console.error('Stack:', err.stack);
  console.error('Request URL:', req.url);
  console.error('Request Method:', req.method);
  console.error('Request Body:', req.body);
  
  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'development' ? {
      message: err.message,
      stack: err.stack,
      details: err
    } : 'Internal Server Error'
  });
});