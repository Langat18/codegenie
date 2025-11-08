include base;
include repo_mapper;
include code_analyzer;
include doc_genie;
include code_genius;

glob Agents = {
    "CodeGenius": CodeGenius,
    "RepoMapper": RepoMapper,
    "CodeAnalyzer": CodeAnalyzer,
    "DocGenie": DocGenie
};