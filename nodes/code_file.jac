"""CodeFile Node"""
node CodeFile {
    has path: str;
    has language: str;
    has content: str = "";
    has ast_data: dict = {};
    has priority: int = 0;
    has analyzed: bool = False;
}
