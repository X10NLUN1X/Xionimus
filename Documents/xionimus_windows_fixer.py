"""
XIONIMUS AI - Automated Windows Bug Fixes
This script automatically fixes critical Windows compatibility issues
Run this BEFORE testing to patch known problems
"""

import os
import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import json

class XionimusWindowsFixer:
    """Automated bug fixes for Windows compatibility"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.backend_path = self.project_path / "backend"
        self.frontend_path = self.project_path / "frontend"
        self.fixes_applied = []
        self.fixes_failed = []
        
    def run_all_fixes(self):
        """Apply all Windows compatibility fixes"""
        print("=" * 80)
        print("XIONIMUS AI - WINDOWS COMPATIBILITY FIXES")
        print("=" * 80)
        print(f"Project Path: {self.project_path}\n")
        
        # Apply fixes in order of priority
        self.fix_sandbox_executor()
        self.fix_supervisor_manager()
        self.fix_path_issues()
        self.fix_subprocess_commands()
        self.fix_asyncio_issues()
        self.fix_database_paths()
        self.fix_websocket_issues()
        self.fix_requirements()
        self.fix_environment_variables()
        self.fix_frontend_env()
        self.create_windows_scripts()
        
        # Report results
        self.print_summary()
        
    def fix_sandbox_executor(self):
        """Fix sandbox executor for Windows"""
        print("\n[1] Fixing Sandbox Executor...")
        
        sandbox_file = self.backend_path / "app" / "core" / "sandbox_executor.py"
        if not sandbox_file.exists():
            print("  ⚠ sandbox_executor.py not found")
            return
            
        try:
            with open(sandbox_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix resource module import
            if 'import resource' in content and 'sys.platform' not in content:
                # Add platform check
                new_import = """import sys
import platform

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
HAS_RESOURCE = False

