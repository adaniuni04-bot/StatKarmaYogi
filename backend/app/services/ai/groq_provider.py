import json
import re
from typing import Optional, Dict, Any, List
import httpx
from app.services.ai.base import LLMProvider
from app.core.config import settings
from app.core.logging import logger

FALLBACK_MODELS = [
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile"
]


class GroqLLMProvider(LLMProvider):
    """
    Groq Cloud Console LLM Provider.
    Enables ultra-fast cloud inference for Qwen 3.8 models
    without requiring any local GPU or Ollama process.
    Compatible with Groq Cloud (https://console.groq.com) and xAI Grok.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or settings.GROQ_API_KEY or settings.GROK_API_KEY
        self.base_url = (base_url or settings.GROQ_BASE_URL).rstrip("/")
        self.model = model or settings.GROQ_MODEL or settings.GROK_MODEL or "qwen/qwen3.8-27b"
        self._working_model = self.model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def _clean_response(self, text: str) -> str:
        """Strip reasoning and thought tags common in Qwen models."""
        if not text:
            return ""
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        cleaned = re.sub(r'<thought>.*?</thought>', '', cleaned, flags=re.DOTALL)
        return cleaned.strip()

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        if not self.is_configured:
            logger.warning("GROQ_API_KEY is not configured yet. Returning fallback response.")
            return (
                "**Groq Qwen Engine Notice**: GROQ_API_KEY is not configured yet. "
                "Please add your free Groq API key from https://console.groq.com/keys "
                "into the .env file (GROQ_API_KEY=gsk_...) to enable live cloud AI inference."
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "StatKarmaYogi/1.0 (Windows NT 10.0; Win64; x64)",
            "Content-Type": "application/json"
        }

        candidate_models = [self._working_model] + [m for m in FALLBACK_MODELS if m != self._working_model]

        last_error = None
        for candidate in candidate_models:
            payload = {
                "model": candidate,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.2),
                "max_tokens": kwargs.get("max_tokens", 2048)
            }

            try:
                logger.info(f"Groq Cloud Qwen model '{candidate}' generating response...")
                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    if resp.status_code == 404 or resp.status_code == 400:
                        logger.warning(f"Model '{candidate}' error on Groq ({resp.text[:120]}), attempting alternate candidate...")
                        continue

                    resp.raise_for_status()
                    data = resp.json()
                    self._working_model = candidate
                    raw_content = data["choices"][0]["message"]["content"]
                    logger.info(f"Groq Cloud Qwen response received successfully ({len(raw_content)} chars)")
                    return self._clean_response(raw_content)
            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"Groq API error with model '{candidate}': {e.response.status_code} - {e.response.text[:120]}")
                if e.response.status_code == 401:
                    raise ValueError(f"Invalid Groq API Key: {e.response.text}")
                continue
            except Exception as e:
                last_error = e
                logger.warning(f"Groq request exception with model '{candidate}': {e}")
                continue

        if last_error:
            raise last_error
        raise RuntimeError("Failed to generate response from Groq API across candidate models")

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Output valid strict JSON only. Do not wrap in markdown or include conversational text."
        raw_text = await self.generate(enhanced_prompt, system_prompt, **kwargs)
        cleaned = self._clean_response(raw_text)

        match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', cleaned)
        if match:
            clean_json_str = match.group(0)
        else:
            clean_json_str = cleaned.strip().replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(clean_json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to decode JSON from Groq response: {e}. Raw content: {cleaned[:200]}")
            return {"error": "Invalid JSON returned", "raw": cleaned}

    async def summarize(self, text: str, max_words: int = 150) -> str:
        prompt = f"Summarize the following technical content in under {max_words} words:\n\n{text}"
        return await self.generate(prompt)
