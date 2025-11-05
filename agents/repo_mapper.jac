"""RepoMapper Agent - Clones and maps repositories"""
import:py from utils.git_operations {clone_repository, validate_github_url};
import:py from utils.file_scanner {scan_directory, detect_languages, find_readme, count_total_files};
import:py os;
import:py time;

walker RepoMapper {
    has repo_url: str;
    has clone_dir: str = "./temp_repos";
    
    can start with `root entry {
        print(f"[RepoMapper] Starting analysis of {self.repo_url}");
        
        if not validate_github_url(self.repo_url):
            print("[RepoMapper] Invalid GitHub URL");
            return;
        
        repo_name = self.repo_url.rstrip('/').split('/')[-1].replace('.git', '');
        repo = Repository(url=self.repo_url, name=repo_name);
        root ++> repo;
        visit repo;
    }
    
    can clone_repository with Repository entry {
        print(f"[RepoMapper] Cloning {here.name}...");
        start_time = time.time();
        
        try {
            local_path = clone_repository(here.url, self.clone_dir, here.name, timeout=300);
            here.local_path = local_path;
            here.status = "cloned";
            here.clone_time = time.time() - start_time;
            print(f"[RepoMapper] Cloned in {here.clone_time:.2f}s");
            
            file_tree = FileTree(path=local_path);
            readme = ReadmeSummary();
            here ++> file_tree;
            here ++> readme;
            visit [-->];
        } except Exception as e {
            here.status = "error";
            here.error_msg = str(e);
            print(f"[RepoMapper] Error: {e}");
        }
    }
    
    can build_file_tree with FileTree entry {
        print(f"[RepoMapper] Building file tree");
        repo_node = [<--][0];
        structure = scan_directory(repo_node.local_path);
        here.structure = structure;
        here.total_files = count_total_files(structure);
        here.languages = detect_languages(structure);
        print(f"[RepoMapper] Found {here.total_files} files");
    }
    
    can summarize_readme with ReadmeSummary entry {
        print(f"[RepoMapper] Looking for README");
        repo_node = [<--][0];
        readme_path = find_readme(repo_node.local_path);
        
        if readme_path:
            print(f"[RepoMapper] Found README");
            try {
                with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                    here.content = f.read(5000);
                here.found = True;
                here.summary = self.generate_summary(here.content);
                here.key_points = self.extract_key_points(here.content);
                print(f"[RepoMapper] README summarized");
            } except Exception as e {
                print(f"[RepoMapper] Couldn't read README: {e}");
            }
        }
    }
    
    """Generate README summary."""
    def generate_summary(content: str) -> str by llm();
    """Extract key points."""
    def extract_key_points(content: str) -> list[str] by llm();
}
