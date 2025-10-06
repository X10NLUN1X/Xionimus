// Add request tracking
const requestTracker = new Map();

app.use((req, res, next) => {
  const trackingId = Date.now() + Math.random();
  req.trackingId = trackingId;
  
  requestTracker.set(trackingId, {
    method: req.method,
    url: req.url,
    start: Date.now(),
    headers: req.headers
  });
  
  res.on('finish', () => {
    const tracking = requestTracker.get(trackingId);
    if (tracking) {
      tracking.end = Date.now();
      tracking.duration = tracking.end - tracking.start;
      tracking.status = res.statusCode;
      
      if (res.statusCode >= 400) {
        console.log('Request failed:', tracking);
      }
      
      requestTracker.delete(trackingId);
    }
  });
  
  next();
});