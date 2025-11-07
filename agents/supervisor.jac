"""
CodeGenius Supervisor - Orchestrates all agents
"""
walker CodeGenius {
    has repo_url:str;

    can orchestrate with entry {
        print("\n" + "="*60);
        print("CODE GENIUS - Documentation Generator");
        print("="*60 + "\n");

        # Spawn RepoMapper to clone and map repository
        mapper = spawn RepoMapper(repo_url=self.repo_url) with root;
        repo_nodes = mapper.repo_nodes;

        if (repo_nodes and repo_nodes[0].status == "cloned") {
            # Analyze and generate documentation
            analyzer = spawn CodeAnalyzer() with repo_nodes[0];
            doc_genie = spawn DocGenie() with repo_nodes[0];

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