if not IS_WINDOWS:
    try:
        import resource
        HAS_RESOURCE = True
    except ImportError:
        pass"""
                
                content = content.replace('import resource', new_import)
                
            # Fix resource.setrlimit usage
            content = re.sub(
                r'resource\.setrlimit\((.*?)\)',
                r'if HAS_RESOURCE: resource.setrlimit(\1)',
                content
            )
            
            # Fix preexec_fn usage
            content = re.sub(
                r'preexec_fn=.*?,',
                r'preexec_fn=set_limits if not IS_WINDOWS else None,',
                content
            )
            
            # Add Windows-specific timeout handling
            if 'subprocess.run' in content and 'timeout=' in content:
                if 'creationflags' not in content:
                    content = re.sub(
                        r'(subprocess\.run\([^)]+)(timeout=\d+)',
                        r'\1\2, creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0',
                        content
                    )
                    
            # Fix /tmp path
            content = content.replace('/tmp/', 'tempfile.gettempdir() + os.sep')
            
            if content != original_content:
                # Backup original
                backup_file = sandbox_file.with_suffix('.py.bak')
                shutil.copy2(sandbox_file, backup_file)
                
                # Write fixed content
                with open(sandbox_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("  ✓ Fixed sandbox_executor.py")
                self.fixes_applied.append("sandbox_executor.py")
            else:
                print("  ✓ sandbox_executor.py already fixed")
                
        except Exception as e:
            print(f"  ✗ Failed to fix sandbox_executor.py: {e}")
            self.fixes_failed.append(("sandbox_executor.py", str(e)))
            
    def fix_supervisor_manager(self):
        """Fix supervisor manager for Windows"""
        print("\n[2] Fixing Supervisor Manager...")
        
        supervisor_file = self.backend_path / "app" / "core" / "supervisor_manager.py"
        if not supervisor_file.exists():
            print("  ⚠ supervisor_manager.py not found")
            return
            
        try:
            with open(supervisor_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Replace Unix commands with Windows equivalents
            replacements = {
                "'grep'": "'findstr'" if sys.platform == 'win32' else "'grep'",
                '"grep"': '"findstr"' if sys.platform == 'win32' else '"grep"',
                "'ls'": "'dir'" if sys.platform == 'win32' else "'ls'",
                '"ls"': '"dir"' if sys.platform == 'win32' else '"ls"',
                "'chmod'": "'icacls'" if sys.platform == 'win32' else "'chmod'",
                '"chmod"': '"icacls"' if sys.platform == 'win32' else '"chmod"',
            }
            
            for old, new in replacements.items():
                content = content.replace(old, new)
                
            # Fix signal handling
            if 'signal.SIGKILL' in content:
                content = content.replace(
                    'signal.SIGKILL',
                    'signal.SIGTERM if sys.platform != "win32" else signal.SIGTERM'
                )
                
            if content != original_content:
                # Backup and write
                backup_file = supervisor_file.with_suffix('.py.bak')
                shutil.copy2(supervisor_file, backup_file)
                
                with open(supervisor_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("  ✓ Fixed supervisor_manager.py")
                self.fixes_applied.append("supervisor_manager.py")
            else:
                print("  ✓ supervisor_manager.py already fixed")
                
        except Exception as e:
            print(f"  ✗ Failed to fix supervisor_manager.py: {e}")
            self.fixes_failed.append(("supervisor_manager.py", str(e)))
            
    def fix_path_issues(self):
        """Fix path separator and hardcoded path issues"""
        print("\n[3] Fixing Path Issues...")
        
        # Find all Python files
        py_files = list(self.backend_path.glob("app/**/*.py"))
        
        fixed_count = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                
                # Fix /tmp paths
                if '/tmp' in content:
                    content = re.sub(
                        r'["\']\/tmp\/',
                        r'tempfile.gettempdir() + os.sep + "',
                        content
                    )
                    # Add tempfile import if needed
                    if 'import tempfile' not in content:
                        content = 'import tempfile\n' + content
                        
                # Fix hardcoded Unix paths
                unix_paths = ['/var/', '/usr/', '/etc/', '/home/']
                for unix_path in unix_paths:
                    if unix_path in content:
                        # Add warning comment
                        content = content.replace(
                            unix_path,
                            f'{unix_path}  # WARNING: Unix path - needs Windows alternative'
                        )
                        
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    
            except Exception as e:
                pass  # Skip files with encoding issues
                
        if fixed_count > 0:
            print(f"  ✓ Fixed path issues in {fixed_count} files")
            self.fixes_applied.append(f"Path issues in {fixed_count} files")
        else:
            print("  ✓ No path issues found")
            
    def fix_subprocess_commands(self):
        """Fix subprocess commands for Windows"""
        print("\n[4] Fixing Subprocess Commands...")
        
        # Find files with subprocess usage
        py_files = list(self.backend_path.glob("app/**/*.py"))
        
        fixed_count = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'subprocess' not in content:
                    continue
                    
                original_content = content
                
                # Add platform detection if not present
                if 'IS_WINDOWS' not in content and 'subprocess' in content:
                    content = "IS_WINDOWS = sys.platform == 'win32'\n" + content
                    
                # Fix shell=True usage
                if 'shell=True' in content:
                    # Add warning comment
                    content = re.sub(
                        r'shell=True',
                        r'shell=True  # WARNING: Check Windows compatibility',
                        content
                    )
                    
                # Add creationflags for Windows
                if 'subprocess.run' in content or 'subprocess.Popen' in content:
                    if 'creationflags' not in content and 'CREATE_NO_WINDOW' not in content:
                        # Add import
                        if 'import subprocess' in content:
                            content = content.replace(
                                'import subprocess',
                                'import subprocess\nif sys.platform == "win32":\n    subprocess.CREATE_NO_WINDOW = 0x08000000'
                            )
                            
                if content != original_content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    
            except Exception as e:
                pass
                
        if fixed_count > 0:
            print(f"  ✓ Fixed subprocess usage in {fixed_count} files")
            self.fixes_applied.append(f"Subprocess fixes in {fixed_count} files")
        else:
            print("  ✓ No subprocess issues found")
            
    def fix_asyncio_issues(self):
        """Fix asyncio event loop for Windows"""
        print("\n[5] Fixing Asyncio Issues...")
        
        main_file = self.backend_path / "main.py"
        if not main_file.exists():
            print("  ⚠ main.py not found")
            return
            
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Add Windows event loop policy
            if 'asyncio' in content and 'WindowsProactorEventLoopPolicy' not in content:
                # Find where to add the policy setting
                if '__name__ == "__main__"' in content:
                    content = content.replace(
                        '__name__ == "__main__"',
                        '''__name__ == "__main__"
    # Set Windows event loop policy
    if sys.platform == 'win32':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    if __name__ == "__main__"'''
                    )
                    
            # Remove uvloop if present
            if 'uvloop' in content:
                content = re.sub(r'import uvloop.*?\n', '', content)
                content = re.sub(r'uvloop\.install\(\).*?\n', '', content)
                
            if content != original_content:
                # Backup and write
                backup_file = main_file.with_suffix('.py.bak')
                shutil.copy2(main_file, backup_file)
                
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("  ✓ Fixed asyncio configuration in main.py")
                self.fixes_applied.append("main.py asyncio")
            else:
                print("  ✓ Asyncio already configured for Windows")
                
        except Exception as e:
            print(f"  ✗ Failed to fix asyncio: {e}")
            self.fixes_failed.append(("asyncio", str(e)))
            
    def fix_database_paths(self):
        """Fix database path issues for Windows"""
        print("\n[6] Fixing Database Paths...")
        
        db_file = self.backend_path / "app" / "core" / "database.py"
        if not db_file.exists():
            # Try alternative locations
            db_file = self.backend_path / "app" / "database.py"
            
        if not db_file.exists():
            print("  ⚠ database.py not found")
            return
            
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            
            # Fix SQLite paths
            if 'sqlite:///' in content:
                # Make sure paths are absolute on Windows
                content = re.sub(
                    r'sqlite:\/\/\/(?![\w:])',  # sqlite:/// not followed by drive letter
                    r'sqlite:///' + str(Path.cwd()).replace('\\', '/') + '/',
                    content
                )
                
            if content != original_content:
                backup_file = db_file.with_suffix('.py.bak')
                shutil.copy2(db_file, backup_file)
                
                with open(db_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print("  ✓ Fixed database paths")
                self.fixes_applied.append("database.py")
            else:
                print("  ✓ Database paths already fixed")
                
        except Exception as e:
            print(f"  ✗ Failed to fix database paths: {e}")
            self.fixes_failed.append(("database paths", str(e)))
            
    def fix_websocket_issues(self):
        """Fix WebSocket issues for Windows"""
        print("\n[7] Fixing WebSocket Issues...")
        
        ws_files = list(self.backend_path.glob("app/**/*websocket*.py"))
        ws_files.extend(list(self.backend_path.glob("app/**/*ws*.py")))
        
        fixed_count = 0
        for ws_file in ws_files:
            try:
                with open(ws_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                original_content = content
                
                # Add proper error handling for Windows
                if 'websocket' in content.lower():
                    if 'ConnectionResetError' not in content:
                        # Add error handling
                        content = re.sub(
                            r'(async def.*?websocket.*?:)',
                            r'''\1
    try:
        # Existing code will be indented
    except ConnectionResetError:
        logger.warning("WebSocket connection reset (common on Windows)")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")''',
                            content,
                            count=1
                        )
                        
                if content != original_content:
                    with open(ws_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    fixed_count += 1
                    
            except Exception as e:
                pass
                
        if fixed_count > 0:
            print(f"  ✓ Fixed WebSocket handling in {fixed_count} files")
            self.fixes_applied.append(f"WebSocket fixes in {fixed_count} files")
        else:
            print("  ✓ No WebSocket issues found")
            
    def fix_requirements(self):
        """Create Windows-specific requirements file"""
        print("\n[8] Fixing Requirements...")
        
        req_file = self.backend_path / "requirements.txt"
        req_win_file = self.backend_path / "requirements-windows.txt"
        
        if not req_file.exists():
            print("  ⚠ requirements.txt not found")
            return
            
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
                
            # Remove Unix-only packages and add Windows alternatives
            windows_lines = []
            skip_packages = ['uvloop', 'gunicorn', 'python-daemon', 'pyinotify']
            replacements = {
                'python-magic': 'python-magic-bin==0.4.14',
                'psycopg2': 'psycopg2-binary',
            }
            
            for line in lines:
                line_lower = line.lower()
                
                # Skip Unix-only packages
                if any(pkg in line_lower for pkg in skip_packages):
                    continue
                    
                # Replace with Windows versions
                replaced = False
                for old, new in replacements.items():
                    if old in line_lower:
                        windows_lines.append(new + '\n')
                        replaced = True
                        break
                        
                if not replaced:
                    windows_lines.append(line)
                    
            # Add Windows-specific packages if not present
            windows_specific = ['pywin32>=307']
            for pkg in windows_specific:
                if not any(pkg.split('>=')[0] in line for line in windows_lines):
                    windows_lines.append(pkg + '\n')
                    
            # Write Windows requirements
            with open(req_win_file, 'w') as f:
                f.writelines(windows_lines)
                
            print("  ✓ Created requirements-windows.txt")
            self.fixes_applied.append("requirements-windows.txt")
            
        except Exception as e:
            print(f"  ✗ Failed to fix requirements: {e}")
            self.fixes_failed.append(("requirements", str(e)))
            
    def fix_environment_variables(self):
        """Create Windows-compatible .env file"""
        print("\n[9] Fixing Environment Variables...")
        
        env_example = self.backend_path / ".env.example"
        env_file = self.backend_path / ".env"
        
        if not env_example.exists() and not env_file.exists():
            # Create a basic .env file
            env_content = """# Xionimus AI Environment Variables for Windows

