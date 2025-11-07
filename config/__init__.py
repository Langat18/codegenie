"""
Configuration package for Codebase Genius
"""

from .settings import *
from .llm_config import get_llm, summarize_readme, generate_documentation_section

__all__ = [
    'get_llm',
    'summarize_readme',
    'generate_documentation_section',
    'GEMINI_API_KEY',
    'LLM_PROVIDER',
    'LLM_MODEL'
]