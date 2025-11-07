"""LLM Configuration"""
import os
from byllm llm import Model

def get_llm_instance():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    return Model(model_name=os.getenv("OPENAI_MODEL", "gpt-4-turbo"))
