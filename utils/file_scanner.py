

import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path


class FileScanner:
    """Handles file system operations"""
    
    def __init__(self, ignored_dirs: List[str] = None):
        self.ignored_dirs = ignored_dirs or [
            '.git', 'node_modules', 'venv', '.venv', '__pycache__',
            '.pytest_cache', 'dist', 'build', '.idea', '.vscode'
        ]
        
        self.language_extensions = {
            'python': ['.py'],
            'jac': ['.jac'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx'],
            'java': ['.java'],
            'cpp': ['.cpp', '.h', '.hpp']
        }
    
    def should_ignore(self, path: str) -> bool:
        """Check if path should be ignored"""
        path_parts = Path(path).parts
        return any(ignored_dir in path_parts for ignored_dir in self.ignored_dirs)
    
    def detect_language(self, filename: str) -> str:
        """Detect programming language from extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        for language, extensions in self.language_extensions.items():
            if ext in extensions:
                return language
        
        return 'unknown'
    
    def generate_file_tree(self, root_path: str, max_depth: int = 10) -> Dict:
        """Generate tree structure of repository"""
        def build_tree(path: str, depth: int = 0) -> Optional[Dict]:
            if depth > max_depth or self.should_ignore(path):
                return None
            
            name = os.path.basename(path)
            
            if os.path.isfile(path):
                language = self.detect_language(name)
                return {
                    'name': name,
                    'type': 'file',
                    'path': path,
                    'language': language,
                    'size': os.path.getsize(path)
                }
            
            elif os.path.isdir(path):
                children = []
                try:
                    for item in sorted(os.listdir(path)):
                        item_path = os.path.join(path, item)
                        child = build_tree(item_path, depth + 1)
                        if child:
                            children.append(child)
                except PermissionError:
                    pass
                
                return {
                    'name': name,
                    'type': 'directory',
                    'path': path,
                    'children': children
                }
            
            return None
        
        return build_tree(root_path)
    
    def get_all_files(self, root_path: str, extensions: List[str] = None) -> List[str]:
        """Get all files in repository"""
        all_files = []
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if not self.should_ignore(os.path.join(dirpath, d))]
            
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                
                if extensions:
                    if any(filename.endswith(ext) for ext in extensions):
                        all_files.append(filepath)
                else:
                    all_files.append(filepath)
        
        return all_files
    
    def find_readme(self, root_path: str) -> Optional[str]:
        """Find README file"""
        readme_patterns = [
            'README.md', 'readme.md', 'Readme.md',
            'README.rst', 'README.txt', 'README'
        ]
        
        for pattern in readme_patterns:
            readme_path = os.path.join(root_path, pattern)
            if os.path.exists(readme_path):
                return readme_path
        
        return None
    
    def read_readme(self, root_path: str) -> Tuple[bool, str]:
        """Read README file content"""
        readme_path = self.find_readme(root_path)
        
        if not readme_path:
            return False, "No README file found"
        
        try:
            with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return True, content
        except Exception as e:
            return False, f"Error reading README: {str(e)}"
    
    def find_entry_points(self, root_path: str) -> List[str]:
        """Find likely entry point files"""
        entry_patterns = [
            'main.py', 'app.py', '__main__.py', 'run.py',
            'server.py', 'index.py', 'start.py',
            'main.jac', 'app.jac', 'server.jac'
        ]
        
        entry_points = []
        
        for dirpath, dirnames, filenames in os.walk(root_path):
            depth = dirpath[len(root_path):].count(os.sep)
            if depth > 1:
                continue
            
            for filename in filenames:
                if filename.lower() in [p.lower() for p in entry_patterns]:
                    entry_points.append(os.path.join(dirpath, filename))
        
        return entry_points