include repo_mapper;
include code_analyzer;
include doc_genie;

walker CodeGenius {
    has repo_url:str = "";
    
    can orchestrate with entry {
        print("\n" + "="*60);
        print("CODE GENIUS - Documentation Generator");
        print("="*60 + "\n");
        
        mapper = RepoMapper(repo_url=self.repo_url) spawn root;
        repo_nodes = mapper.repo_nodes;

        if repo_nodes and repo_nodes[0].status == "cloned" {
            analyzer = CodeAnalyzer() spawn repo_nodes[0];
            doc_genie = DocGenie() spawn repo_nodes[0];
            doc_nodes = doc_genie.doc_nodes;
            
            if doc_nodes {
                print("Status: success");
                print("Repository: " + repo_nodes[0].name);
                print("Output: " + doc_nodes[0].output_path);
            } else {
                print("Status: error - Doc generation failed");
            }
        } else {
            print("Status: error - Clone failed");
        }
    }
}