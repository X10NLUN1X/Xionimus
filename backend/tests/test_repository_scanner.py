"""
Tests for Repository Scanner
"""
import pytest
from pathlib import Path
import tempfile
import os
from app.core.repository_scanner import RepositoryScanner


class TestRepositoryScanner:
    """Test repository scanning functionality"""
    
    def test_scanner_initialization(self):
        """Test scanner initializes with default path"""
        scanner = RepositoryScanner()
        assert scanner.root_path is not None
        assert isinstance(scanner.root_path, Path)
    
    def test_scanner_custom_path(self):
        """Test scanner accepts custom root path"""
        custom_path = "/tmp/test"
        scanner = RepositoryScanner(root_path=custom_path)
        assert str(scanner.root_path) == custom_path
    
    def test_excluded_directories(self):
        """Test that excluded directories are properly defined"""
        scanner = RepositoryScanner()
        excluded = scanner.EXCLUDE_DIRS
        
        # Verify common exclusions
        assert 'node_modules' in excluded
        assert '__pycache__' in excluded
        assert '.git' in excluded
        assert 'venv' in excluded
    
    def test_code_extensions(self):
        """Test that code extensions are properly defined"""
        scanner = RepositoryScanner()
        extensions = scanner.CODE_EXTENSIONS
        
        # Verify common code file types
        assert '.py' in extensions
        assert '.js' in extensions
        assert '.ts' in extensions
        assert '.tsx' in extensions
    
    def test_language_detection(self):
        """Test programming language detection from extension"""
        scanner = RepositoryScanner()
        
        assert scanner._detect_language('.py') == 'python'
        assert scanner._detect_language('.js') == 'javascript'
        assert scanner._detect_language('.ts') == 'typescript'
        assert scanner._detect_language('.java') == 'java'
        assert scanner._detect_language('.unknown') == 'unknown'
    
    def test_scan_with_temp_directory(self):
        """Test scanning a temporary directory with sample files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_py = Path(tmpdir) / "test.py"
            test_py.write_text("print('hello')")
            
            test_js = Path(tmpdir) / "test.js"
            test_js.write_text("console.log('hello');")
            
            # Create excluded directory
            node_modules = Path(tmpdir) / "node_modules"
            node_modules.mkdir()
            excluded_file = node_modules / "package.js"
            excluded_file.write_text("// should be excluded")
            
            # Scan
            scanner = RepositoryScanner(root_path=tmpdir)
            files = scanner.scan_repository(max_files=10)
            
            # Verify results
            assert len(files) == 2  # Only test.py and test.js
            
            # Verify excluded file is not in results
            file_names = [f['name'] for f in files]
            assert 'package.js' not in file_names
            assert 'test.py' in file_names
            assert 'test.js' in file_names
    
    def test_file_size_calculation(self):
        """Test that file sizes are calculated correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            content = "print('hello world')"
            test_file.write_text(content)
            
            scanner = RepositoryScanner(root_path=tmpdir)
            files = scanner.scan_repository()
            
            assert len(files) == 1
            assert files[0]['size'] == len(content)
            assert files[0]['lines'] == 1
    
    def test_priority_sorting(self):
        """Test that files are sorted by priority (backend > frontend > root)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files in different locations
            backend_dir = Path(tmpdir) / "backend"
            backend_dir.mkdir()
            backend_file = backend_dir / "api.py"
            backend_file.write_text("# backend")
            
            frontend_dir = Path(tmpdir) / "frontend"
            frontend_dir.mkdir()
            frontend_file = frontend_dir / "app.js"
            frontend_file.write_text("// frontend")
            
            root_file = Path(tmpdir) / "readme.md"
            root_file.write_text("# readme")
            
            scanner = RepositoryScanner(root_path=tmpdir)
            files = scanner.scan_repository()
            
            # Verify sorting (backend first, then frontend, then root)
            assert len(files) == 3
            assert files[0]['relative_path'].startswith('backend/')
            assert files[1]['relative_path'].startswith('frontend/')
            # Note: .md files should be in CODE_EXTENSIONS to be included
    
    def test_summary_generation(self):
        """Test summary statistics generation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            py_file = Path(tmpdir) / "test.py"
            py_file.write_text("print('hello')\nprint('world')")
            
            js_file = Path(tmpdir) / "test.js"
            js_file.write_text("console.log('test');")
            
            scanner = RepositoryScanner(root_path=tmpdir)
            files = scanner.scan_repository()
            summary = scanner.get_summary(files)
            
            assert summary['total_files'] == 2
            assert summary['total_lines'] == 3  # 2 Python + 1 JS
            assert 'by_language' in summary
            assert 'python' in summary['by_language']
            assert 'javascript' in summary['by_language']
    
    def test_max_files_limit(self):
        """Test that max_files limit is respected"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create many files
            for i in range(20):
                test_file = Path(tmpdir) / f"test{i}.py"
                test_file.write_text(f"# file {i}")
            
            scanner = RepositoryScanner(root_path=tmpdir)
            files = scanner.scan_repository(max_files=5)
            
            assert len(files) == 5  # Limited to 5
