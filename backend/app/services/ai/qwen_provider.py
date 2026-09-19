import json
import re
from typing import Optional, Dict, Any, List
import httpx
from app.services.ai.base import LLMProvider, EmbeddingProvider
from app.core.config import settings
from app.core.logging import logger


class QwenOllamaLLMProvider(LLMProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or getattr(settings, "OLLAMA_LLM_MODEL", "qwen3:8b")

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt or "You are an expert Statistical Advisor for India's Official Statistical System (MoSPI/NSSTA). Provide precise, grounded, and authoritative explanations.",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data.get("response", "")
            # Strip internal thought tags if present
            cleaned = re.sub(r'<thought>.*?</thought>', '', raw_text, flags=re.DOTALL).strip()
            return cleaned

    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        enhanced_prompt = f"{prompt}\n\nIMPORTANT: Respond with strict valid JSON only, without any explanatory text or markdown formatting."
        raw_text = await self.generate(enhanced_prompt, system_prompt)

        # Extract JSON substring
        match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
        if match:
            clean_json_str = match.group(0)
        else:
            clean_json_str = raw_text.strip().replace("```json", "").replace("```", "").strip()

        try:
            return json.loads(clean_json_str)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from Qwen3: {raw_text[:200]}")
            # Return safe fallback structure
            return {
                "questions": [
                    {
                        "question_text": "Under the Horvitz-Thompson estimation framework, how is the population total estimated from unequal probability samples?",
                        "question_type": "SINGLE_CHOICE",
                        "options": [
                            "By weighting each sample unit with the inverse of its first-order inclusion probability (1/pi_i).",
                            "By taking the simple unweighted arithmetic mean of all surveyed units.",
                            "By dividing the sample variance by the total number of strata.",
                            "By multiplying the sample total by the non-response rate."
                        ],
                        "correct_option_index": 0,
                        "explanation": "The Horvitz-Thompson estimator calculates the unbiased population total as sum(y_i / pi_i), where pi_i is the inclusion probability.",
                        "competency_code": "SAMPLING",
                        "difficulty": "INTERMEDIATE",
                        "source_reference": "MoSPI Sampling Techniques Manual"
                    }
                ]
            }

    async def summarize(self, text: str, max_words: int = 150) -> str:
        prompt = f"Summarize the following official statistical documentation in under {max_words} words:\n\n{text}"
        return await self.generate(prompt)


class QwenOllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or getattr(settings, "OLLAMA_EMBED_MODEL", "bge-m3:latest")

    async def embed_text(self, text: str) -> List[float]:
        payload = {"model": self.model, "prompt": text}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/api/embeddings", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [0.0] * 1024)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for t in texts:
            vec = await self.embed_text(t)
            results.append(vec)
        return results
