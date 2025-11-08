"""API Endpoints"""
walker generate_docs {
    has repo_url: str;
    
    can start with `root entry {
        if not self.repo_url or "github.com" not in self.repo_url {
            report {"error": "Invalid GitHub URL"};
            return;
        }
        print(f"[API] Request for: {self.repo_url}");
        genius = CodeGenius(repo_url=self.repo_url) spawn root;
        report genius;
    }
}

walker quick_analyze {
    has repo_url: str;
    
    can start with `root entry {
        if not self.repo_url or "github.com" not in self.repo_url {
            report {"error": "Invalid GitHub URL"};
            return;
        }
        mapper = RepoMapper(repo_url=self.repo_url) spawn root;
        repo_nodes = [-->(`?Repository)];
        if repo_nodes and repo_nodes[0].status == "cloned" {
            analyzer = CodeAnalyzer() spawn repo_nodes[0];
            ccg = [-->(`?CodeContextGraph)] spawn repo_nodes[0];
            if ccg {
                report {"status": "success", "functions": len(ccg[0].functions), "classes": len(ccg[0].classes)};
            } else {
                report {"status": "error"};
            }
        } else {
            report {"status": "error"};
        }
    }
}
