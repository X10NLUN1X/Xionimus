# Python Cache Issue - Code Changes Not Applied

**Issue:** Code changes not reflected after restart due to Python bytecode cache

**Status:** ✅ FIXED - Cache cleared

---

## 🐛 The Problem

Even after changing the Perplexity timeout from 60s to 300s and restarting the backend, the error still showed:
```
ERROR: Perplexity API timeout: Request took longer than 60 seconds
```

**Root Cause:**
- Python caches bytecode in `__pycache__` directories as `.pyc` files
- When code changes, Python may load old cached versions instead of new code
- Backend restart doesn't automatically clear Python cache
- `uvicorn --reload` sometimes doesn't detect changes in imported modules

---

## ✅ Fix Applied

### Cleared all Python cache:

```bash
# Remove all .pyc files
find /app/backend -name "*.pyc" -delete

# Remove all __pycache__ directories
find /app/backend -type d -name "__pycache__" -exec rm -rf {} +

# Restart backend completely
sudo supervisorctl stop backend
sudo supervisorctl start backend
```

---

## 🔍 Why This Happens

### Python Bytecode Caching:

When Python imports a module, it:
1. **Compiles** `.py` file to bytecode
2. **Saves** bytecode in `__pycache__/module.cpython-311.pyc`
3. **Checks** modification time of `.py` vs `.pyc`
4. **Uses cached `.pyc`** if `.py` hasn't changed (by timestamp)

**Problem:** Sometimes timestamp check fails or cache isn't invalidated

### Common Scenarios:

1. **File edited but timestamp unchanged** (rare)
2. **Module imported before change** (hot reload issue)
3. **Supervisor restart too fast** (doesn't wait for cleanup)
4. **NFS/Docker volumes** (timestamp issues)

---

## 🧪 Verification

### Check if cache is causing issues:

```bash
# Find all .pyc files
find /app/backend/app -name "*.pyc"

# Check modification time
ls -la /app/backend/app/core/__pycache__/

# Should show .pyc files older than .py files if cache is stale
```

### After clearing cache:

```bash
# No .pyc files should exist immediately after clearing
find /app/backend/app -name "*.pyc" | wc -l
# Should output: 0

# After first request, new .pyc files are created
# These will have current timestamps
```

---

## 🚀 Prevention

### Method 1: Add to restart script

```bash
#!/bin/bash
# File: restart_backend.sh

echo "Clearing Python cache..."
find /app/backend -name "*.pyc" -delete
find /app/backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

echo "Restarting backend..."
sudo supervisorctl restart backend

echo "✅ Backend restarted with fresh code"
```

### Method 2: Disable Python cache (Development)

```bash
# Run Python with -B flag (don't write .pyc files)
python -B -m uvicorn main:app --reload

# Or set environment variable
export PYTHONDONTWRITEBYTECODE=1
uvicorn main:app --reload
```

**Note:** Disabling cache slows down startup, use only for development

### Method 3: Use proper reload mode

```bash
# Uvicorn with reload watches for file changes
uvicorn main:app --reload --reload-dir /app/backend/app
```

---

## 📊 Cache Locations

### Python creates cache in:

```
/app/backend/app/
├── core/
│   ├── __pycache__/
│   │   ├── ai_manager.cpython-311.pyc  ← Cached bytecode
│   │   ├── config.cpython-311.pyc
│   │   └── database.cpython-311.pyc
│   ├── ai_manager.py                   ← Source code
│   └── config.py
├── api/
│   ├── __pycache__/
│   │   ├── chat.cpython-311.pyc
│   │   └── chat_stream.cpython-311.pyc
│   ├── chat.py
│   └── chat_stream.py
```

---

## 🔧 Manual Cache Clear

### During development:

```bash
# Quick cache clear for specific module
rm -rf /app/backend/app/core/__pycache__/

# Clear all cache in app
find /app/backend/app -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Clear everything including venv (use with caution)
find /app/backend -name "*.pyc" -delete
```

### In production:

```bash
# Stop service first
sudo supervisorctl stop backend

# Clear cache
find /app/backend/app -name "*.pyc" -delete
find /app/backend/app -type d -name "__pycache__" -exec rm -rf {} +

# Start service
sudo supervisorctl start backend
```

---

## 🎯 Best Practices

### For Development:

1. **Use hot reload:** `uvicorn main:app --reload`
2. **Clear cache on major changes:** Especially for critical files
3. **Restart completely:** `stop` then `start` instead of just `restart`
4. **Watch logs:** Verify changes are loaded

### For Production:

1. **Pre-compile:** Run `python -m compileall` before deployment
2. **Clear on deploy:** Always clear cache during deployment
3. **Use fresh environment:** Deploy to new directory or container
4. **Test changes:** Verify critical changes took effect

---

## 🚨 Signs of Cache Issues

### You might have cache issues if:

- ✅ Code changed but behavior didn't
- ✅ Error messages show old text
- ✅ New functions not found
- ✅ Old bugs reappear
- ✅ Restart doesn't fix issues
- ✅ Manual file edit visible but not active

### Quick test:

```python
# Add to your code temporarily
import sys
print(f"Module loaded from: {__file__}")
print(f"Python cache: {sys.dont_write_bytecode}")

# If __file__ points to .pyc, cache is being used
```

---

## 📝 Summary

**Problem:** Python bytecode cache prevented new code from loading  
**Solution:** Clear all `.pyc` files and `__pycache__` directories  
**Prevention:** Clear cache before important restarts  
**Status:** ✅ FIXED

**Commands to remember:**
```bash
# Clear cache
find /app/backend -name "*.pyc" -delete
find /app/backend -type d -name "__pycache__" -exec rm -rf {} +

# Restart fresh
sudo supervisorctl stop backend
sudo supervisorctl start backend
```

**The timeout change (60s → 300s) is now active!** ✅

---

**Always clear Python cache when making critical code changes!**