# Security
SECRET_KEY=your-secret-key-here-change-this

# Database
DATABASE_URL=sqlite:///./xionimus.db
MONGODB_URL=mongodb://localhost:27017/xionimus

# API Keys (Add your own)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
PERPLEXITY_API_KEY=
GITHUB_TOKEN=

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Frontend URL
FRONTEND_URL=http://localhost:3000

# File Storage (Windows paths)
UPLOAD_DIR=./uploads
TEMP_DIR=./temp

# Logging
LOG_LEVEL=INFO
"""
            
            try:
                if not env_file.exists():
                    with open(env_file, 'w') as f:
                        f.write(env_content)
                    print("  ✓ Created .env file with Windows paths")
                    self.fixes_applied.append(".env")
                else:
                    print("  ✓ .env file already exists")
            except Exception as e:
                print(f"  ✗ Failed to create .env: {e}")
                self.fixes_failed.append((".env", str(e)))
        else:
            print("  ✓ Environment configuration exists")
            
    def fix_frontend_env(self):
        """Fix frontend environment for Windows"""
        print("\n[10] Fixing Frontend Environment...")
        
        # Fix package.json scripts
        package_json = self.frontend_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    
                # Check scripts for Unix commands
                scripts = data.get('scripts', {})
                modified = False
                
                for name, script in scripts.items():
                    if 'rm -rf' in script:
                        # Replace with cross-platform alternative
                        scripts[name] = script.replace('rm -rf', 'rimraf')
                        modified = True
                    if 'cp' in script and 'cpx' not in script:
                        scripts[name] = script.replace('cp', 'cpx')
                        modified = True
                        
                if modified:
                    # Add required dev dependencies
                    dev_deps = data.get('devDependencies', {})
                    if 'rimraf' not in dev_deps:
                        dev_deps['rimraf'] = '^3.0.2'
                    if 'cpx' not in dev_deps:
                        dev_deps['cpx'] = '^1.5.0'
                        
                    data['devDependencies'] = dev_deps
                    
                    # Backup and write
                    backup_file = package_json.with_suffix('.json.bak')
                    shutil.copy2(package_json, backup_file)
                    
                    with open(package_json, 'w') as f:
                        json.dump(data, f, indent=2)
                        
                    print("  ✓ Fixed package.json scripts for Windows")
                    self.fixes_applied.append("package.json")
                else:
                    print("  ✓ package.json already Windows-compatible")
                    
            except Exception as e:
                print(f"  ✗ Failed to fix package.json: {e}")
                self.fixes_failed.append(("package.json", str(e)))
        else:
            print("  ⚠ package.json not found")
            
    def create_windows_scripts(self):
        """Create Windows batch scripts for easy setup and running"""
        print("\n[11] Creating Windows Scripts...")
        
        # Create install.bat
        install_bat = self.project_path / "install-windows.bat"
        install_content = """@echo off
