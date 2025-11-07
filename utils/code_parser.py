import ast
from typing import Dict, List


class CodeParser:
    """Parse Python code"""
    
    def parse_python(self, content: str) -> Dict:
        """
        Parse Python code
        
        Returns:
            Dictionary with functions, classes, and imports
        """
        result = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Extract functions
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'docstring': ast.get_docstring(node) or '',
                        'parameters': [arg.arg for arg in node.args.args],
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    }
                    result['functions'].append(func_info)
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    
                    class_info = {
                        'name': node.name,
                        'line_number': node.lineno,
                        'docstring': ast.get_docstring(node) or '',
                        'methods': methods,
                        'base_classes': [base.id for base in node.bases if isinstance(base, ast.Name)]
                    }
                    result['classes'].append(class_info)
                
                # Extract imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        result['imports'].append(node.module)
            
        except Exception as e:
            result['error'] = str(e)
        
        return result