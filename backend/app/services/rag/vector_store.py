import json
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.documents import Document, DocumentChunk
from app.services.ai.factory import get_embedding_provider
from app.services.rag.authority import get_authority_multiplier


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


async def search_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    competency_code: Optional[str] = None
) -> List[Dict[str, Any]]:
    embedder = get_embedding_provider()
    query_vec = await embedder.embed_text(query)

    query_builder = db.query(DocumentChunk).join(Document)
    if competency_code and competency_code != "ALL":
        query_builder = query_builder.filter(DocumentChunk.competency_code == competency_code)

    chunks = query_builder.all()
    if not chunks:
        return []

    scored_chunks = []
    for chunk in chunks:
        if not chunk.embedding_json:
            continue
        try:
            chunk_vec = json.loads(chunk.embedding_json)
        except Exception:
            continue

        raw_sim = cosine_similarity(query_vec, chunk_vec)
        tier = chunk.document.authority_tier if chunk.document else "TIER_A"
        multiplier = get_authority_multiplier(tier)
        weighted_score = round(raw_sim * multiplier, 4)

        scored_chunks.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "title": chunk.document.title if chunk.document else "Statistical Document",
            "organization": chunk.document.source_organization if chunk.document else "MoSPI",
            "authority_tier": tier,
            "page_number": chunk.page_number,
            "section_header": chunk.section_header,
            "competency_code": chunk.competency_code,
            "content": chunk.content,
            "similarity_score": weighted_score
        })

    # Sort descending by score
    scored_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored_chunks[:top_k]
