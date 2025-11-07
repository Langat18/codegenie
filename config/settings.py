import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Google Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-pro")

# Server Configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Path Configuration
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "./outputs"))
TEMP_DIR = Path(os.getenv("TEMP_DIR", "./temp_repos"))
LOG_FILE = Path(os.getenv("LOG_FILE", "./logs/codebase_genius.log"))

# Create directories
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOG_FILE.parent.mkdir(exist_ok=True)

# Repository Configuration
MAX_REPO_SIZE_MB = int(os.getenv("MAX_REPO_SIZE_MB", "500"))
CLONE_TIMEOUT_SECONDS = int(os.getenv("CLONE_TIMEOUT_SECONDS", "300"))
IGNORED_DIRS = os.getenv(
    "IGNORED_DIRS",
    ".git,node_modules,venv,.venv,__pycache__,.pytest_cache,dist,build"
).split(",")

# Code Analysis Configuration
MAX_FILE_SIZE_KB = int(os.getenv("MAX_FILE_SIZE_KB", "1024"))
MAX_FILES_TO_ANALYZE = int(os.getenv("MAX_FILES_TO_ANALYZE", "1000"))
PARSE_TIMEOUT_SECONDS = int(os.getenv("PARSE_TIMEOUT_SECONDS", "30"))

# Documentation Configuration
INCLUDE_DIAGRAMS = os.getenv("INCLUDE_DIAGRAMS", "true").lower() == "true"
DIAGRAM_FORMAT = os.getenv("DIAGRAM_FORMAT", "mermaid")
MAX_DIAGRAM_NODES = int(os.getenv("MAX_DIAGRAM_NODES", "50"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Rate Limiting
MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "3"))

# Priority file patterns
PRIORITY_PATTERNS = [
    "main.py",
    "app.py",
    "__init__.py",
    "index.py",
    "setup.py",
    "main.jac",
    "app.jac",
    "server.jac"
]

# Supported file extensions
SUPPORTED_EXTENSIONS = {
    "python": [".py"],
    "jac": [".jac"],
    "javascript": [".js", ".jsx", ".ts", ".tsx"],
    "java": [".java"],
    "cpp": [".cpp", ".cc", ".cxx", ".h", ".hpp"]
}

DOC_SECTIONS = [
    "overview",
    "installation",
    "architecture",
    "api_reference",
    "usage_examples",
    "dependencies",
    "contributing"
]


def validate_config():
    """Validate configuration"""
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required in .env file")
    
    if LLM_PROVIDER != "gemini":
        print(f"Warning: LLM_PROVIDER is set to '{LLM_PROVIDER}' but Gemini API key is configured")
    
    return True


# Validate on import
try:
    validate_config()
    print(f"✓ Configuration loaded successfully")
    print(f"  Provider: {LLM_PROVIDER}")
    print(f"  Model: {LLM_MODEL}")
except ValueError as e:
    print(f"✗ Configuration error: {e}")