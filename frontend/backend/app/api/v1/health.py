from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings

router = APIRouter(tags=["Health & Readiness"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "India Official Statistical System Skill Intelligence Platform",
        "environment": settings.ENVIRONMENT
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ready" if db_status == "ok" else "degraded",
        "components": {
            "database": db_status,
            "llm_provider": settings.LLM_PROVIDER,
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "demo_mode": settings.DEMO_MODE,
            "igot_mode": settings.IGOT_MODE,
            "nssta_mode": settings.NSSTA_MODE
        }
    }


@router.get("/admin/ai-settings")
def get_ai_settings():
    """Rule 123: Admin sees provider info, never exposing secrets."""
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "demo_mode": settings.DEMO_MODE,
        "vector_dimension": settings.VECTOR_DIMENSION,
        "rag_top_k": settings.RAG_TOP_K,
        "rag_similarity_threshold": settings.RAG_SIMILARITY_THRESHOLD,
        "fallback_provider": settings.AI_FALLBACK_PROVIDER,
        "upload_max_mb": settings.UPLOAD_MAX_MB,
        "weights": {
            "self_assessment": settings.WEIGHT_SELF_ASSESSMENT,
            "knowledge_assessment": settings.WEIGHT_KNOWLEDGE_ASSESSMENT,
            "practical_assessment": settings.WEIGHT_PRACTICAL_ASSESSMENT,
            "training_evidence": settings.WEIGHT_TRAINING_EVIDENCE
        }
    }
