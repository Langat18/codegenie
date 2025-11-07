"""
Git Operations Handler
"""

import os
import shutil
from typing import Tuple
from urllib.parse import urlparse
import git
from git.exc import GitCommandError


class GitHandler:
    """Handles Git repository operations"""
    
    def __init__(self, temp_dir: str = "./temp_repos"):
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
    
    def validate_github_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate GitHub repository URL
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)
            
            if parsed.netloc not in ['github.com', 'www.github.com']:
                return False, "URL must be from github.com"
            
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) < 2:
                return False, "Invalid repository format"
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid URL: {str(e)}"
    
    def extract_repo_name(self, url: str) -> str:
        """Extract repository name from URL"""
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        if len(path_parts) >= 2:
            repo_name = path_parts[1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            return repo_name
        
        return "unknown_repo"
    
    def clone_repository(self, url: str, target_dir: str = None, timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Clone a GitHub repository
        
        Returns:
            Tuple of (success, local_path, error_message)
        """
        is_valid, error_msg = self.validate_github_url(url)
        if not is_valid:
            return False, "", error_msg
        
        if target_dir is None:
            repo_name = self.extract_repo_name(url)
            target_dir = os.path.join(self.temp_dir, repo_name)
        
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        try:
            print(f"Cloning repository from {url}...")
            
            repo = git.Repo.clone_from(
                url,
                target_dir,
                depth=1,
                timeout=timeout
            )
            
            print(f"✓ Repository cloned to {target_dir}")
            return True, target_dir, ""
            
        except GitCommandError as e:
            error_msg = f"Git clone failed: {str(e)}"
            if "Authentication failed" in str(e):
                error_msg = "Repository is private"
            elif "not found" in str(e).lower():
                error_msg = "Repository not found"
            
            return False, "", error_msg
            
        except Exception as e:
            return False, "", f"Unexpected error: {str(e)}"
    
    def cleanup_repo(self, repo_path: str) -> bool:
        """Clean up cloned repository"""
        try:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
                print(f"✓ Cleaned up {repo_path}")
                return True
            return False
        except Exception as e:
            print(f"✗ Error cleaning up: {str(e)}")
            return False