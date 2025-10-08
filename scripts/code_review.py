#!/usr/bin/env python3
"""
Automated Code Review Script
Checks code quality, security issues, and best practices
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
import re


class CodeReviewer:
    """Automated code review checks"""
    
    def __init__(self, target_dir: str = "/app/backend/app"):
        self.target_dir = Path(target_dir)
        self.issues = []
        self.stats = {
            'files_checked': 0,
            'issues_found': 0,
            'critical': 0,
            'warning': 0,
            'info': 0
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all code review checks"""
        print("🔍 Starting Automated Code Review...")
        print(f"📂 Target Directory: {self.target_dir}\n")
        
        # Run checks
        self.check_bare_except_statements()
        self.check_sql_injection_risks()
        self.check_hardcoded_credentials()
        self.check_security_vulnerabilities()
        self.check_code_complexity()
        self.check_missing_docstrings()
        self.check_todos_and_fixmes()
        
        # Generate report
        return self.generate_report()
    
    def check_bare_except_statements(self):
        """Check for bare except statements"""
        print("🔎 Checking for bare except statements...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        self.stats['files_checked'] += len(python_files)
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Skip comments
                    if line.strip().startswith('#'):
                        continue
                    
                    # Check for bare except
                    if re.search(r'^\s*except\s*:\s*$', line):
                        self.add_issue(
                            severity='critical',
                            file=str(file_path.relative_to(self.target_dir)),
                            line=i,
                            issue='Bare except statement',
                            description='Use specific exception types instead of bare except:',
                            suggestion='except (SpecificError1, SpecificError2) as e:'
                        )
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked {len(python_files)} Python files\n")
    
    def check_sql_injection_risks(self):
        """Check for SQL injection vulnerabilities"""
        print("🔎 Checking for SQL injection risks...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        patterns = [
            (r'execute\(f"', 'F-string in SQL execute'),
            (r'execute\(".*\{', 'String formatting in SQL'),
            (r'execute\(.*\+.*\)', 'String concatenation in SQL'),
            (r'\.query\(f"', 'F-string in query'),
        ]
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in patterns:
                        if re.search(pattern, line):
                            self.add_issue(
                                severity='critical',
                                file=str(file_path.relative_to(self.target_dir)),
                                line=i,
                                issue='Potential SQL injection',
                                description=description,
                                suggestion='Use parameterized queries with placeholders'
                            )
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked SQL injection patterns\n")
    
    def check_hardcoded_credentials(self):
        """Check for hardcoded credentials"""
        print("🔎 Checking for hardcoded credentials...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        patterns = [
            (r'password\s*=\s*["\'](?!.*\{)[\w@!#$%^&*]+["\']', 'Hardcoded password'),
            (r'api_key\s*=\s*["\'](?!.*\{)[a-zA-Z0-9_-]{20,}["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'](?!.*\{)[\w-]{20,}["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'](?!.*\{)[a-zA-Z0-9_-]{20,}["\']', 'Hardcoded token'),
        ]
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Skip test files and examples
                    if 'test' in str(file_path).lower() or 'example' in line.lower():
                        continue
                    
                    for pattern, description in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.add_issue(
                                severity='critical',
                                file=str(file_path.relative_to(self.target_dir)),
                                line=i,
                                issue='Hardcoded credential',
                                description=description,
                                suggestion='Use environment variables or secrets management'
                            )
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked hardcoded credentials\n")
    
    def check_security_vulnerabilities(self):
        """Check for common security vulnerabilities"""
        print("🔎 Checking for security vulnerabilities...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        patterns = [
            (r'eval\(', 'Use of eval() - code injection risk'),
            (r'exec\(', 'Use of exec() - code injection risk'),
            (r'subprocess.*shell=True', 'Shell=True in subprocess - command injection risk'),
            (r'pickle\.loads?\(', 'Use of pickle - arbitrary code execution risk'),
            (r'yaml\.load\((?!.*Loader)', 'Unsafe YAML loading'),
        ]
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    for pattern, description in patterns:
                        if re.search(pattern, line):
                            self.add_issue(
                                severity='critical',
                                file=str(file_path.relative_to(self.target_dir)),
                                line=i,
                                issue='Security vulnerability',
                                description=description,
                                suggestion='Use safer alternatives or add input validation'
                            )
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked security patterns\n")
    
    def check_code_complexity(self):
        """Check for overly complex functions"""
        print("🔎 Checking code complexity...")
        
        # This would ideally use tools like radon or mccabe
        # For now, just check function length as a proxy
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                current_function = None
                function_start = 0
                indent_level = 0
                
                for i, line in enumerate(lines, 1):
                    # Detect function definition
                    if re.match(r'^\s*def\s+\w+\(', line):
                        # Save previous function if too long
                        if current_function and (i - function_start) > 150:
                            self.add_issue(
                                severity='warning',
                                file=str(file_path.relative_to(self.target_dir)),
                                line=function_start,
                                issue='Complex function',
                                description=f'Function {current_function} is {i - function_start} lines long',
                                suggestion='Consider breaking into smaller functions'
                            )
                        
                        current_function = line.split('def ')[1].split('(')[0]
                        function_start = i
                        indent_level = len(line) - len(line.lstrip())
            
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked code complexity\n")
    
    def check_missing_docstrings(self):
        """Check for missing docstrings"""
        print("🔎 Checking for missing docstrings...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # Check for function/class without docstring
                    if re.match(r'^\s*(def|class)\s+\w+', line):
                        # Look for docstring in next few lines
                        has_docstring = False
                        for j in range(i, min(i + 5, len(lines))):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                has_docstring = True
                                break
                        
                        if not has_docstring and not line.strip().startswith('_'):
                            func_name = line.split()[1].split('(')[0]
                            self.add_issue(
                                severity='info',
                                file=str(file_path.relative_to(self.target_dir)),
                                line=i,
                                issue='Missing docstring',
                                description=f'Function/class {func_name} has no docstring',
                                suggestion='Add docstring to describe purpose and parameters'
                            )
            
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked docstrings\n")
    
    def check_todos_and_fixmes(self):
        """Check for TODO and FIXME comments"""
        print("🔎 Checking for TODOs and FIXMEs...")
        
        python_files = list(self.target_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                        comment = line.split('#')[1].strip()
                        self.add_issue(
                            severity='info',
                            file=str(file_path.relative_to(self.target_dir)),
                            line=i,
                            issue='Action item',
                            description=comment,
                            suggestion='Address or remove this comment'
                        )
            
            except Exception as e:
                print(f"  ⚠️  Error checking {file_path}: {e}")
        
        print(f"  ✓ Checked action items\n")
    
    def add_issue(self, severity: str, file: str, line: int, issue: str, description: str, suggestion: str):
        """Add an issue to the list"""
        self.issues.append({
            'severity': severity,
            'file': file,
            'line': line,
            'issue': issue,
            'description': description,
            'suggestion': suggestion
        })
        self.stats['issues_found'] += 1
        self.stats[severity] += 1
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate review report"""
        print("=" * 80)
        print("📊 CODE REVIEW REPORT")
        print("=" * 80)
        
        print(f"\n📈 Statistics:")
        print(f"  Files Checked: {self.stats['files_checked']}")
        print(f"  Issues Found: {self.stats['issues_found']}")
        print(f"    🔴 Critical: {self.stats['critical']}")
        print(f"    🟡 Warning: {self.stats['warning']}")
        print(f"    🔵 Info: {self.stats['info']}")
        
        # Group issues by severity
        critical = [i for i in self.issues if i['severity'] == 'critical']
        warnings = [i for i in self.issues if i['severity'] == 'warning']
        info = [i for i in self.issues if i['severity'] == 'info']
        
        if critical:
            print(f"\n🔴 CRITICAL ISSUES ({len(critical)}):")
            for issue in critical[:10]:  # Show first 10
                print(f"  [{issue['file']}:{issue['line']}] {issue['issue']}")
                print(f"     {issue['description']}")
                print(f"     💡 {issue['suggestion']}\n")
        
        if warnings:
            print(f"\n🟡 WARNINGS ({len(warnings)}):")
            for issue in warnings[:5]:  # Show first 5
                print(f"  [{issue['file']}:{issue['line']}] {issue['issue']}")
                print(f"     {issue['description']}\n")
        
        # Overall grade
        if self.stats['critical'] == 0 and self.stats['warning'] < 5:
            grade = "A"
            emoji = "🌟"
        elif self.stats['critical'] == 0 and self.stats['warning'] < 20:
            grade = "B"
            emoji = "👍"
        elif self.stats['critical'] < 3:
            grade = "C"
            emoji = "⚠️"
        else:
            grade = "D"
            emoji = "🚨"
        
        print(f"\n{emoji} Overall Grade: {grade}")
        print("=" * 80)
        
        return {
            'stats': self.stats,
            'issues': self.issues,
            'grade': grade
        }


def main():
    """Main entry point"""
    reviewer = CodeReviewer()
    report = reviewer.run_all_checks()
    
    # Save report to file
    report_path = "/app/backend/code_review_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: {report_path}")
    
    # Exit with error code if critical issues found
    if report['stats']['critical'] > 0:
        print("\n❌ Critical issues found! Please fix before proceeding.")
        sys.exit(1)
    else:
        print("\n✅ No critical issues found!")
        sys.exit(0)


if __name__ == "__main__":
    main()
