node CodeFile {
    has path:str = "";
    has content:str = "";
    has language:str = "";
}

node CodeRepo {
    has url:str = "";
    has name:str = "";
    has branch:str = "";
}

glob Nodes = {
    "CodeFile": CodeFile,
    "CodeRepo": CodeRepo
};