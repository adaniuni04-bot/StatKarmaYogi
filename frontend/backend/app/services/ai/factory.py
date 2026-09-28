from app.core.config import settings
from app.core.logging import logger
from app.services.ai.base import LLMProvider, EmbeddingProvider
from app.services.ai.mock_provider import MockLLMProvider, MockEmbeddingProvider
from app.services.ai.gemini_provider import GeminiLLMProvider, GeminiEmbeddingProvider
from app.services.ai.openai_provider import OpenAICompatibleLLMProvider, OpenAIEmbeddingProvider
from app.services.ai.qwen_provider import QwenOllamaLLMProvider, QwenOllamaEmbeddingProvider
from app.services.ai.groq_provider import GroqLLMProvider


def get_llm_provider() -> LLMProvider:
    provider_type = settings.LLM_PROVIDER.lower()

    # 1. Groq / Grok Cloud Console (Primary for Qwen cloud inference)
    has_groq_key = bool(settings.GROQ_API_KEY or settings.GROK_API_KEY)
    if provider_type in ["groq", "grok"]:
        if has_groq_key:
            return GroqLLMProvider()
        else:
            logger.info("GROQ_API_KEY is not configured in .env yet. Using fallback provider until key is added.")
            return MockLLMProvider()

    # Auto-detect Groq if key is present even if LLM_PROVIDER was not explicitly set
    if has_groq_key:
        return GroqLLMProvider()

    # 2. Local Ollama (Qwen)
    if provider_type == "qwen":
        return QwenOllamaLLMProvider()

    # 3. Gemini
    elif provider_type == "gemini" and settings.GEMINI_API_KEY:
        try:
            return GeminiLLMProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini provider ({e}), falling back to MockLLMProvider")
            return MockLLMProvider()

    # 4. OpenAI
    elif provider_type == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAICompatibleLLMProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI provider ({e}), falling back to MockLLMProvider")
            return MockLLMProvider()

    return MockLLMProvider()


def get_embedding_provider() -> EmbeddingProvider:
    provider_type = settings.EMBEDDING_PROVIDER.lower()

    if provider_type in ["mock", "groq", "grok"]:
        return MockEmbeddingProvider(dimension=settings.VECTOR_DIMENSION)

    if provider_type == "qwen":
        return QwenOllamaEmbeddingProvider()

    elif provider_type == "gemini" and settings.GEMINI_API_KEY:
        try:
            return GeminiEmbeddingProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini embedding ({e}), falling back to MockEmbeddingProvider")
            return MockEmbeddingProvider()

    elif provider_type == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAIEmbeddingProvider()
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI embedding ({e}), falling back to MockEmbeddingProvider")
            return MockEmbeddingProvider()

    return MockEmbeddingProvider(dimension=settings.VECTOR_DIMENSION)
