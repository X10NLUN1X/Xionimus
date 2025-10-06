# Run these checks:

# 1. Check environment variables
cat .env | grep -E "JWT_SECRET|DATABASE_URL|NODE_ENV"

# 2. Check npm packages are installed
npm ls bcryptjs jsonwebtoken express cors cookie-parser

# 3. Reinstall dependencies if needed
rm -rf node_modules package-lock.json
npm install

# 4. Check MongoDB is running (if using MongoDB)
mongosh --eval "db.adminCommand('ping')"

# 5. Clear any corrupted data
# In MongoDB shell:
# db.users.find({email: "test@example.com"})
# Check password field exists and is hashed