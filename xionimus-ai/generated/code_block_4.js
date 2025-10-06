// Wrong order can cause 500s
app.use(authMiddleware)  // Must be AFTER
app.use(bodyParser.json()) // this