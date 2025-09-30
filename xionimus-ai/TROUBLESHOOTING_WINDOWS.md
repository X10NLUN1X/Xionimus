# Windows Installation Troubleshooting Guide

## ❌ Error: "Das System kann den angegebenen Pfad nicht finden" (Cannot find specified path)

### 🎯 What This Means
The START_BACKEND.bat script cannot find the virtual environment (venv) folder. This usually means:
1. **Installation was not completed** - `install-windows.bat` was not run, or failed
2. **Running from wrong location** - Script is in the wrong directory
3. **Virtual environment was deleted** - The venv folder was accidentally removed

---

## ✅ SOLUTION: Step-by-Step Fix

### Step 1: Check Your Location
Open Command Prompt and verify you're in the correct directory:

```batch
cd C:\path\to\xionimus-ai
dir
```

**You should see:**
- `backend\` folder
- `frontend\` folder  
- `install-windows.bat`
- `START_BACKEND.bat`

If you don't see these, navigate to the correct directory first!

---

### Step 2: Run the Diagnostic Script
```batch
CHECK_INSTALLATION.bat
```

This will tell you exactly what's missing. Look for:
- ❌ [ERROR] Virtual environment NOT created → You need to run install-windows.bat
- ❌ [ERROR] node_modules NOT found → You need to run install-windows.bat
- ✅ [OK] markers mean that component is fine

---

### Step 3: Run Full Installation
If the diagnostic shows errors, run the full installation:

```batch
install-windows.bat
```

**Wait for it to complete!** This takes 5-10 minutes and includes:
1. Creating Python virtual environment
2. Installing Python packages (~100+ packages)
3. Installing Node.js packages
4. Creating start scripts

**Common installation issues:**
- **"Access denied"** → Run as Administrator (right-click → Run as Administrator)
- **"Python not found"** → Install Python 3.8+ from python.org
- **"Node not found"** → Install Node.js v18+ from nodejs.org
- **Installation hangs** → Check your internet connection

---

### Step 4: Verify Installation
After installation completes, check again:

```batch
CHECK_INSTALLATION.bat
```

**Expected output:**
```
[SUCCESS] Installation is COMPLETE and READY!
```

---

### Step 5: Start Backend
Now try starting the backend:

```batch
START_BACKEND.bat
```

**Expected output:**
```
[INFO] Aktiviere virtuelle Umgebung...
[INFO] Pruefe kritische Python-Abhaengigkeiten...
[OK] Alle Abhaengigkeiten vorhanden

Starte Backend auf http://localhost:8001
INFO:     Started server process [XXXX]
INFO:     Uvicorn running on http://0.0.0.0:8001
```

---

## 🔧 Advanced Troubleshooting

### Issue 1: Virtual Environment Exists But Can't Activate

**Symptoms:**
```
[INFO] Aktiviere virtuelle Umgebung...
Das System kann den angegebenen Pfad nicht finden.
```

**But** the diagnostic shows venv exists.

**Solution A: PowerShell ExecutionPolicy**
```powershell
# Open PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solution B: Recreate Virtual Environment**
```batch
cd backend
rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

---

### Issue 2: "Python not found" Inside Virtual Environment

**Symptoms:**
Virtual environment exists but Python is missing inside it.

**Solution: Recreate venv with full path**
```batch
cd backend
rmdir /s /q venv
C:\Python311\python.exe -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

*Replace `C:\Python311\python.exe` with your actual Python path*

---

### Issue 3: "Module not found" Errors After Activation

**Symptoms:**
```
[FEHLER] fastapi fehlt!
[FEHLER] pypdf fehlt!
```

**Solution A: Auto-install (START_BACKEND.bat should do this)**
The script will automatically install missing packages.

**Solution B: Manual install**
```batch
cd backend
call venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

**Solution C: Clear pip cache and reinstall**
```batch
cd backend
call venv\Scripts\activate.bat
pip cache purge
pip install -r requirements-windows.txt --no-cache-dir
```

---

### Issue 4: Multiple Python Versions Conflict

**Symptoms:**
Wrong Python version in venv, or venv uses system Python incorrectly.

**Solution: Specify Python version explicitly**
```batch
cd backend
rmdir /s /q venv

