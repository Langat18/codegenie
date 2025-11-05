"""Git utilities for cloning repositories"""
import subprocess
import os
import shutil
from pathlib import Path

def validate_github_url(url):
    if not url:
        return False
    valid_patterns = ["https://github.com/", "http://github.com/", "git@github.com:"]
    return any(url.startswith(p) for p in valid_patterns)

def clone_repository(url, destination_dir, repo_name, timeout=300):
    Path(destination_dir).mkdir(parents=True, exist_ok=True)
    local_path = os.path.join(destination_dir, repo_name)
    
    if os.path.exists(local_path):
        shutil.rmtree(local_path)
    
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url, local_path],
            check=True, capture_output=True, text=True, timeout=timeout
        )
        return local_path
    except subprocess.TimeoutExpired:
        raise Exception(f"Clone timed out after {timeout} seconds")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Clone failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("Git not installed")

def cleanup_repo(local_path):
    if os.path.exists(local_path):
        try:
            shutil.rmtree(local_path)
            return True
        except:
            return False
    return True
