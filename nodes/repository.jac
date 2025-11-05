"""Repository Node"""
node Repository {
    has url: str;
    has name: str;
    has local_path: str = "";
    has status: str = "pending";
    has error_msg: str = "";
    has clone_time: float = 0.0;
}
