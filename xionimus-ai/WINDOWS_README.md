# Xionimus AI - Windows Installation

## Quick Start

### 1. Install
```batch
install-windows.bat
```
Wait 5-10 minutes for installation to complete.

### 2. Start Application
```batch
START_ALL.bat
```
Or start individually:
- `START_BACKEND.bat` - Backend only (port 8001)
- `START_FRONTEND.bat` - Frontend only (port 3000)

### 3. Open Browser
```
http://localhost:3000
```

---

## Requirements

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js v18+** ([Download](https://nodejs.org/))
- **Git** (Optional, [Download](https://git-scm.com/))

---

## Troubleshooting

### "Virtuelle Umgebung nicht gefunden"
**Solution:** Run `install-windows.bat` first

### "Python not found"  
**Solution:** Install Python and ensure "Add Python to PATH" is checked

### "Cannot find specified path"
**Solution:** Make sure you're in the xionimus-ai folder when running scripts

### Still having issues?
1. Delete `backend\venv` folder
2. Run `install-windows.bat` again
3. If that fails, run as Administrator (right-click → Run as Administrator)

---

## What Each Script Does

- **install-windows.bat** - One-time setup (installs all dependencies)
- **START_BACKEND.bat** - Starts the Python backend server
- **START_FRONTEND.bat** - Starts the React frontend server  
- **START_ALL.bat** - Starts both backend and frontend together

---

## Notes

- First installation takes ~10 minutes (downloads ~2GB of packages)
- uvloop is not used on Windows (Linux/macOS only)
- All AI features work on Windows (ChromaDB, PyTorch, etc.)
