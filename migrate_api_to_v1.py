#!/usr/bin/env python3
"""
API Migration Script - Migriert alle API-Calls zu /api/v1/
=========================================================
Migrates all API endpoints from /api/ to /api/v1/ in the Xionimus project
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

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

# Files to migrate
FILES_TO_MIGRATE = {
    'backend': [
        'server_launcher.py',  # Might have logging/validation
    ],
    'frontend/src/components': [
        'ActiveProjectBadge.tsx',
        'ContextWarningBanner.tsx',
        'FileUploadDialog.tsx',
        'GitHubImportDialog.tsx',
        'GitHubPushDialog.tsx',
        'SessionForkDialog.tsx',
        'TokenUsageWidget.tsx',
    ],
    'frontend/src/contexts': [
        'GitHubContext.tsx',
    ],
    'frontend/src/services': [
        'githubOAuthService.ts',
    ],
}

# API endpoint patterns to migrate
API_PATTERNS = [
    # GitHub endpoints
    (r'`\${BACKEND_URL}/api/github/', r'`${BACKEND_URL}/api/v1/github/'),
    (r'`\${BACKEND_URL}/api/github-pat/', r'`${BACKEND_URL}/api/v1/github-pat/'),
    
    # Session endpoints
    (r'`\${BACKEND_URL}/api/sessions/', r'`${BACKEND_URL}/api/v1/sessions/'),
    
    # File endpoints
    (r'`\${BACKEND_URL}/api/files/', r'`${BACKEND_URL}/api/v1/files/'),
    
    # Token endpoints
    (r'`\${BACKEND_URL}/api/tokens/', r'`${BACKEND_URL}/api/v1/tokens/'),
    
    # Workspace endpoints
    (r'`\${BACKEND_URL}/api/workspace/', r'`${BACKEND_URL}/api/v1/workspace/'),
    
    # Generic pattern (catch-all)
    (r'`\${BACKEND_URL}/api/(?!v1/)([a-z-]+)', r'`${BACKEND_URL}/api/v1/\1'),
]

def migrate_file(file_path: Path) -> Tuple[bool, int]:
    """
    Migrate a single file
    Returns: (success, num_changes)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = 0
        
        # Apply all API patterns
        for old_pattern, new_pattern in API_PATTERNS:
            new_content, count = re.subn(old_pattern, new_pattern, content)
            if count > 0:
                content = new_content
                changes += count
        
        # Only write if changes were made
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write migrated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, changes
        
        return True, 0
        
    except Exception as e:
        print_error(f"Error migrating {file_path}: {e}")
        return False, 0

def main():
    print_header("API V1 MIGRATION SCRIPT")
    print_info("This script will migrate all API calls from /api/ to /api/v1/")
    print()
    
    # Get project root
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()
    
    print_info(f"Project root: {project_root}")
    
    # Verify project structure
    if not (project_root / 'backend').exists() or not (project_root / 'frontend').exists():
        print_error("Invalid project structure! Expected backend/ and frontend/ directories.")
        print_error(f"Current directory: {project_root}")
        return False
    
    total_files = 0
    total_changes = 0
    failed_files = []
    
    # Migrate backend files
    print_header("MIGRATING BACKEND FILES")
    for file_name in FILES_TO_MIGRATE['backend']:
        file_path = project_root / 'backend' / file_name
        if file_path.exists():
            print_info(f"Processing: {file_name}")
            success, changes = migrate_file(file_path)
            if success:
                if changes > 0:
                    print_success(f"  ✓ Migrated {changes} API call(s)")
                    total_changes += changes
                else:
                    print_warning(f"  → No changes needed")
                total_files += 1
            else:
                failed_files.append(str(file_path))
        else:
            print_warning(f"File not found: {file_name}")
    
    # Migrate frontend components
    print_header("MIGRATING FRONTEND COMPONENTS")
    for file_name in FILES_TO_MIGRATE['frontend/src/components']:
        file_path = project_root / 'frontend' / 'src' / 'components' / file_name
        if file_path.exists():
            print_info(f"Processing: {file_name}")
            success, changes = migrate_file(file_path)
            if success:
                if changes > 0:
                    print_success(f"  ✓ Migrated {changes} API call(s)")
                    total_changes += changes
                else:
                    print_warning(f"  → No changes needed")
                total_files += 1
            else:
                failed_files.append(str(file_path))
        else:
            print_warning(f"File not found: {file_name}")
    
    # Migrate frontend contexts
    print_header("MIGRATING FRONTEND CONTEXTS")
    for file_name in FILES_TO_MIGRATE['frontend/src/contexts']:
        file_path = project_root / 'frontend' / 'src' / 'contexts' / file_name
        if file_path.exists():
            print_info(f"Processing: {file_name}")
            success, changes = migrate_file(file_path)
            if success:
                if changes > 0:
                    print_success(f"  ✓ Migrated {changes} API call(s)")
                    total_changes += changes
                else:
                    print_warning(f"  → No changes needed")
                total_files += 1
            else:
                failed_files.append(str(file_path))
        else:
            print_warning(f"File not found: {file_name}")
    
    # Migrate frontend services
    print_header("MIGRATING FRONTEND SERVICES")
    for file_name in FILES_TO_MIGRATE['frontend/src/services']:
        file_path = project_root / 'frontend' / 'src' / 'services' / file_name
        if file_path.exists():
            print_info(f"Processing: {file_name}")
            success, changes = migrate_file(file_path)
            if success:
                if changes > 0:
                    print_success(f"  ✓ Migrated {changes} API call(s)")
                    total_changes += changes
                else:
                    print_warning(f"  → No changes needed")
                total_files += 1
            else:
                failed_files.append(str(file_path))
        else:
            print_warning(f"File not found: {file_name}")
    
    # Print summary
    print_header("MIGRATION SUMMARY")
    print(f"Files processed: {total_files}")
    print(f"Total API calls migrated: {total_changes}")
    
    if failed_files:
        print_error(f"Failed files: {len(failed_files)}")
        for file in failed_files:
            print_error(f"  - {file}")
        return False
    
    if total_changes > 0:
        print_success("Migration completed successfully!")
        print()
        print_info("Backups created with .backup extension")
        print_info("Next steps:")
        print("  1. Test the application")
        print("  2. Commit changes: git add . && git commit -m 'feat: Migrate to /api/v1/ endpoints'")
        print("  3. Push to GitHub: git push origin main")
    else:
        print_warning("No changes were needed - all files already use /api/v1/")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_warning("Migration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
