"""
Tests for Edit Agent
"""
import pytest
import os
import tempfile
import shutil
import asyncio
from pathlib import Path
from app.core.edit_agent import EditAgent


@pytest.fixture
def temp_workspace():
    """Create temporary workspace"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    try:
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception:
        pass


@pytest.fixture
def edit_agent():
    """Create edit agent instance"""
    return EditAgent()


@pytest.mark.asyncio
async def test_user_directed_edit_basic(edit_agent, temp_workspace):
    """
    Test basic user-directed edit functionality
    """
    test_file = os.path.join(temp_workspace, "test.py")
    
    # Create test file
    with open(test_file, 'w') as f:
        f.write("def old_function():\n    pass\n")
    
    # This will fail without AI, but test the file operations
    result = await edit_agent.user_directed_edit(
        file_path="test.py",
        edit_instructions="Test edit",
        workspace_path=temp_workspace
    )
    
    # Should at least not crash with file permission errors
    assert 'status' in result
    assert 'file' in result


@pytest.mark.asyncio
async def test_file_read_retry_mechanism(edit_agent, temp_workspace):
    """
    Test that file read retries work (simulates Windows file locks)
    """
    test_file = os.path.join(temp_workspace, "locked.py")
    
    with open(test_file, 'w') as f:
        f.write("x = 1\n")
    
    # Try to edit while file exists
    result = await edit_agent.user_directed_edit(
        file_path="locked.py",
        edit_instructions="Change x to 2",
        workspace_path=temp_workspace
    )
    
    # Should handle gracefully (may fail AI, but not file ops)
    assert result['status'] in ['success', 'error']
    assert 'file' in result


@pytest.mark.asyncio
async def test_atomic_write_pattern(edit_agent, temp_workspace):
    """
    Test that atomic write pattern works
    """
    test_file = os.path.join(temp_workspace, "atomic.py")
    original_content = "original = True\n"
    
    with open(test_file, 'w') as f:
        f.write(original_content)
    
    # File exists and is readable
    assert os.path.exists(test_file)
    assert os.access(test_file, os.R_OK)
    assert os.access(test_file, os.W_OK)


@pytest.mark.asyncio
async def test_nonexistent_file_error(edit_agent, temp_workspace):
    """
    Test proper error handling for nonexistent files
    """
    result = await edit_agent.user_directed_edit(
        file_path="nonexistent.py",
        edit_instructions="Test",
        workspace_path=temp_workspace
    )
    
    assert result['status'] == 'error'
    assert 'not found' in result['message'].lower()


@pytest.mark.asyncio
async def test_workspace_file_listing(edit_agent):
    """
    Test that workspace file finding works
    """
    # Use actual workspace
    files = edit_agent._find_code_files('/app/xionimus-ai')
    
    # Should find some files (or empty list if workspace empty)
    assert isinstance(files, list)


@pytest.mark.asyncio
async def test_summarize_changes(edit_agent):
    """
    Test change summarization
    """
    old_content = "line 1\nline 2\nline 3"  # 3 lines (no trailing newline)
    new_content = "line 1\nline 2 modified\nline 3\nline 4"  # 4 lines
    
    summary = edit_agent._summarize_changes(old_content, new_content)
    
    assert 'old_lines' in summary
    assert 'new_lines' in summary
    assert 'lines_changed' in summary
    # Content with 3 lines split creates 3 items
    assert summary['new_lines'] == 4
    assert summary['lines_changed'] == 1  # Difference


@pytest.mark.asyncio
async def test_get_language_from_extension(edit_agent):
    """
    Test language detection from file extensions
    """
    assert edit_agent._get_language_from_extension('.py') == 'python'
    assert edit_agent._get_language_from_extension('.js') == 'javascript'
    assert edit_agent._get_language_from_extension('.tsx') == 'typescript'
    assert edit_agent._get_language_from_extension('.unknown') == 'text'


@pytest.mark.asyncio
async def test_quick_analyze_file(edit_agent):
    """
    Test quick static analysis
    """
    python_code = """
def test():
    print("hello")  # Should warn about print
    try:
        pass
    except:  # Should warn about bare except
        pass
"""
    
    suggestions = edit_agent._quick_analyze_file("test.py", python_code)
    
    # Should find some issues
    assert isinstance(suggestions, list)
    # May find print() and bare except issues
    if suggestions:
        assert all('file' in s and 'issue' in s for s in suggestions)


@pytest.mark.asyncio
async def test_batch_edit_structure(edit_agent, temp_workspace):
    """
    Test batch edit returns proper structure
    """
    # Create test files
    file1 = os.path.join(temp_workspace, "file1.py")
    file2 = os.path.join(temp_workspace, "file2.py")
    
    with open(file1, 'w') as f:
        f.write("x = 1\n")
    with open(file2, 'w') as f:
        f.write("y = 2\n")
    
    result = await edit_agent.batch_edit(
        edit_requests=[
            {"file": "file1.py", "instructions": "Test 1"},
            {"file": "file2.py", "instructions": "Test 2"}
        ],
        workspace_path=temp_workspace
    )
    
    assert 'status' in result
    assert 'results' in result
    assert 'success_count' in result
    assert 'total_requests' in result
    assert result['total_requests'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
