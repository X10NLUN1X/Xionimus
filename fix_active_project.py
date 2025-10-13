#!/usr/bin/env python3
"""
Active Project Auto-Set Fix
============================
Automatically sets the active project after GitHub import
so the AI can access the repository files.

Problem: After importing a repo, the session doesn't have an active project set.
Solution: Set the active project automatically after successful import.
"""

import os
import sys
import re
from pathlib import Path
from typing import Tuple

# Color codes for Windows CMD
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def apply_active_project_fix(file_path: Path) -> Tuple[bool, str]:
    """
    Apply the active project fix to github_pat.py
    Returns: (success, message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Check if fix is already applied
        content = ''.join(lines)
        if "# AUTO-SET ACTIVE PROJECT" in content:
            return True, "Fix already applied - no changes needed"
        
        # Find the line with "files_skipped += 1" after the copy exception
        # This is around line 1716 in the original file
        insertion_line = None
        for i, line in enumerate(lines):
            if 'files_skipped += 1' in line and i > 1700:
                # Check if previous lines contain the copy exception handler
                prev_lines = ''.join(lines[max(0, i-5):i])
                if 'Failed to copy' in prev_lines or 'shutil.copy2' in prev_lines:
                    insertion_line = i + 1
                    break
        
        if insertion_line is None:
            return False, "Could not find insertion point - looking for alternative..."
        
        # Get the indentation of the line
        indent = len(lines[insertion_line - 1]) - len(lines[insertion_line - 1].lstrip())
        indent_str = ' ' * indent
        
        # Create the fix code with proper indentation
        fix_code = f'''
{indent_str}# ==========================================
{indent_str}# AUTO-SET ACTIVE PROJECT AFTER IMPORT
{indent_str}# ==========================================
{indent_str}# This ensures the AI can access the imported repository files
{indent_str}try:
{indent_str}    # Find or create a session for this user
{indent_str}    from ..models.session_models import Session as SessionModel
{indent_str}    
{indent_str}    # Try to find the most recent session for this user
{indent_str}    session = db.query(SessionModel).filter(
{indent_str}        SessionModel.user_id == user_id
{indent_str}    ).order_by(SessionModel.updated_at.desc()).first()
{indent_str}    
{indent_str}    if session:
{indent_str}        # Set active project in the session
{indent_str}        session.active_project = {{
{indent_str}            'repo_owner': repo_owner,
{indent_str}            'repo_name': repo.name,
{indent_str}            'branch': branch_name,
{indent_str}            'workspace_path': workspace_dir,
{indent_str}            'import_date': datetime.now(timezone.utc).isoformat()
{indent_str}        }}
{indent_str}        db.commit()
{indent_str}        logger.info(f"✅ Active project set for session {{session.session_id}}: {{repo_owner}}/{{repo.name}}")
{indent_str}    else:
{indent_str}        logger.warning(f"⚠️ No session found for user {{user_id}} - active project not set")
{indent_str}except Exception as e:
{indent_str}    logger.error(f"Failed to set active project: {{e}}")
{indent_str}    # Don't fail the import if we can't set active project
{indent_str}    pass
{indent_str}# ==========================================

'''
        
        # Insert the fix code
        lines.insert(insertion_line, fix_code)
        
        # Create backup
        backup_path = file_path.with_suffix(file_path.suffix + '.before_active_project_fix')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Write fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        return True, f"Fix applied successfully at line {insertion_line} (backup: {backup_path.name})"
        
    except Exception as e:
        return False, f"Error applying fix: {e}"

def main():
    print_header("ACTIVE PROJECT AUTO-SET FIX")
    print_info("This fix automatically sets the active project after GitHub import")
    print_info("So the AI can immediately access the repository files")
    print()
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    print_info(f"Project root: {project_root}")
    
    # Verify project structure
    backend_dir = project_root / 'backend'
    if not backend_dir.exists():
        print_error("backend/ directory not found!")
        print_error(f"Current directory: {project_root}")
        return False
    
    # Find github_pat.py
    github_pat_file = backend_dir / 'app' / 'api' / 'github_pat.py'
    if not github_pat_file.exists():
        print_error(f"File not found: {github_pat_file}")
        return False
    
    print_success(f"Found: {github_pat_file}")
    print()
    
    # Apply fix
    print_header("APPLYING FIX")
    success, message = apply_active_project_fix(github_pat_file)
    
    if success:
        print_success(message)
        print()
        print_header("FIX APPLIED SUCCESSFULLY!")
        print()
        print_info("What changed:")
        print("  ✅ After GitHub import completes")
        print("  ✅ The active project is automatically set")
        print("  ✅ AI can now access repository files")
        print()
        print_info("Next steps:")
        print("  1. Restart backend: START.bat")
        print("  2. Import a repository in the UI")
        print("  3. The active project will be set automatically")
        print("  4. Chat with the AI about the repository!")
        print()
    else:
        print_error(message)
        print()
        print_warning("Fix could not be applied automatically")
        print_info("You may need to apply the fix manually")
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_warning("Fix cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