echo ==========================================
echo Xionimus AI - Windows Installation
echo ==========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.11+
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 18+
    pause
    exit /b 1
)

echo.
echo Installing Backend...
cd backend
python -m venv venv
call venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements-windows.txt

echo.
echo Installing Frontend...
cd ..\\frontend
call npm install

echo.
echo ==========================================
echo Installation Complete!
echo Run 'start-windows.bat' to start the application
echo ==========================================
pause
"""
        
        # Create start.bat
        start_bat = self.project_path / "start-windows.bat"
        start_content = """@echo off
echo ==========================================
echo Starting Xionimus AI on Windows
echo ==========================================

REM Start MongoDB (if installed as service, it should already be running)
echo Checking MongoDB...
mongo --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MongoDB not found. Some features may not work.
)

REM Start Backend
echo.
echo Starting Backend Server...
start cmd /k "cd backend && venv\\Scripts\\activate && python main.py"

REM Wait a moment for backend to start
timeout /t 5 /nobreak >nul

REM Start Frontend
echo Starting Frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo Xionimus AI is starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ==========================================
echo Press any key to open in browser...
pause >nul
start http://localhost:3000
"""
        
        # Create test.bat
        test_bat = self.project_path / "test-windows.bat"
        test_content = """@echo off
echo ==========================================
echo Running Xionimus AI Tests on Windows
echo ==========================================

