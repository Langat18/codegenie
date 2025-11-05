"""CodeGenius Supervisor - Orchestrates all agents"""
walker CodeGenius {
    has repo_url: str;
    
    can orchestrate with `root entry {
        print("\n" + "="*60);
        print("CODE GENIUS - Documentation Generator");
        print("="*60 + "\n");
        
        mapper = RepoMapper(repo_url=self.repo_url) spawn root;
        
        repo_nodes = [-->(`?Repository)];
        if repo_nodes and repo_nodes[0].status == "cloned":
            analyzer = CodeAnalyzer() spawn repo_nodes[0];
            doc_genie = DocGenie() spawn repo_nodes[0];
            
            doc_nodes = [-->(`?Documentation)] spawn repo_nodes[0];
            if doc_nodes:
                report {"status": "success", "repository": repo_nodes[0].name, "output": doc_nodes[0].output_path};
            else:
                report {"status": "error", "message": "Doc generation failed"};
        else:
            report {"status": "error", "message": "Clone failed"};
    }
}
