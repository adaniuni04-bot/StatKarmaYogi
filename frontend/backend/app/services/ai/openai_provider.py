import json
from typing import Optional, Dict, Any, List
import httpx
from app.services.ai.base import LLMProvider, EmbeddingProvider
from app.core.config import settings


class OpenAICompatibleLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url
        self.model = "gpt-4o-mini"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "messages": messages, "temperature": 0.3}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        enhanced_prompt = f"{prompt}\n\nRespond with strict JSON."
        text_resp = await self.generate(enhanced_prompt, system_prompt)
        text_clean = text_resp.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text_clean)

    async def summarize(self, text: str, max_words: int = 150) -> str:
        prompt = f"Summarize in under {max_words} words:\n\n{text}"
        return await self.generate(prompt)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url
        self.model = "text-embedding-3-small"

    async def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "input": text}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["embedding"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"model": self.model, "input": texts}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]
