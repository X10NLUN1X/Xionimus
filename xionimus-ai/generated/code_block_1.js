// Enhanced error logging middleware
const errorLogger = (err, req, res, next) => {
  console.error('=== AUTH ERROR DEBUG ===');
  console.error('Timestamp:', new Date().toISOString());
  console.error('Endpoint:', req.method, req.originalUrl);
  console.error('Headers:', req.headers);
  console.error('Body:', req.body);
  console.error('Error Stack:', err.stack);
  console.error('Error Details:', {
    message: err.message,
    name: err.name,
    code: err.code
  });
  console.error('========================');
  
  next(err);
};

app.use(errorLogger);