import:jac from repo_mapper, RepoMapper;
import:jac from code_analyzer, CodeAnalyzer;
import:jac from doc_genie, DocGenie;

walker CodeGenius {
    has repo_url:str = "";
    
    can orchestrate with entry {
        print("\n" + "="*60);
        print("CODE GENIUS - Documentation Generator");
        print("="*60 + "\n");
        
        # Spawn RepoMapper
        mapper = RepoMapper(repo_url=self.repo_url) spawn root;
        repo_nodes = mapper.repo_nodes;

        if (repo_nodes and repo_nodes[0].status == "cloned") {
            # Spawn CodeAnalyzer
            analyzer = CodeAnalyzer() spawn repo_nodes[0];
            
            # Spawn DocGenie
            doc_genie = DocGenie() spawn repo_nodes[0];
            
            doc_nodes = doc_genie.doc_nodes;
            
            if (doc_nodes) {
                report {
                    "status": "success",
                    "repository": repo_nodes[0].name,
                    "output": doc_nodes[0].output_path
                };
            } else {
                report {"status": "error", "message": "Doc generation failed"};
            }
        } else {
            report {"status": "error", "message": "Clone failed"};
        }
    }
}