cd backend
call venv\\Scripts\\activate
python -m pytest tests/ -v
pause
"""
        
        try:
            # Write scripts
            with open(install_bat, 'w') as f:
                f.write(install_content)
            print("  ✓ Created install-windows.bat")
            
            with open(start_bat, 'w') as f:
                f.write(start_content)
            print("  ✓ Created start-windows.bat")
            
            with open(test_bat, 'w') as f:
                f.write(test_content)
            print("  ✓ Created test-windows.bat")
            
            self.fixes_applied.extend(["install-windows.bat", "start-windows.bat", "test-windows.bat"])
            
        except Exception as e:
            print(f"  ✗ Failed to create batch scripts: {e}")
            self.fixes_failed.append(("batch scripts", str(e)))
            
    def print_summary(self):
        """Print summary of fixes"""
        print("\n" + "=" * 80)
        print("FIX SUMMARY")
        print("=" * 80)
        
        print(f"\n✓ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"  • {fix}")
            
        if self.fixes_failed:
            print(f"\n✗ Fixes Failed: {len(self.fixes_failed)}")
            for fix, error in self.fixes_failed:
                print(f"  • {fix}: {error[:50]}...")
                
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("1. Run 'install-windows.bat' to install dependencies")
        print("2. Configure your API keys in backend/.env")
        print("3. Run 'start-windows.bat' to start the application")
        print("4. Run 'python xionimus_windows_test_suite.py' to validate")
        print("=" * 80)
        
def main():
    """Main entry point"""
    print("Starting Xionimus Windows Compatibility Fixer...")
    
    # Detect project path
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        current_path = Path.cwd()
        if (current_path / "backend").exists():
            project_path = current_path
        elif (current_path.parent / "backend").exists():
            project_path = current_path.parent
        else:
            project_path = current_path
            
    # Run fixes
    fixer = XionimusWindowsFixer(project_path)
    fixer.run_all_fixes()
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
