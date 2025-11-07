"""
Pytest configuration and fixtures for Codebase Genius tests
Place this file at: tests/conftest.py
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_repo_url():
    """Sample GitHub repository URL for testing"""
    return "https://github.com/jaseci-labs/jaclang-samples"


@pytest.fixture
def invalid_repo_url():
    """Invalid repository URL for negative testing"""
    return "https://gitlab.com/user/repo"


@pytest.fixture
def api_base_url():
    """API base URL for testing"""
    return "http://localhost:8000"


@pytest.fixture
def test_session_id():
    """Sample session ID for testing"""
    return "test-session-12345"


@pytest.fixture
def sample_file_tree():
    """Sample file tree structure for testing"""
    return {
        "name": "test-repo",
        "type": "directory",
        "children": [
            {
                "name": "main.py",
                "type": "file",
                "language": "python",
                "size": 1024
            },
            {
                "name": "utils",
                "type": "directory",
                "children": [
                    {
                        "name": "helper.py",
                        "type": "file",
                        "language": "python",
                        "size": 512
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_code_content():
    """Sample Python code for parsing tests"""
    return '''
def hello_world():
    """A simple hello world function"""
    print("Hello, World!")

class MyClass:
    """A sample class"""
    def __init__(self):
        self.value = 0
    
    def increment(self):
        """Increment the value"""
        self.value += 1
'''


@pytest.fixture
def temp_test_dir(tmp_path):
    """Create a temporary directory for testing"""
    test_dir = tmp_path / "test_repo"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def mock_repo_structure(temp_test_dir):
    """Create a mock repository structure for testing"""
    # Create some files
    (temp_test_dir / "README.md").write_text("# Test Repository")
    (temp_test_dir / "main.py").write_text("print('Hello')")
    
    # Create subdirectory
    utils_dir = temp_test_dir / "utils"
    utils_dir.mkdir()
    (utils_dir / "helper.py").write_text("def help(): pass")
    
    return temp_test_dir


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )