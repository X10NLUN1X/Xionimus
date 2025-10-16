"""
ULTRA-ROBUST Framework Detection
Findet Framework auch wenn Dateien in Unterverzeichnissen liegen

FEATURES:
- Rekursive Suche nach main.py, server.py, etc.
- Höhere Gewichtung für FastAPI
- Sucht in backend/, src/, app/ Unterverzeichnissen
- Robuster gegen False Positives

INSTALLATION:
    copy framework_detector_v3.py backend\app\core\framework_detector.py
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """
    Ultra-robust framework detection
    Searches recursively and weighs evidence intelligently
    """
    
    FRAMEWORK_SIGNATURES = {
        "fastapi": {
            "entry_files": ["main.py", "server.py", "app.py"],  # Possible entry points
            "imports": ["from fastapi import", "import fastapi"],
            "dependencies": ["fastapi", "uvicorn", "pydantic"],
            "patterns": [
                "@app.get", "@app.post", "@app.put", "@app.delete",
                "FastAPI(", "APIRouter(", "async def",
                "Depends(", "HTTPException", "WebSocket"
            ],
            "directories": ["app/api", "app/core", "api", "routers"],
            "min_score": 10  # Minimum score to be considered
        },
        "django": {
            "entry_files": ["manage.py", "wsgi.py"],
            "imports": ["from django", "import django"],
            "dependencies": ["django"],
            "patterns": [
                "INSTALLED_APPS", "urlpatterns", "django.db.models",
                "django.contrib", "settings.py"
            ],
            "directories": ["migrations"],
            "min_score": 20  # Higher threshold to reduce false positives
        },
        "flask": {
            "entry_files": ["app.py", "wsgi.py", "application.py"],
            "imports": ["from flask import", "import flask"],
            "dependencies": ["flask"],
            "patterns": ["@app.route", "Flask(__name__)"],
            "min_score": 10
        },
        "express": {
            "entry_files": ["server.js", "app.js", "index.js"],
            "dependencies": ["express"],
            "patterns": ["app.get(", "app.post(", "express()"],
            "min_score": 8
        },
        "nextjs": {
            "entry_files": ["next.config.js", "next.config.ts"],
            "directories": ["pages", "app"],
            "dependencies": ["next", "react"],
            "patterns": ["export default function"],
            "min_score": 8
        }
    }
    
    def __init__(self, project_path: str):
        """Initialize detector with project path"""
        self.project_path = Path(project_path)
        self.detected_framework = None
        self.confidence = 0.0
        self.evidence = []
        
        # Common subdirectories to search in
        self.search_dirs = [
            self.project_path,
            self.project_path / "backend",
            self.project_path / "src",
            self.project_path / "app",
            self.project_path / "server"
        ]
    
    def detect(self) -> Dict[str, any]:
        """Detect framework by analyzing project files"""
        if not self.project_path.exists():
            return {
                "framework": "unknown",
                "confidence": 0.0,
                "evidence": ["Project path does not exist"],
                "error": "Path not found"
            }
        
        scores = {}
        all_evidence = {}
        
        # Score each framework
        for framework, signatures in self.FRAMEWORK_SIGNATURES.items():
            score, evidence = self._score_framework(framework, signatures)
            
            # Apply minimum score threshold
            min_score = signatures.get("min_score", 0)
            if score < min_score:
                score = 0
                if score > 0:  # Only add warning if there was some score
                    evidence.append(f"⚠️ Score {score} below minimum {min_score}")
            
            scores[framework] = score
            all_evidence[framework] = evidence
        
        # Find highest scoring framework
        if scores:
            best_framework = max(scores, key=scores.get)
            best_score = scores[best_framework]
            
            if best_score > 0:
                # Calculate confidence (0-100%)
                # Max possible score is ~30, so normalize
                confidence = min(best_score * 3.33, 100.0)
                
                self.detected_framework = best_framework
                self.confidence = confidence / 100.0
                self.evidence = all_evidence[best_framework]
                
                return {
                    "framework": best_framework,
                    "confidence": round(confidence, 1),
                    "evidence": self.evidence,
                    "all_scores": scores
                }
        
        # No framework detected
        return {
            "framework": "unknown",
            "confidence": 0.0,
            "evidence": ["No clear framework indicators found"],
            "all_scores": scores
        }
    
    def _score_framework(self, framework: str, signatures: Dict) -> Tuple[int, List[str]]:
        """Score a framework based on its signatures"""
        score = 0
        evidence = []
        
        # 🔍 CHECK 1: Entry files (HIGHEST WEIGHT)
        if "entry_files" in signatures:
            for filename in signatures["entry_files"]:
                found_path = self._find_file_recursive(filename)
                if found_path:
                    score += 8  # Very high weight for entry files
                    rel_path = found_path.relative_to(self.project_path)
                    evidence.append(f"✅ Found {rel_path}")
                    
                    # Bonus: Check if file actually imports the framework
                    if self._file_contains_patterns(found_path, signatures.get("imports", [])):
                        score += 3  # Bonus for confirmed imports
                        evidence.append(f"✅ {rel_path} imports {framework}")
        
        # 🔍 CHECK 2: Dependencies (HIGH WEIGHT)
        if "dependencies" in signatures:
            deps_found = self._check_dependencies(signatures["dependencies"])
            score += len(deps_found) * 4  # Higher weight
            for dep in deps_found:
                evidence.append(f"✅ Dependency: {dep}")
        
        # 🔍 CHECK 3: Directories (MEDIUM WEIGHT)
        if "directories" in signatures:
            for dirname in signatures["directories"]:
                if self._directory_exists_recursive(dirname):
                    score += 3
                    evidence.append(f"✅ Found {dirname}/ directory")
        
        # 🔍 CHECK 4: Code patterns (MEDIUM WEIGHT)
        if "patterns" in signatures and "entry_files" in signatures:
            for filename in signatures["entry_files"]:
                found_path = self._find_file_recursive(filename)
                if found_path:
                    patterns_found = self._check_patterns_in_file(found_path, signatures["patterns"])
                    # Higher weight for FastAPI patterns
                    weight = 2 if framework == "fastapi" else 1
                    score += len(patterns_found) * weight
                    for pattern in patterns_found[:3]:  # Limit evidence items
                        evidence.append(f"✅ Pattern: {pattern}")
                    if len(patterns_found) > 3:
                        evidence.append(f"✅ ... and {len(patterns_found) - 3} more patterns")
        
        # 🔍 CHECK 5: Imports in ANY Python file (MEDIUM WEIGHT)
        if "imports" in signatures:
            imports_found = self._check_imports_recursive(signatures["imports"])
            score += min(len(imports_found), 3) * 3  # Cap at 3 files
            if imports_found:
                evidence.append(f"✅ {len(imports_found)} file(s) import {framework}")
        
        return score, evidence
    
    def _find_file_recursive(self, filename: str) -> Optional[Path]:
        """Find file in project (recursively in common subdirs)"""
        # Try direct path first
        if (self.project_path / filename).exists():
            return self.project_path / filename
        
        # Try common subdirectories
        for search_dir in self.search_dirs:
            if not search_dir.exists():
                continue
            
            # Try direct
            file_path = search_dir / filename
            if file_path.exists():
                return file_path
            
            # Try recursive search (but limit depth to 2 levels)
            try:
                for root, dirs, files in os.walk(search_dir):
                    # Limit depth
                    depth = len(Path(root).relative_to(search_dir).parts)
                    if depth > 2:
                        continue
                    
                    # Skip common ignore dirs
                    dirs[:] = [d for d in dirs if d not in 
                              ['venv', '.venv', '__pycache__', 'node_modules', '.git']]
                    
                    if filename in files:
                        return Path(root) / filename
            except Exception:
                continue
        
        return None
    
    def _directory_exists_recursive(self, dirname: str) -> bool:
        """Check if directory exists (search in subdirs)"""
        for search_dir in self.search_dirs:
            if not search_dir.exists():
                continue
            
            # Direct check
            if (search_dir / dirname).is_dir():
                return True
            
            # Recursive check (limit depth)
            try:
                for root, dirs, _ in os.walk(search_dir):
                    depth = len(Path(root).relative_to(search_dir).parts)
                    if depth > 2:
                        continue
                    
                    dirs[:] = [d for d in dirs if d not in 
                              ['venv', '.venv', '__pycache__', 'node_modules', '.git']]
                    
                    if dirname in dirs:
                        return True
            except Exception:
                continue
        
        return False
    
    def _check_dependencies(self, dependencies: List[str]) -> List[str]:
        """Check if dependencies are listed in package files"""
        found = set()
        
        # Python requirements files
        for req_file in ["requirements.txt", "backend/requirements.txt", "pyproject.toml"]:
            req_path = self.project_path / req_file
            if req_path.exists():
                try:
                    content = req_path.read_text(encoding='utf-8').lower()
                    for dep in dependencies:
                        if dep.lower() in content:
                            found.add(dep)
                except Exception:
                    pass
        
        # Node.js package files
        for pkg_file in ["package.json", "frontend/package.json"]:
            package_path = self.project_path / pkg_file
            if package_path.exists():
                try:
                    content = package_path.read_text(encoding='utf-8')
                    data = json.loads(content)
                    all_deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    for dep in dependencies:
                        if dep in all_deps:
                            found.add(dep)
                except Exception:
                    pass
        
        return list(found)
    
    def _check_patterns_in_file(self, file_path: Path, patterns: List[str]) -> List[str]:
        """Check if code patterns exist in file"""
        if not file_path.exists():
            return []
        
        found = []
        try:
            content = file_path.read_text(encoding='utf-8')
            for pattern in patterns:
                if pattern in content and pattern not in found:
                    found.append(pattern)
        except Exception:
            pass
        
        return found
    
    def _file_contains_patterns(self, file_path: Path, patterns: List[str]) -> bool:
        """Check if file contains any of the patterns"""
        if not file_path.exists():
            return False
        
        try:
            content = file_path.read_text(encoding='utf-8')
            return any(pattern in content for pattern in patterns)
        except Exception:
            return False
    
    def _check_imports_recursive(self, imports: List[str]) -> List[Path]:
        """Check if imports exist in Python files (limit search)"""
        found = []
        checked = 0
        max_files = 50  # Don't check too many files
        
        for search_dir in self.search_dirs:
            if not search_dir.exists():
                continue
            
            try:
                for py_file in search_dir.rglob("*.py"):
                    # Skip venv, cache, etc.
                    if any(skip in str(py_file) for skip in 
                          ['venv', '.venv', '__pycache__', 'node_modules', '.git']):
                        continue
                    
                    checked += 1
                    if checked > max_files:
                        break
                    
                    try:
                        content = py_file.read_text(encoding='utf-8')
                        if any(imp in content for imp in imports):
                            found.append(py_file)
                            if len(found) >= 5:  # Cap at 5 files
                                return found
                    except Exception:
                        continue
            except Exception:
                continue
            
            if checked > max_files:
                break
        
        return found
    
    def get_context_for_ai(self) -> str:
        """Generate context string for AI"""
        result = self.detect()
        
        if result["framework"] == "unknown":
            return """
