from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate a natural language text response."""
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate structured JSON conforming to expected output."""
        pass

    @abstractmethod
    async def summarize(self, text: str, max_words: int = 150) -> str:
        """Summarize text content."""
        pass


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate a vector embedding for a single text string."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text strings."""
        pass
