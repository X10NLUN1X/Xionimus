#!/usr/bin/env python3
"""
Docker Yarn.lock Fix Validation Script
Tests the specific yarn.lock fix and Docker configuration validation
"""

import os
import sys
import json
import yaml
from pathlib import Path

class YarnLockFixValidator:
    def __init__(self):
        self.root_dir = Path("/app")
        self.results = {
            "yarn_lock_fix": {},
            "dockerfile_validation": {},
            "build_scripts": {},
            "package_compatibility": {},
            "test_summary": {
                "total_tests": 8,
                "passed": 0,
                "failed": 0,
                "warnings": 0
            }
        }
    
    def test_yarn_lock_location(self):
        """Test 1: Verify yarn.lock Fix - Confirm only /app/frontend/yarn.lock exists and root yarn.lock is removed"""
        print("🔍 Test 1: Validating yarn.lock file locations...")
        
        # Check root yarn.lock should NOT exist
        root_yarn_lock = self.root_dir / "yarn.lock"
        frontend_yarn_lock = self.root_dir / "frontend" / "yarn.lock"
        
        root_exists = root_yarn_lock.exists()
        frontend_exists = frontend_yarn_lock.exists()
        
        self.results["yarn_lock_fix"]["root_yarn_lock_removed"] = not root_exists
        self.results["yarn_lock_fix"]["frontend_yarn_lock_exists"] = frontend_exists
        
        if not root_exists and frontend_exists:
            print("  ✅ PASS: Root yarn.lock removed, frontend yarn.lock exists")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print(f"  ❌ FAIL: Root yarn.lock exists: {root_exists}, Frontend yarn.lock exists: {frontend_exists}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_dockerfile_yarn_pattern(self):
        """Test 2: Validate Dockerfile COPY instruction uses 'yarn.lock*' pattern"""
        print("🔍 Test 2: Validating Dockerfile yarn.lock* pattern...")
        
        dockerfile_path = self.root_dir / "frontend" / "Dockerfile"
        if not dockerfile_path.exists():
            print("  ❌ FAIL: Frontend Dockerfile not found")
            self.results["test_summary"]["failed"] += 1
            return False
        
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for yarn.lock* pattern
        has_yarn_pattern = "yarn.lock*" in content
        
        self.results["dockerfile_validation"]["yarn_lock_pattern"] = has_yarn_pattern
        
        if has_yarn_pattern:
            print("  ✅ PASS: Dockerfile uses 'yarn.lock*' pattern for optional yarn.lock copy")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print("  ❌ FAIL: Dockerfile does not use 'yarn.lock*' pattern")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_yarn_install_command(self):
        """Test 3: Verify yarn install command without --frozen-lockfile flag"""
        print("🔍 Test 3: Validating yarn install command...")
        
        dockerfile_path = self.root_dir / "frontend" / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check yarn install command
        has_yarn_install = "yarn install" in content
        has_frozen_lockfile = "--frozen-lockfile" in content
        
        self.results["dockerfile_validation"]["yarn_install_present"] = has_yarn_install
        self.results["dockerfile_validation"]["no_frozen_lockfile"] = not has_frozen_lockfile
        
        if has_yarn_install and not has_frozen_lockfile:
            print("  ✅ PASS: yarn install command present without --frozen-lockfile flag")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print(f"  ❌ FAIL: yarn install: {has_yarn_install}, frozen-lockfile: {has_frozen_lockfile}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_build_scripts_no_cache(self):
        """Test 4: Verify build scripts include --no-cache flag"""
        print("🔍 Test 4: Validating build scripts --no-cache flag...")
        
        scripts = ["build-docker.sh", "build-docker.bat"]
        all_have_no_cache = True
        
        for script_name in scripts:
            script_path = self.root_dir / script_name
            if script_path.exists():
                with open(script_path, 'r') as f:
                    content = f.read()
                
                has_no_cache = "--no-cache" in content
                self.results["build_scripts"][script_name] = {
                    "exists": True,
                    "has_no_cache": has_no_cache
                }
                
                if not has_no_cache:
                    all_have_no_cache = False
                    print(f"  ⚠️  WARNING: {script_name} missing --no-cache flag")
            else:
                self.results["build_scripts"][script_name] = {
                    "exists": False,
                    "has_no_cache": False
                }
                all_have_no_cache = False
        
        if all_have_no_cache:
            print("  ✅ PASS: Build scripts include --no-cache flag")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print("  ❌ FAIL: Some build scripts missing --no-cache flag")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_package_json_compatibility(self):
        """Test 5: Verify package.json and yarn.lock compatibility"""
        print("🔍 Test 5: Validating package.json and yarn.lock compatibility...")
        
        package_path = self.root_dir / "frontend" / "package.json"
        yarn_lock_path = self.root_dir / "frontend" / "yarn.lock"
        
        if not package_path.exists():
            print("  ❌ FAIL: package.json not found")
            self.results["test_summary"]["failed"] += 1
            return False
        
        if not yarn_lock_path.exists():
            print("  ❌ FAIL: yarn.lock not found")
            self.results["test_summary"]["failed"] += 1
            return False
        
        # Check package.json structure
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        has_dependencies = "dependencies" in package_data
        has_scripts = "scripts" in package_data
        has_package_manager = "packageManager" in package_data
        
        # Check yarn.lock structure
        with open(yarn_lock_path, 'r') as f:
            yarn_content = f.read()
        
        is_valid_yarn_lock = yarn_content.startswith("# THIS IS AN AUTOGENERATED FILE")
        
        self.results["package_compatibility"] = {
            "package_json_valid": has_dependencies and has_scripts,
            "yarn_lock_valid": is_valid_yarn_lock,
            "package_manager_specified": has_package_manager
        }
        
        if has_dependencies and has_scripts and is_valid_yarn_lock:
            print("  ✅ PASS: package.json and yarn.lock are compatible")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print("  ❌ FAIL: package.json or yarn.lock compatibility issues")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_docker_compose_build_context(self):
        """Test 6: Verify frontend build context can access yarn.lock properly"""
        print("🔍 Test 6: Validating Docker Compose build context...")
        
        compose_path = self.root_dir / "docker-compose.yml"
        if not compose_path.exists():
            print("  ❌ FAIL: docker-compose.yml not found")
            self.results["test_summary"]["failed"] += 1
            return False
        
        with open(compose_path, 'r') as f:
            compose_config = yaml.safe_load(f)
        
        if "services" not in compose_config or "frontend" not in compose_config["services"]:
            print("  ❌ FAIL: Frontend service not found in docker-compose.yml")
            self.results["test_summary"]["failed"] += 1
            return False
        
        frontend_service = compose_config["services"]["frontend"]
        
        # Check build context
        has_build_context = "build" in frontend_service
        if has_build_context:
            build_config = frontend_service["build"]
            if isinstance(build_config, dict):
                context = build_config.get("context", "")
            else:
                context = build_config
            
            correct_context = context == "./frontend"
        else:
            correct_context = False
        
        if has_build_context and correct_context:
            print("  ✅ PASS: Frontend build context properly configured")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print("  ❌ FAIL: Frontend build context issues")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_craco_configuration(self):
        """Test 7: Verify craco configuration exists since package.json uses craco"""
        print("🔍 Test 7: Validating craco configuration...")
        
        package_path = self.root_dir / "frontend" / "package.json"
        craco_config_path = self.root_dir / "frontend" / "craco.config.js"
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        uses_craco = False
        if "scripts" in package_data:
            scripts = package_data["scripts"]
            uses_craco = any("craco" in script for script in scripts.values())
        
        craco_config_exists = craco_config_path.exists()
        
        if uses_craco and craco_config_exists:
            print("  ✅ PASS: Craco configuration exists")
            self.results["test_summary"]["passed"] += 1
            return True
        elif not uses_craco:
            print("  ✅ PASS: Craco not used, no config needed")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print("  ❌ FAIL: Uses craco but craco.config.js not found")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def test_dockerfile_syntax_validation(self):
        """Test 8: Validate overall Dockerfile syntax and structure"""
        print("🔍 Test 8: Validating Dockerfile syntax and structure...")
        
        dockerfile_path = self.root_dir / "frontend" / "Dockerfile"
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check required instructions
        required_instructions = ["FROM", "WORKDIR", "COPY", "RUN", "EXPOSE", "CMD"]
        missing_instructions = []
        
        for instruction in required_instructions:
            if instruction not in content:
                missing_instructions.append(instruction)
        
        # Check specific patterns
        has_node_base = "FROM node:" in content
        has_workdir = "WORKDIR /app" in content
        has_expose = "EXPOSE 3000" in content
        
        syntax_valid = len(missing_instructions) == 0 and has_node_base and has_workdir and has_expose
        
        if syntax_valid:
            print("  ✅ PASS: Dockerfile syntax and structure valid")
            self.results["test_summary"]["passed"] += 1
            return True
        else:
            print(f"  ❌ FAIL: Dockerfile issues - Missing: {missing_instructions}")
            self.results["test_summary"]["failed"] += 1
            return False
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🚀 Starting Docker Yarn.lock Fix Validation...")
        print("=" * 60)
        
        tests = [
            self.test_yarn_lock_location,
            self.test_dockerfile_yarn_pattern,
            self.test_yarn_install_command,
            self.test_build_scripts_no_cache,
            self.test_package_json_compatibility,
            self.test_docker_compose_build_context,
            self.test_craco_configuration,
            self.test_dockerfile_syntax_validation
        ]
        
        for test in tests:
            test()
            print()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("📊 YARN.LOCK FIX VALIDATION SUMMARY")
        print("=" * 60)
        
        summary = self.results["test_summary"]
        total = summary["total_tests"]
        passed = summary["passed"]
        failed = summary["failed"]
        
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Yarn.lock fix is working correctly.")
            print("✅ Docker build should succeed without yarn.lock errors")
            print("✅ Frontend build context properly configured")
            print("✅ Build scripts include cache-busting flags")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Issues need to be addressed:")
            
            # Specific recommendations based on failures
            if not self.results["yarn_lock_fix"].get("root_yarn_lock_removed", True):
                print("🔧 Remove root /app/yarn.lock file")
            
            if not self.results["dockerfile_validation"].get("yarn_lock_pattern", True):
                print("🔧 Update Dockerfile to use 'COPY yarn.lock* ./' pattern")
            
            if not self.results["dockerfile_validation"].get("no_frozen_lockfile", True):
                print("🔧 Remove --frozen-lockfile flag from yarn install command")
        
        print("=" * 60)

def main():
    """Main function"""
    validator = YarnLockFixValidator()
    results = validator.run_all_tests()
    validator.print_summary()
    
    # Return exit code based on results
    failed_tests = results["test_summary"]["failed"]
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    sys.exit(main())