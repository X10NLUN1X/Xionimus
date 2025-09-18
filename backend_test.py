#!/usr/bin/env python3
"""
Docker Yarn.lock Fix Validation Script
Tests Docker configuration, yarn.lock fix, and validates build process
"""

import os
import sys
import subprocess
import json
import yaml
import requests
from pathlib import Path
import time

class DockerTester:
    def __init__(self):
        self.root_dir = Path("/app")
        self.results = {
            "docker_environment": {},
            "dockerfile_validation": {},
            "compose_validation": {},
            "build_tests": {},
            "dependency_checks": {},
            "configuration_issues": [],
            "recommendations": []
        }
    
    def run_command(self, command, capture_output=True, timeout=30):
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=capture_output, 
                text=True, 
                timeout=timeout,
                cwd=self.root_dir
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_docker_environment(self):
        """Test Docker installation and availability"""
        print("🔍 Testing Docker Environment...")
        
        # Check if Docker is installed
        docker_version = self.run_command("docker --version")
        self.results["docker_environment"]["docker_installed"] = docker_version["success"]
        self.results["docker_environment"]["docker_version"] = docker_version["stdout"] if docker_version["success"] else docker_version["stderr"]
        
        # Check if Docker Compose is available
        compose_version = self.run_command("docker-compose --version")
        self.results["docker_environment"]["compose_installed"] = compose_version["success"]
        self.results["docker_environment"]["compose_version"] = compose_version["stdout"] if compose_version["success"] else compose_version["stderr"]
        
        # Check Docker daemon status
        docker_info = self.run_command("docker info")
        self.results["docker_environment"]["docker_running"] = docker_info["success"]
        self.results["docker_environment"]["docker_info"] = docker_info["stderr"] if not docker_info["success"] else "Docker daemon is running"
        
        # Check for Docker Desktop on Windows (common issue)
        if not docker_info["success"] and "pipe/dockerDesktopLinuxEngine" in docker_info["stderr"]:
            self.results["configuration_issues"].append({
                "type": "CRITICAL",
                "component": "Docker Desktop",
                "issue": "Docker Desktop Linux Engine connection failed",
                "description": "The error suggests Docker Desktop is not running or has connectivity issues",
                "solution": "Start Docker Desktop and ensure it's properly initialized"
            })
        
        if not docker_version["success"]:
            self.results["configuration_issues"].append({
                "type": "CRITICAL",
                "component": "Docker Installation",
                "issue": "Docker is not installed or not in PATH",
                "description": "Docker command not found",
                "solution": "Install Docker Desktop or Docker Engine"
            })
    
    def validate_dockerfiles(self):
        """Validate Dockerfile syntax and dependencies"""
        print("📋 Validating Dockerfiles...")
        
        # Backend Dockerfile
        backend_dockerfile = self.root_dir / "backend" / "Dockerfile"
        if backend_dockerfile.exists():
            with open(backend_dockerfile, 'r') as f:
                content = f.read()
            
            self.results["dockerfile_validation"]["backend"] = {
                "exists": True,
                "issues": []
            }
            
            # Check for common issues
            if "COPY requirements.txt" not in content:
                self.results["dockerfile_validation"]["backend"]["issues"].append(
                    "Missing requirements.txt copy step"
                )
            
            if "pip install" not in content:
                self.results["dockerfile_validation"]["backend"]["issues"].append(
                    "Missing pip install step"
                )
            
            # Check if requirements.txt exists
            requirements_file = self.root_dir / "backend" / "requirements.txt"
            if not requirements_file.exists():
                self.results["configuration_issues"].append({
                    "type": "CRITICAL",
                    "component": "Backend Dependencies",
                    "issue": "requirements.txt not found",
                    "description": "Backend Dockerfile references requirements.txt but file doesn't exist",
                    "solution": "Create requirements.txt with necessary Python dependencies"
                })
        else:
            self.results["dockerfile_validation"]["backend"] = {
                "exists": False,
                "issues": ["Backend Dockerfile not found"]
            }
        
        # Frontend Dockerfile
        frontend_dockerfile = self.root_dir / "frontend" / "Dockerfile"
        if frontend_dockerfile.exists():
            with open(frontend_dockerfile, 'r') as f:
                content = f.read()
            
            self.results["dockerfile_validation"]["frontend"] = {
                "exists": True,
                "issues": []
            }
            
            # Check for common issues
            if "package.json" not in content:
                self.results["dockerfile_validation"]["frontend"]["issues"].append(
                    "Missing package.json copy step"
                )
            
            if "yarn install" not in content and "npm install" not in content:
                self.results["dockerfile_validation"]["frontend"]["issues"].append(
                    "Missing dependency installation step"
                )
            
            # Check if package.json exists
            package_file = self.root_dir / "frontend" / "package.json"
            if not package_file.exists():
                self.results["configuration_issues"].append({
                    "type": "CRITICAL",
                    "component": "Frontend Dependencies",
                    "issue": "package.json not found",
                    "description": "Frontend Dockerfile references package.json but file doesn't exist",
                    "solution": "Create package.json with necessary Node.js dependencies"
                })
            
            # Check for yarn.lock
            yarn_lock = self.root_dir / "frontend" / "yarn.lock"
            if "yarn install" in content and not yarn_lock.exists():
                self.results["dockerfile_validation"]["frontend"]["issues"].append(
                    "yarn.lock not found but yarn install is used"
                )
        else:
            self.results["dockerfile_validation"]["frontend"] = {
                "exists": False,
                "issues": ["Frontend Dockerfile not found"]
            }
    
    def validate_compose_files(self):
        """Validate docker-compose configuration"""
        print("🔧 Validating Docker Compose files...")
        
        compose_files = [
            "docker-compose.yml",
            "docker-compose.build.yml"
        ]
        
        for compose_file in compose_files:
            file_path = self.root_dir / compose_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        compose_config = yaml.safe_load(f)
                    
                    self.results["compose_validation"][compose_file] = {
                        "valid_yaml": True,
                        "issues": []
                    }
                    
                    # Check for common issues
                    if "services" not in compose_config:
                        self.results["compose_validation"][compose_file]["issues"].append(
                            "No services defined"
                        )
                    else:
                        services = compose_config["services"]
                        
                        # Check backend service
                        if "backend" in services:
                            backend_service = services["backend"]
                            
                            # Check image vs build configuration
                            if compose_file == "docker-compose.yml":
                                if "image" in backend_service and "build" not in backend_service:
                                    # This is the issue - trying to use pre-built image that doesn't exist
                                    if backend_service["image"] == "xionimus-backend":
                                        self.results["configuration_issues"].append({
                                            "type": "CRITICAL",
                                            "component": "Docker Compose",
                                            "issue": "Backend service references non-existent image",
                                            "description": f"docker-compose.yml tries to use image 'xionimus-backend' which doesn't exist",
                                            "solution": "Either build the image first using build-docker.sh or use docker-compose.build.yml"
                                        })
                            
                            # Check environment variables
                            if "environment" in backend_service:
                                env_vars = backend_service["environment"]
                                if isinstance(env_vars, list):
                                    env_dict = {}
                                    for env in env_vars:
                                        if "=" in env:
                                            key, value = env.split("=", 1)
                                            env_dict[key] = value
                                else:
                                    env_dict = env_vars
                                
                                # Check MongoDB URL
                                if "MONGO_URL" in env_dict:
                                    mongo_url = env_dict["MONGO_URL"]
                                    if "localhost" in mongo_url:
                                        self.results["configuration_issues"].append({
                                            "type": "WARNING",
                                            "component": "Backend Configuration",
                                            "issue": "MongoDB URL uses localhost in Docker context",
                                            "description": "Backend service uses localhost for MongoDB, should use service name",
                                            "solution": "Use 'mongodb://mongodb:27017' instead of localhost"
                                        })
                        
                        # Check frontend service
                        if "frontend" in services:
                            frontend_service = services["frontend"]
                            
                            if "image" in frontend_service and "build" not in frontend_service:
                                if frontend_service["image"] == "xionimus-frontend":
                                    self.results["configuration_issues"].append({
                                        "type": "CRITICAL",
                                        "component": "Docker Compose",
                                        "issue": "Frontend service references non-existent image",
                                        "description": f"docker-compose.yml tries to use image 'xionimus-frontend' which doesn't exist",
                                        "solution": "Either build the image first using build-docker.sh or use docker-compose.build.yml"
                                    })
                
                except yaml.YAMLError as e:
                    self.results["compose_validation"][compose_file] = {
                        "valid_yaml": False,
                        "issues": [f"YAML syntax error: {str(e)}"]
                    }
            else:
                self.results["compose_validation"][compose_file] = {
                    "exists": False,
                    "issues": [f"{compose_file} not found"]
                }
    
    def test_build_scripts(self):
        """Test build scripts"""
        print("🛠️ Testing build scripts...")
        
        build_scripts = [
            "build-docker.sh",
            "build-docker.bat"
        ]
        
        for script in build_scripts:
            script_path = self.root_dir / script
            if script_path.exists():
                self.results["build_tests"][script] = {
                    "exists": True,
                    "executable": os.access(script_path, os.X_OK),
                    "issues": []
                }
                
                # Read script content for analysis
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Check for common issues
                if "docker build" not in content:
                    self.results["build_tests"][script]["issues"].append(
                        "Script doesn't contain docker build commands"
                    )
                
                if "docker-compose up" not in content:
                    self.results["build_tests"][script]["issues"].append(
                        "Script doesn't start services with docker-compose"
                    )
            else:
                self.results["build_tests"][script] = {
                    "exists": False,
                    "issues": [f"{script} not found"]
                }
    
    def check_dependencies(self):
        """Check dependency files"""
        print("📦 Checking dependencies...")
        
        # Backend requirements
        requirements_file = self.root_dir / "backend" / "requirements.txt"
        if requirements_file.exists():
            self.results["dependency_checks"]["backend_requirements"] = {
                "exists": True,
                "issues": []
            }
            
            # Try to validate requirements
            try:
                with open(requirements_file, 'r') as f:
                    requirements = f.read()
                
                # Check for problematic dependencies
                if "emergentintegrations" in requirements:
                    self.results["dependency_checks"]["backend_requirements"]["issues"].append(
                        "Custom package 'emergentintegrations' may not be available in Docker build"
                    )
            except Exception as e:
                self.results["dependency_checks"]["backend_requirements"]["issues"].append(
                    f"Error reading requirements.txt: {str(e)}"
                )
        else:
            self.results["dependency_checks"]["backend_requirements"] = {
                "exists": False,
                "issues": ["requirements.txt not found"]
            }
        
        # Frontend package.json
        package_file = self.root_dir / "frontend" / "package.json"
        if package_file.exists():
            self.results["dependency_checks"]["frontend_package"] = {
                "exists": True,
                "issues": []
            }
            
            try:
                with open(package_file, 'r') as f:
                    package_data = json.load(f)
                
                # Check for scripts
                if "scripts" not in package_data:
                    self.results["dependency_checks"]["frontend_package"]["issues"].append(
                        "No scripts section in package.json"
                    )
                else:
                    scripts = package_data["scripts"]
                    if "start" not in scripts:
                        self.results["dependency_checks"]["frontend_package"]["issues"].append(
                            "No start script defined"
                        )
                    elif "craco" in scripts["start"]:
                        # Check if craco config exists
                        craco_config = self.root_dir / "frontend" / "craco.config.js"
                        if not craco_config.exists():
                            self.results["dependency_checks"]["frontend_package"]["issues"].append(
                                "Uses craco but craco.config.js not found"
                            )
            except Exception as e:
                self.results["dependency_checks"]["frontend_package"]["issues"].append(
                    f"Error reading package.json: {str(e)}"
                )
        else:
            self.results["dependency_checks"]["frontend_package"] = {
                "exists": False,
                "issues": ["package.json not found"]
            }
    
    def generate_recommendations(self):
        """Generate recommendations based on findings"""
        print("💡 Generating recommendations...")
        
        # Docker not available
        if not self.results["docker_environment"]["docker_installed"]:
            self.results["recommendations"].append({
                "priority": "CRITICAL",
                "title": "Install Docker",
                "description": "Docker is not installed or not available in PATH",
                "action": "Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)"
            })
        
        # Docker not running
        if self.results["docker_environment"]["docker_installed"] and not self.results["docker_environment"]["docker_running"]:
            self.results["recommendations"].append({
                "priority": "CRITICAL",
                "title": "Start Docker Service",
                "description": "Docker is installed but not running",
                "action": "Start Docker Desktop or Docker daemon service"
            })
        
        # Image reference issues
        critical_issues = [issue for issue in self.results["configuration_issues"] if issue["type"] == "CRITICAL"]
        if critical_issues:
            for issue in critical_issues:
                if "non-existent image" in issue["issue"]:
                    self.results["recommendations"].append({
                        "priority": "HIGH",
                        "title": "Fix Docker Compose Image References",
                        "description": issue["description"],
                        "action": issue["solution"]
                    })
        
        # Build process recommendations
        if self.results["docker_environment"]["docker_installed"]:
            self.results["recommendations"].append({
                "priority": "HIGH",
                "title": "Use Build-First Approach",
                "description": "Build images before running docker-compose",
                "action": "Run ./build-docker.sh (Linux/Mac) or build-docker.bat (Windows) first, then docker-compose up -d"
            })
            
            self.results["recommendations"].append({
                "priority": "MEDIUM",
                "title": "Alternative: Use Build Compose File",
                "description": "Use docker-compose file with build configuration",
                "action": "Run: docker-compose -f docker-compose.build.yml up -d --build"
            })
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Docker Setup Testing and Debugging...")
        print("=" * 60)
        
        self.test_docker_environment()
        self.validate_dockerfiles()
        self.validate_compose_files()
        self.test_build_scripts()
        self.check_dependencies()
        self.generate_recommendations()
        
        return self.results
    
    def print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("🔍 DOCKER SETUP TEST RESULTS")
        print("=" * 60)
        
        # Docker Environment
        print("\n🐳 Docker Environment:")
        env = self.results["docker_environment"]
        print(f"  Docker Installed: {'✅' if env['docker_installed'] else '❌'}")
        print(f"  Docker Running: {'✅' if env['docker_running'] else '❌'}")
        print(f"  Compose Available: {'✅' if env['compose_installed'] else '❌'}")
        
        if not env['docker_installed']:
            print(f"  Error: {env['docker_version']}")
        if not env['docker_running']:
            print(f"  Error: {env['docker_info']}")
        
        # Configuration Issues
        if self.results["configuration_issues"]:
            print(f"\n⚠️ Configuration Issues Found: {len(self.results['configuration_issues'])}")
            for issue in self.results["configuration_issues"]:
                icon = "🔴" if issue["type"] == "CRITICAL" else "🟡"
                print(f"  {icon} {issue['component']}: {issue['issue']}")
                print(f"     Solution: {issue['solution']}")
        
        # Recommendations
        if self.results["recommendations"]:
            print(f"\n💡 Recommendations ({len(self.results['recommendations'])}):")
            for rec in self.results["recommendations"]:
                priority_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                icon = priority_icon.get(rec["priority"], "ℹ️")
                print(f"  {icon} {rec['title']}")
                print(f"     {rec['description']}")
                print(f"     Action: {rec['action']}")
        
        # Summary
        print(f"\n📊 Summary:")
        critical_count = len([i for i in self.results["configuration_issues"] if i["type"] == "CRITICAL"])
        warning_count = len([i for i in self.results["configuration_issues"] if i["type"] == "WARNING"])
        
        if critical_count == 0 and warning_count == 0:
            print("  ✅ No critical issues found")
        else:
            print(f"  🔴 Critical Issues: {critical_count}")
            print(f"  🟡 Warnings: {warning_count}")
        
        print("\n" + "=" * 60)

def main():
    """Main function"""
    tester = DockerTester()
    results = tester.run_all_tests()
    tester.print_results()
    
    # Return exit code based on results
    critical_issues = len([i for i in results["configuration_issues"] if i["type"] == "CRITICAL"])
    if critical_issues > 0 or not results["docker_environment"]["docker_installed"]:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())