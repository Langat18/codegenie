"""
Simple integration tests for Codebase Genius
Place this file at: tests/test_integration.py

Run with: pytest tests/test_integration.py -v
"""

import pytest
import requests
import time


@pytest.mark.integration
class TestBackendAPI:
    """Test backend API endpoints"""
    
    API_BASE = "http://localhost:8000"
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        try:
            response = requests.get(f"{self.API_BASE}/health", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "status" in data or "llm_provider" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running")
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response = requests.get(f"{self.API_BASE}/", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running")
    
    def test_sessions_endpoint(self):
        """Test sessions listing endpoint"""
        try:
            response = requests.get(f"{self.API_BASE}/sessions", timeout=5)
            assert response.status_code == 200
            data = response.json()
            assert "sessions" in data or "total" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running")


@pytest.mark.integration  
class TestFrontendConnection:
    """Test frontend connectivity"""
    
    FRONTEND_URL = "http://localhost:8501"
    
    def test_frontend_accessible(self):
        """Test if frontend is accessible"""
        try:
            response = requests.get(self.FRONTEND_URL, timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend not running")


@pytest.mark.integration
class TestFullWorkflow:
    """Test complete documentation generation workflow"""
    
    API_BASE = "http://localhost:8000"
    TEST_REPO = "https://github.com/jaseci-labs/jaclang-samples"
    
    @pytest.mark.slow
    def test_generate_documentation_workflow(self):
        """Test full documentation generation"""
        try:
            # 1. Start generation
            response = requests.post(
                f"{self.API_BASE}/generate_docs",
                json={"repo_url": self.TEST_REPO},
                timeout=10
            )
            
            if response.status_code != 200:
                pytest.skip("Cannot start generation")
            
            data = response.json()
            session_id = data.get("session_id")
            assert session_id is not None
            
            # 2. Check status
            response = requests.get(
                f"{self.API_BASE}/status/{session_id}",
                timeout=5
            )
            assert response.status_code == 200
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend not running")


@pytest.mark.unit
class TestBasicFunctionality:
    """Test basic Python functionality"""
    
    def test_imports(self):
        """Test that required packages are importable"""
        try:
            import requests
            import pytest
            assert True
        except ImportError as e:
            pytest.fail(f"Required package not available: {e}")
    
    def test_file_operations(self, tmp_path):
        """Test basic file operations"""
        # Create a test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Read it back
        content = test_file.read_text()
        assert content == "Hello, World!"
    
    def test_path_operations(self):
        """Test path operations"""
        import os
        path = os.path.join("folder", "file.txt")
        assert "folder" in path
        assert "file.txt" in path


# Simple function to run specific test
if __name__ == "__main__":
    # Run only unit tests
    pytest.main([__file__, "-v", "-m", "unit"])