⚠️ FRAMEWORK: UNKNOWN
═══════════════════════════════════════════════════════════════════════════
No clear framework detected. Analyze files carefully before making assumptions.
"""
        
        framework = result["framework"].upper()
        confidence = result["confidence"]
        evidence = result["evidence"]
        
        context = f"""
🎯 DETECTED FRAMEWORK: {framework}
═══════════════════════════════════════════════════════════════════════════
Confidence: {confidence}%

EVIDENCE:
{chr(10).join(f"  • {e}" for e in evidence)}

CRITICAL INSTRUCTIONS:
• This is a {framework} project - DO NOT suggest code for other frameworks!
• ALWAYS verify your assumptions against actual files in the repository
• If you're unsure about something, READ THE ACTUAL FILE first
• DO NOT hallucinate code patterns from other frameworks
• DO NOT make assumptions about file locations - check the actual structure
• ALWAYS use {framework}-specific patterns and best practices
"""
        
        # Add framework-specific guidance
        if framework == "FASTAPI":
            context += """
FASTAPI-SPECIFIC GUIDELINES:
• Use: @app.get(), @app.post(), @app.put(), @app.delete()
• Async patterns: async def endpoint()
• Dependency injection: Depends()
• Request/Response models: BaseModel from pydantic
• File uploads: UploadFile from fastapi
• Main file: Usually main.py or server.py with FastAPI() instance
• DO NOT use Flask syntax (@app.route, request.files)!
• DO NOT use Django patterns (models.Model, admin.site)!
"""
        elif framework == "FLASK":
            context += """
FLASK-SPECIFIC GUIDELINES:
• Use: @app.route() for routing
• Request handling: request.form, request.files, request.json
• Main file: Usually app.py with Flask(__name__)
• DO NOT use FastAPI syntax (async def, UploadFile)!
"""
        elif framework == "DJANGO":
            context += """
DJANGO-SPECIFIC GUIDELINES:
• Models: django.db.models.Model
• Views: Function-based or Class-based views
• URLs: urlpatterns in urls.py
• Settings: INSTALLED_APPS in settings.py
"""
        
        context += """
═══════════════════════════════════════════════════════════════════════════
"""
        
        return context


# Convenience functions
def detect_framework(project_path: str) -> Dict:
    """Quick framework detection"""
    detector = FrameworkDetector(project_path)
    return detector.detect()


def get_framework_context(project_path: str) -> str:
    """Get formatted framework context for AI"""
    detector = FrameworkDetector(project_path)
    return detector.get_context_for_ai()


if __name__ == "__main__":
    import sys
    
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    print(f"🔍 Detecting framework in: {path}")
    print()
    
    detector = FrameworkDetector(path)
    result = detector.detect()
    
    print(f"Framework: {result['framework']}")
    print(f"Confidence: {result['confidence']}%")
    print()
    print("Evidence:")
    for e in result['evidence']:
        print(f"  {e}")
    print()
    if 'all_scores' in result:
        print("All Scores:")
        for fw, score in sorted(result['all_scores'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {fw:12s} {score:3d}")
