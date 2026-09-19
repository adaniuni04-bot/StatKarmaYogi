import json
from typing import Optional, Dict, Any, List
import httpx
from app.services.ai.base import LLMProvider, EmbeddingProvider
from app.core.config import settings
from app.core.logging import logger


class GeminiLLMProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model = "gemini-1.5-flash"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {"contents": contents}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Respond strictly with valid JSON without markdown wrapping."
        text_resp = await self.generate(enhanced_prompt, system_prompt)
        text_clean = text_resp.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text_clean)

    async def summarize(self, text: str, max_words: int = 150) -> str:
        prompt = f"Summarize the following official statistical text in under {max_words} words:\n\n{text}"
        return await self.generate(prompt)


class GeminiEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"

    async def embed_text(self, text: str) -> List[float]:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured")

        url = f"{self.base_url}?key={self.api_key}"
        payload = {"content": {"parts": [{"text": text}]}}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["embedding"]["values"]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for t in texts:
            vec = await self.embed_text(t)
            results.append(vec)
        return results
