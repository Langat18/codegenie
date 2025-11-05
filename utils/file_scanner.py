"""File system utilities"""
import os

DEFAULT_IGNORE_DIRS = [".git", "node_modules", "__pycache__", ".venv", "venv"]
DEFAULT_IGNORE_EXTS = [".pyc", ".pyo", ".so", ".dll", ".exe", ".jpg", ".png", ".zip"]

def scan_directory(root_path, ignore_dirs=None, ignore_exts=None, max_depth=10):
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS
    if ignore_exts is None:
        ignore_exts = DEFAULT_IGNORE_EXTS
    
    def _scan(path, depth=0):
        if depth > max_depth:
            return None
        result = {"name": os.path.basename(path), "type": "directory", "children": []}
        try:
            items = os.listdir(path)
        except:
            return result
        
        for item in items:
            if item.startswith('.') or item in ignore_dirs:
                continue
            item_path = os.path.join(path, item)
            if os.path.islink(item_path):
                continue
            if os.path.isdir(item_path):
                subdir = _scan(item_path, depth + 1)
                if subdir:
                    result["children"].append(subdir)
            else:
                ext = os.path.splitext(item)[1].lower()
                if ext not in ignore_exts:
                    result["children"].append({
                        "name": item, "type": "file",
                        "path": item_path, "extension": ext
                    })
        return result
    return _scan(root_path)

def detect_languages(file_tree):
    lang_map = {
        ".py": "Python", ".jac": "Jac", ".js": "JavaScript",
        ".ts": "TypeScript", ".java": "Java", ".go": "Go"
    }
    counts = {}
    def count_files(node):
        if node.get("type") == "file":
            ext = node.get("extension", "")
            lang = lang_map.get(ext, "Other")
            counts[lang] = counts.get(lang, 0) + 1
        else:
            for child in node.get("children", []):
                count_files(child)
    count_files(file_tree)
    return counts

def count_total_files(file_tree):
    if file_tree.get("type") == "file":
        return 1
    return sum(count_total_files(child) for child in file_tree.get("children", []))

def find_readme(directory):
    candidates = ["README.md", "README.txt", "README", "readme.md"]
    for candidate in candidates:
        path = os.path.join(directory, candidate)
        if os.path.isfile(path):
            return path
    return ""
