# Test login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}' \
  -v

# Test with token
curl http://localhost:3000/api/protected \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -v