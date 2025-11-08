"""Code Genius - Main Entry Point"""

node system {
    has name: str = "system";
    has created: int = 0;
}

include agents;

with entry {
    root ++> system();
    CodeGenius() spawn root;
}