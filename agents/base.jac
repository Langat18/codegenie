node BaseAgent {
    has name = "agent";
    has created = 0;
    
    can process {
        report "Processing base agent";
    }
}

node RepoAgent:BaseAgent {
    has repo_url = "";
    has repo_data = {};
}

node AnalyzerAgent:BaseAgent {
    has code_data = {};
}

node DocAgent:BaseAgent {
    has docs = "";
}

node base_node {
    has name = "base";
    has created = 0;
}