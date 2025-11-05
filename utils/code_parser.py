"""Code parsing utilities"""
import ast
import re

def parse_python_file(content, filepath="<unknown>"):
    result = {"functions": [], "classes": [], "imports": []}
    try:
        tree = ast.parse(content, filename=filepath)
    except:
        return result
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "params": [arg.arg for arg in node.args.args],
                "line": node.lineno,
                "calls": []
            })
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                "inherits": [b.id for b in node.bases if isinstance(b, ast.Name)]
            })
        elif isinstance(node, ast.Import):
            result["imports"].extend([alias.name for alias in node.names])
        elif isinstance(node, ast.ImportFrom) and node.module:
            result["imports"].append(node.module)
    return result

def parse_jac_file(content, filepath="<unknown>"):
    result = {"functions": [], "classes": [], "imports": []}
    walkers = re.findall(r'walker\s+(\w+)', content)
    for w in walkers:
        result["classes"].append({"name": w, "type": "walker", "methods": [], "inherits": [], "line": 0})
    nodes = re.findall(r'node\s+(\w+)', content)
    for n in nodes:
        result["classes"].append({"name": n, "type": "node", "methods": [], "inherits": [], "line": 0})
    abilities = re.findall(r'can\s+(\w+)\s+with', content)
    for a in abilities:
        result["functions"].append({"name": a, "type": "ability", "params": [], "calls": [], "line": 0})
    return result

def parse_javascript_file(content, filepath="<unknown>"):
    result = {"functions": [], "classes": [], "imports": []}
    functions = re.findall(r'function\s+(\w+)\s*\(([^)]*)\)', content)
    for name, params in functions:
        result["functions"].append({"name": name, "params": [], "calls": [], "line": 0})
    classes = re.findall(r'class\s+(\w+)(?:\s+extends\s+(\w+))?', content)
    for name, parent in classes:
        result["classes"].append({"name": name, "inherits": [parent] if parent else [], "methods": [], "line": 0})
    return result
