from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    PROJECT_NAME: str = "National Statistical Skill Intelligence Platform"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"
    DEMO_MODE: bool = False

    # Security & Auth
    SECRET_KEY: str = "gov-stat-skill-intelligence-secret-key-2026-super-secure"
    JWT_SECRET: str = "gov-stat-jwt-secret-key-super-secure-2026-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "sqlite+pysqlite:///./stat_skills.db"
    VECTOR_DIMENSION: int = 1024  # Matched to BGE-M3 1024-dim embeddings

    # AI & RAG Configuration (Groq Cloud Console with Qwen models)
    LLM_PROVIDER: str = "groq"
    EMBEDDING_PROVIDER: str = "mock"

    # Groq Cloud Console API (https://console.groq.com)
    GROQ_API_KEY: Optional[str] = None
    GROK_API_KEY: Optional[str] = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "qwen/qwen3.8-27b"
    GROK_MODEL: Optional[str] = None

    # Alternative / Local Providers
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_LLM_MODEL: str = "qwen3:8b"
    OLLAMA_EMBED_MODEL: str = "bge-m3:latest"

    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    AI_FALLBACK_PROVIDER: str = "mock"
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.65

    # Integration Modes
    IGOT_MODE: str = "live"
    NSSTA_MODE: str = "live"

    # File uploads
    UPLOAD_MAX_MB: int = 25
    ALLOWED_EXTENSIONS: Union[List[str], str] = ["pdf", "docx", "pptx", "txt"]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def adjust_database_url(cls, v):
        import os
        if not v or not isinstance(v, str):
            v = "sqlite+pysqlite:///./stat_skills.db"
        # If running on Vercel Serverless and using SQLite, redirect to writable /tmp
        if os.environ.get("VERCEL") and "sqlite" in v and "/tmp" not in v:
            return "sqlite+pysqlite:////tmp/stat_skills.db"
        # Normalize postgres:// to postgresql+psycopg://
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg://", 1)
        if v.startswith("postgresql://") and "+psycopg" not in v and "+asyncpg" not in v:
            return v.replace("postgresql://", "postgresql+psycopg://", 1)
        return v

    @field_validator("GROQ_API_KEY", "GROK_API_KEY", mode="before")
    @classmethod
    def parse_groq_api_key(cls, v):
        if isinstance(v, str):
            v_clean = v.strip()
            return v_clean if len(v_clean) > 5 else None
        return v


    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                try:
                    import json
                    return json.loads(v_clean)
                except Exception:
                    pass
            return [ext.strip().lstrip(".") for ext in v_clean.split(",") if ext.strip()]
        return v

    # Deterministic Competency Evidence Weights (Must equal 1.0)
    WEIGHT_SELF_ASSESSMENT: float = 0.10
    WEIGHT_KNOWLEDGE_ASSESSMENT: float = 0.35
    WEIGHT_PRACTICAL_ASSESSMENT: float = 0.40
    WEIGHT_TRAINING_EVIDENCE: float = 0.15

    # Deterministic Recommendation Weights (Must equal 1.0)
    WEIGHT_SKILL_GAP: float = 0.35
    WEIGHT_ROLE_RELEVANCE: float = 0.20
    WEIGHT_DIFFICULTY_SUITABILITY: float = 0.15
    WEIGHT_LEARNING_HISTORY: float = 0.10
    WEIGHT_CAREER_RELEVANCE: float = 0.10
    WEIGHT_DEPARTMENT_PRIORITY: float = 0.05
    WEIGHT_FRESHNESS: float = 0.05

    # Proficiency Level Thresholds
    LEVEL_1_MAX: int = 20   # Foundation: 0-20
    LEVEL_2_MAX: int = 40   # Basic: 21-40
    LEVEL_3_MAX: int = 60   # Intermediate: 41-60
    LEVEL_4_MAX: int = 80   # Advanced: 61-80
    LEVEL_5_MAX: int = 100  # Expert: 81-100

    # Role Readiness Thresholds
    ROLE_READINESS_READY_THRESHOLD: float = 85.0
    ROLE_READINESS_NEAR_READY_THRESHOLD: float = 65.0


settings = Settings()
