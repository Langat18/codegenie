node CodeFile {
    has path = "";
    has content = "";
    has language = "";
}

node CodeRepo {
    has url = "";
    has name = "";
    has branch = "";
}

glob Nodes = {
    "CodeFile": CodeFile,
    "CodeRepo": CodeRepo
};