@echo off
echo ==========================================
echo Running Xionimus AI Tests on Windows
echo ==========================================

cd backend
call venv\Scripts\activate
python -m pytest tests/ -v
pause
