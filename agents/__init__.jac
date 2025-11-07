"""
Agents package initialization
Exports all agent walkers
"""

include:jac supervisor;
include:jac repo_mapper;
include:jac code_analyzer;
include:jac doc_genie;

# Export all agents
glob Agents = {
    "CodeGenius": CodeGenius,
    "RepoMapper": RepoMapper,
    "CodeAnalyzer": CodeAnalyzer,
    "DocGenie": DocGenie
};