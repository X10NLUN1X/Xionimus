// Implement detailed error logging
app.use((err, req, res, next) => {
  console.error('Full Error Stack:', err);
  console.error('Error Message:', err.message);
  console.error('Error Details:', {
    path: req.path,
    method: req.method,
    body: req.body,
    headers: req.headers
  });

  res.status(500).json({
    error: 'Internal Server Error',
    details: process.env.NODE_ENV === 'development' ? err.message : null
  });
});