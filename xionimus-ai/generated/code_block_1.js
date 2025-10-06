// Enhanced error logging middleware
const errorLogger = (err, req, res, next) => {
  console.error('=== AUTH ERROR ===');
  console.error('Timestamp:', new Date().toISOString());
  console.error('Endpoint:', req.method, req.originalUrl);
  console.error('Headers:', req.headers);
  console.error('Body:', req.body);
  console.error('Error Stack:', err.stack);
  console.error('Error Details:', {
    name: err.name,
    message: err.message,
    code: err.code
  });
  console.error('==================');
  next(err);
};

app.use(errorLogger);