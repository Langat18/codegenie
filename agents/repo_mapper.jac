"""
RepoMapper Agent
Clones repository, generates file tree, and summarizes README
"""

include:jac ../models/nodes;
include:jac ../models/data_types;
include:jac ../config;

import:py os;
import:py from datetime import, datetime;

walker RepoMapper {
    """
    Agent responsible for repository mapping
    - Clones the repository
    - Generates file tree structure
    - Finds and summarizes README
    - Identifies entry points
    """
    has repo_url: str;
    has session_id: str;
    has status: str = "pending";
    has result: dict = {};
    has errors: list = [];
    has local_path: str = "";
    
    can start_mapping with `root entry {
        """Start the repository mapping process"""
        import:py from utils.git_handler, GitHandler;
        import:py from utils.file_parser, FileParser;
        
        logger.info(f"[RepoMapper] Starting mapping for {self.repo_url}");
        
        # Step 1: Clone repository
        git_handler = GitHandler(TEMP_DIR);
        repo_name = git_handler.extract_repo_name(self.repo_url);
        
        success, local_path, error = git_handler.clone_repository(
            self.repo_url,
            timeout=CLONE_TIMEOUT_SECONDS
        );
        
        if not success {
            self.errors.append(f"Failed to clone repository: {error}");
            self.status = "failed";
            return;
        }
        
        self.local_path = local_path;
        logger.info(f"✓ Repository cloned to {local_path}");
        
        # Check repository size
        repo_size_mb = git_handler.get_repo_size_mb(local_path);
        if repo_size_mb > MAX_REPO_SIZE_MB {
            self.errors.append(f"Repository too large: {repo_size_mb:.2f}MB > {MAX_REPO_SIZE_MB}MB");
            self.status = "failed";
            return;
        }
        
        logger.info(f"Repository size: {repo_size_mb:.2f}MB");
        
        # Step 2: Generate file tree
        file_parser = FileParser(IGNORED_DIRS);
        file_tree = file_parser.generate_file_tree(local_path, max_depth=10);
        
        if not file_tree {
            self.errors.append("Failed to generate file tree");
            self.status = "failed";
            return;
        }
        
        logger.info("✓ File tree generated");
        
        # Step 3: Get file statistics
        file_stats = file_parser.get_file_stats(local_path);
        logger.info(f"Total files: {file_stats['total_files']}, Total lines: {file_stats['total_lines']}");
        
        # Step 4: Find and read README
        success, readme_content = file_parser.read_readme(local_path);
        readme_summary = "";
        
        if success {
            logger.info("✓ README found");
            # Summarize README using LLM
            readme_summary = self.summarize_readme(readme_content);
        } else {
            logger.warning("⚠ No README found");
            readme_summary = "No README file found in repository";
        }
        
        # Step 5: Identify entry points
        entry_points = file_parser.find_entry_points(local_path);
        logger.info(f"Entry points found: {len(entry_points)}");
        
        # Step 6: Get all source files
        all_files = [];
        for ext_list in SUPPORTED_EXTENSIONS.values() {
            files = file_parser.get_all_files(local_path, ext_list);
            all_files.extend(files);
        }
        
        logger.info(f"Source files found: {len(all_files)}");
        
        # Compile result
        self.result = {
            "repo_name": repo_name,
            "local_path": local_path,
            "repo_url": self.repo_url,
            "repo_size_mb": repo_size_mb,
            "file_tree": file_tree,
            "file_stats": file_stats,
            "readme_summary": readme_summary,
            "entry_points": entry_points,
            "all_files": all_files,
            "total_files": len(all_files),
            "mapped_at": datetime.now().isoformat()
        };
        
        self.status = "completed";
        logger.info("[RepoMapper] Mapping completed successfully");
    }
    
    can summarize_readme(content: str) -> str {
        """
        Summarize README content using LLM
        """
        if not content or len(content) < 100 {
            return "README is too short to summarize";
        }
        
        # Truncate very long READMEs
        if len(content) > 10000 {
            content = content[:10000] + "...";
        }
        
        try {
            if LLM_PROVIDER == "openai" {
                return self.summarize_with_openai(content);
            } elif LLM_PROVIDER == "gemini" {
                return self.summarize_with_gemini(content);
            } else {
                # Fallback: simple extraction
                return self.extract_simple_summary(content);
            }
        } except Exception as e {
            logger.error(f"Error summarizing README: {str(e)}");
            return self.extract_simple_summary(content);
        }
    }
    
    can summarize_with_openai(content: str) -> str {
        """Summarize using OpenAI"""
        import:py openai;
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY);
        
        prompt = f"""Summarize the following README in 3-5 sentences. Focus on:
1. What the project does
2. Key features
3. Main technologies used

README:
{content}

Summary:""";
        
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a technical documentation expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        );
        
        return response.choices[0].message.content.strip();
    }
    
    can summarize_with_gemini(content: str) -> str {
        """Summarize using Gemini"""
        import:py google.generativeai as genai;
        
        genai.configure(api_key=GEMINI_API_KEY);
        model = genai.GenerativeModel(LLM_MODEL);
        
        prompt = f"""Summarize the following README in 3-5 sentences. Focus on:
1. What the project does
2. Key features
3. Main technologies used

README:
{content}""";
        
        response = model.generate_content(prompt);
        return response.text.strip();
    }
    
    can extract_simple_summary(content: str) -> str {
        """
        Extract simple summary from README without LLM
        Takes first few paragraphs
        """
        lines = content.split('\n');
        summary_lines = [];
        
        for line in lines[:20] {
            line = line.strip();
            # Skip markdown headers and empty lines
            if line and not line.startswith('#') and len(line) > 20 {
                summary_lines.append(line);
                if len(summary_lines) >= 3 {
                    break;
                }
            }
        }
        
        return ' '.join(summary_lines) if summary_lines else "No summary available";
    }
    
    can get_primary_language(file_stats: dict) -> str {
        """Determine primary programming language"""
        languages = file_stats.get('languages', {});
        
        if not languages {
            return 'unknown';
        }
        
        # Find language with most lines of code
        primary = max(languages.items(), key=lambda x: x[1].get('lines', 0));
        return primary[0];
    }
}