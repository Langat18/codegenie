"""Agents package initialization — imports and registers all agent walkers."""

include:std base;
include:std graph;

include:jac base;
include:jac repo_mapper;
include:jac code_analyzer;
include:jac doc_genie;
include:jac code_genius;

glob Agents = {
    "CodeGenius": CodeGenius,
    "RepoMapper": RepoMapper,
    "CodeAnalyzer": CodeAnalyzer,
    "DocGenie": DocGenie
};
