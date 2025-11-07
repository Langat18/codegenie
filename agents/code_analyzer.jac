"""
CodeAnalyzer Agent
Performs deep code analysis and builds Code Context Graph (CCG)
"""

include:jac ../models/nodes;
include:jac ../models/data_types;
include:jac ../config;

import:py os;
import:py from datetime import, datetime;
import:py from typing, List, Dict;

walker CodeAnalyzer {
    """
    Agent responsible for code analysis
    - Parses source files using Tree-sitter
    - Builds Code Context Graph (CCG)
    - Identifies functions, classes, and relationships
    - Provides query APIs for relationships
    """
    has repo_path: str;
    has session_id: str;
    has priority_files: list = [];
    has status: str = "pending";
    has result: dict = {};
    has errors: list = [];
    has ccg: dict = {};
    
    can start_analysis with `root entry {
        """Start the code analysis process"""
        import:py from utils.tree_sitter_parser, TreeSitterParser;
        import:py from utils.file_parser, FileParser;
        
        logger.info(f"[CodeAnalyzer] Starting analysis for {self.repo_path}");
        
        # Initialize parsers
        parser = TreeSitterParser();
        file_parser = FileParser(IGNORED_DIRS);
        
        # Get all source files
        all_files = [];
        for lang, extensions in SUPPORTED_EXTENSIONS.items() {
            files = file_parser.get_all_files(self.repo_path, extensions);
            for filepath in files {
                all_files.append({
                    "path": filepath,
                    "language": lang,
                    "name": os.path.basename(filepath)
                });
            }
        }
        
        logger.info(f"Found {len(all_files)} source files to analyze");
        
        # Prioritize files
        prioritized_files = self.prioritize_files(all_files);
        
        # Initialize CCG
        self.ccg = {
            "functions": {},
            "classes": {},
            "modules": {},
            "relationships": [],
            "imports": []
        };
        
        # Analyze files
        analyzed_count = 0;
        skipped_count = 0;
        
        for file_info in prioritized_files[:MAX_FILES_TO_ANALYZE] {
            filepath = file_info["path"];
            language = file_info["language"];
            
            # Read file content
            success, content = file_parser.read_file_content(
                filepath,
                max_size_kb=MAX_FILE_SIZE_KB
            );
            
            if not success {
                logger.warning(f"Skipping {filepath}: {content}");
                skipped_count += 1;
                continue;
            }
            
            # Parse file
            try {
                parsed_data = parser.parse_file(filepath, content, language);
                
                if "error" in parsed_data {
                    logger.warning(f"Parse error in {filepath}: {parsed_data['error']}");
                    continue;
                }
                
                # Add to CCG
                self.add_to_ccg(filepath, parsed_data, language);
                analyzed_count += 1;
                
                if analyzed_count % 10 == 0 {
                    logger.info(f"Analyzed {analyzed_count} files...");
                }
                
            } except Exception as e {
                logger.error(f"Error parsing {filepath}: {str(e)}");
                self.errors.append(f"Error parsing {filepath}: {str(e)}");
            }
        }
        
        logger.info(f"✓ Analyzed {analyzed_count} files, skipped {skipped_count}");
        
        # Build relationships
        self.build_relationships();
        
        # Compile results
        self.result = {
            "total_files_analyzed": analyzed_count,
            "total_functions": len(self.ccg["functions"]),
            "total_classes": len(self.ccg["classes"]),
            "total_modules": len(self.ccg["modules"]),
            "relationships": self.ccg["relationships"],
            "ccg": self.ccg,
            "analyzed_at": datetime.now().isoformat()
        };
        
        self.status = "completed";
        logger.info("[CodeAnalyzer] Analysis completed successfully");
    }
    
    can prioritize_files(files: list) -> list {
        """Prioritize files for analysis"""
        # Priority 1: Explicitly provided priority files
        prioritized = [];
        remaining = [];
        
        for file in files {
            filepath = file["path"];
            if any(filepath.endswith(pf) or filepath == pf for pf in self.priority_files) {
                file["priority"] = 10;
                prioritized.append(file);
            } else {
                remaining.append(file);
            }
        }
        
        # Priority 2: Entry point patterns
        for file in remaining[:] {
            filename = file["name"].lower();
            for pattern in PRIORITY_PATTERNS {
                if filename == pattern.lower() {
                    file["priority"] = 8;
                    prioritized.append(file);
                    remaining.remove(file);
                    break;
                }
            }
        }
        
        # Priority 3: By directory depth (prefer root-level files)
        for file in remaining {
            depth = file["path"].count(os.sep);
            file["priority"] = max(0, 5 - depth);
        }
        
        remaining.sort(key=lambda x: x["priority"], reverse=True);
        prioritized.extend(remaining);
        
        return prioritized;
    }
    
    can add_to_ccg(filepath: str, parsed_data: dict, language: str) {
        """Add parsed data to Code Context Graph"""
        module_name = self.get_module_name(filepath);
        
        # Add module
        self.ccg["modules"][module_name] = {
            "path": filepath,
            "language": language,
            "imports": parsed_data.get("imports", []),
            "functions": [],
            "classes": []
        };
        
        # Add functions
        for func in parsed_data.get("functions", []) {
            func_key = f"{module_name}.{func['name']}";
            self.ccg["functions"][func_key] = {
                **func,
                "module": module_name
            };
            self.ccg["modules"][module_name]["functions"].append(func['name']);
        }
        
        # Add classes
        for cls in parsed_data.get("classes", []) {
            class_key = f"{module_name}.{cls['name']}";
            self.ccg["classes"][class_key] = {
                **cls,
                "module": module_name
            };
            self.ccg["modules"][module_name]["classes"].append(cls['name']);
        }
        
        # Add imports
        for imp in parsed_data.get("imports", []) {
            self.ccg["imports"].append({
                "from_module": module_name,
                "import_statement": imp,
                "file": filepath
            });
        }
    }
    
    can build_relationships() {
        """Build relationships between code entities"""
        logger.info("Building code relationships...");
        
        # Function call relationships
        for func_key, func_data in self.ccg["functions"].items() {
            calls = func_data.get("calls", []);
            for called_func in calls {
                self.ccg["relationships"].append({
                    "type": "calls",
                    "source": func_key,
                    "target": called_func,
                    "source_file": func_data["file_path"]
                });
            }
        }
        
        # Class inheritance relationships
        for class_key, class_data in self.ccg["classes"].items() {
            base_classes = class_data.get("base_classes", []);
            for base_class in base_classes {
                self.ccg["relationships"].append({
                    "type": "inherits",
                    "source": class_key,
                    "target": base_class,
                    "source_file": class_data["file_path"]
                });
            }
        }
        
        # Module import relationships
        for imp_data in self.ccg["imports"] {
            self.ccg["relationships"].append({
                "type": "imports",
                "source": imp_data["from_module"],
                "target": imp_data["import_statement"],
                "source_file": imp_data["file"]
            });
        }
        
        logger.info(f"✓ Built {len(self.ccg['relationships'])} relationships");
    }
    
    can get_module_name(filepath: str) -> str {
        """Extract module name from file path"""
        # Remove repo path and extension
        rel_path = filepath.replace(self.repo_path, "").lstrip(os.sep);
        module_name = os.path.splitext(rel_path)[0];
        # Replace path separators with dots
        module_name = module_name.replace(os.sep, '.');
        return module_name;
    }
    
    can query_functions_called_by(func_name: str) -> list {
        """Query which functions are called by a given function"""
        results = [];
        for rel in self.ccg["relationships"] {
            if rel["type"] == "calls" and func_name in rel["source"] {
                results.append(rel["target"]);
            }
        }
        return results;
    }
    
    can query_functions_calling(func_name: str) -> list {
        """Query which functions call a given function"""
        results = [];
        for rel in self.ccg["relationships"] {
            if rel["type"] == "calls" and func_name in rel["target"] {
                results.append(rel["source"]);
            }
        }
        return results;
    }
    
    can query_class_hierarchy(class_name: str) -> dict {
        """Query class inheritance hierarchy"""
        hierarchy = {
            "name": class_name,
            "inherits_from": [],
            "inherited_by": []
        };
        
        for rel in self.ccg["relationships"] {
            if rel["type"] == "inherits" {
                if class_name in rel["source"] {
                    hierarchy["inherits_from"].append(rel["target"]);
                }
                if class_name in rel["target"] {
                    hierarchy["inherited_by"].append(rel["source"]);
                }
            }
        }
        
        return hierarchy;
    }
}