REM Use Python 3.11 (adjust to your version)
py -3.11 -m venv venv

REM Or use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m venv venv

call venv\Scripts\activate.bat
pip install -r requirements-windows.txt
```

---

### Issue 5: Antivirus Blocking Scripts

**Symptoms:**
Scripts fail silently or get blocked by Windows Defender / antivirus.

**Solution:**
1. Add exception for `xionimus-ai` folder in Windows Defender
2. Temporarily disable antivirus during installation
3. Run scripts as Administrator

**Windows Defender Exception:**
```
Settings → Privacy & Security → Windows Security → Virus & threat protection
→ Manage settings → Exclusions → Add or remove exclusions
→ Add folder: C:\path\to\xionimus-ai
```

---

### Issue 6: Path Contains Spaces or Special Characters

**Symptoms:**
Scripts fail with path-related errors if project is in folder like "My Documents" or "Projekte (neu)"

**Solution: Move project to simple path**
```batch
REM BAD (avoid these):
C:\Users\John Doe\Documents\xionimus-ai
C:\Projekte (neu)\xionimus-ai
C:\Projects\AI & ML\xionimus-ai

REM GOOD (use these):
C:\xionimus-ai
C:\Users\john\xionimus-ai
C:\projects\xionimus-ai
D:\dev\xionimus-ai
```

---

## 📋 Quick Reference Commands

### Check if Python is in PATH
```batch
python --version
where python
```

### Check if Node is in PATH
```batch
node -v
where node
```

### Check if venv exists
```batch
dir backend\venv
```

### Manually activate venv
```batch
cd backend
venv\Scripts\activate.bat
```

### Check installed Python packages in venv
```batch
cd backend
call venv\Scripts\activate.bat
pip list
```

### Reinstall everything from scratch
```batch
cd backend
rmdir /s /q venv
rmdir /s /q __pycache__
cd ..\frontend
rmdir /s /q node_modules
cd ..
install-windows.bat
```

---

## 🆘 Still Having Issues?

### Collect Diagnostic Information

Run these commands and share the output:

```batch
REM 1. Check installation
CHECK_INSTALLATION.bat > diagnostic_report.txt

REM 2. Check Python
python --version >> diagnostic_report.txt
where python >> diagnostic_report.txt

REM 3. Check directory structure
dir >> diagnostic_report.txt
dir backend >> diagnostic_report.txt

REM 4. Check venv
dir backend\venv >> diagnostic_report.txt 2>&1
```

Then open `diagnostic_report.txt` and share it.

---

## ✅ Verification Checklist

Before asking for help, verify:
- [ ] Python 3.8+ is installed: `python --version`
- [ ] Node.js v18+ is installed: `node -v`
- [ ] You're in the xionimus-ai directory: `cd C:\path\to\xionimus-ai`
- [ ] You ran install-windows.bat completely: `CHECK_INSTALLATION.bat`
- [ ] backend\venv folder exists: `dir backend\venv`
- [ ] Python is in venv: `dir backend\venv\Scripts\python.exe`
- [ ] No antivirus blocking: Check Windows Defender exclusions
- [ ] No path issues: Path doesn't contain spaces or special characters

---

## 📞 Getting Help

When reporting issues, include:
1. **Your Windows version:** Windows 10/11, version, build
2. **Python version:** Output of `python --version`
3. **Node version:** Output of `node -v`
4. **Error message:** Exact text of the error
5. **Diagnostic report:** Output of `CHECK_INSTALLATION.bat`
6. **What you tried:** List all solutions you attempted
7. **Project path:** Where xionimus-ai is located

---

**Last Updated:** 2025-09-30 (v2.1.0)
**Critical Fix:** Path detection for admin rights, python-cors removal, enhanced error handling
