"""Base Agent Definitions"""

node BaseAgent {
    has name: str = "agent";
    has created: int = 0;
}

node RepoAgent(BaseAgent) {
    has repo_url: str = "";
    has repo_data: dict = {};
}

node AnalyzerAgent(BaseAgent) {
    has code_data: dict = {};
}

node DocAgent(BaseAgent) {
    has docs: str = "";
}

node base_node {
    has name: str = "base";
    has created: int = 0;
}