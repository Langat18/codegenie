"""LLM Configuration"""
import os
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from openai import AsyncOpenAI

class LLMConfig:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        self._client = None

    @asynccontextmanager
    async def get_client(self):
        if not self._client:
            self._client = AsyncOpenAI(api_key=self.api_key)
        try:
            yield self._client
        finally:
            await self._client.close()

    async def get_completion(self, prompt: str, **kwargs) -> Dict[str, Any]:
        async with self.get_client() as client:
            try:
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0.7),
                    max_tokens=kwargs.get('max_tokens', 1000)
                )
                return {"status": "success", "content": response.choices[0].message.content}
            except Exception as e:
                return {"status": "error", "error": str(e)}
