"""CodeAnalyzer Agent - Parses code and builds CCG"""
import:py from utils.code_parser {parse_python_file, parse_jac_file, parse_javascript_file};
import:py os;

walker CodeAnalyzer {
    has target_languages: list = ["Python", "Jac"];
    has max_files: int = 50;
    
    can start with Repository entry {
        print(f"[CodeAnalyzer] Starting analysis");
        file_trees = [-->(`?FileTree)];
        if not file_trees:
            return;
        
        ccg = CodeContextGraph();
        here ++> ccg;
        
        files = self._extract_files(file_trees[0].structure);
        prioritized = self._prioritize(files);
        
        print(f"[CodeAnalyzer] Will analyze {min(len(prioritized), self.max_files)} files");
        
        for file_info in prioritized[:self.max_files]:
            code_file = CodeFile(
                path=file_info["path"],
                language=file_info["language"],
                priority=file_info["priority"]
            );
            here ++> code_file;
        
        visit [-->(`?CodeFile)];
        visit ccg;
    }
    
    can analyze_file with CodeFile entry {
        print(f"[CodeAnalyzer] Analyzing {os.path.basename(here.path)}");
        try {
            with open(here.path, 'r', encoding='utf-8', errors='ignore') as f:
                here.content = f.read();
            
            if here.language == "Python":
                here.ast_data = parse_python_file(here.content, here.path);
            elif here.language == "Jac":
                here.ast_data = parse_jac_file(here.content, here.path);
            
            here.analyzed = True;
        } except Exception as e {
            print(f"[CodeAnalyzer] Error: {e}");
        }
    }
    
    can build_ccg with CodeContextGraph entry {
        print(f"[CodeAnalyzer] Building CCG");
        repo = [<--][0];
        code_files = [-->(`?CodeFile)] spawn repo;
        
        functions = {};
        classes = {};
        relationships = [];
        
        for cf in code_files:
            if not cf.analyzed:
                continue;
            ast = cf.ast_data;
            for func in ast.get("functions", []):
                key = f"{cf.path}::{func['name']}";
                functions[key] = {
                    "name": func["name"],
                    "file": cf.path,
                    "params": func.get("params", []),
                    "line": func.get("line", 0)
                };
            for cls in ast.get("classes", []):
                key = f"{cf.path}::{cls['name']}";
                classes[key] = {
                    "name": cls["name"],
                    "file": cf.path,
                    "methods": cls.get("methods", []),
                    "inherits": cls.get("inherits", []),
                    "line": cls.get("line", 0)
                };
        
        here.functions = functions;
        here.classes = classes;
        here.relationships = relationships;
        print(f"[CodeAnalyzer] Found {len(functions)} functions, {len(classes)} classes");
    }
    
    def _extract_files(structure: dict) -> list {
        files = [];
        lang_map = {"Python": ".py", "Jac": ".jac"};
        target_exts = [lang_map.get(lang) for lang in self.target_languages if lang in lang_map];
        
        def traverse(node):
            if node["type"] == "file":
                ext = node.get("extension", "");
                if ext in target_exts:
                    lang = [k for k, v in lang_map.items() if v == ext][0];
                    files.append({"path": node["path"], "name": node["name"], "language": lang, "priority": 0});
            else:
                for child in node.get("children", []):
                    traverse(child);
        traverse(structure);
        return files;
    }
    
    def _prioritize(files: list) -> list {
        high_priority = ["main.py", "app.py", "__init__.py", "main.jac"];
        for f in files:
            if f["name"].lower() in high_priority:
                f["priority"] = 10;
            else:
                f["priority"] = 1;
        return sorted(files, key=lambda x: x["priority"], reverse=True);
    }
}
