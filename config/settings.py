"""Configuration settings for Codebase Genius"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
TEMP_DIR = BASE_DIR / "temp_repos"
OUTPUT_DIR = BASE_DIR / "outputs"
LOGS_DIR = BASE_DIR / "logs"

TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

MAX_FILES_TO_ANALYZE = int(os.getenv("MAX_FILES", "50"))
TARGET_LANGUAGES = ["Python", "Jac"]
CLONE_TIMEOUT = 300
IGNORE_DIRS = [".git", "node_modules", "__pycache__", ".venv", "venv"]
IGNORE_FILES = [".pyc", ".pyo", ".so"]
