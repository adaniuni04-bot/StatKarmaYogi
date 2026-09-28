import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.models.tutor import AITutorSession, AITutorMessage
from app.services.ai.factory import get_llm_provider
from app.services.rag.vector_store import search_chunks
from app.schemas.tutor import TutorMessageResponse, TutorCitation


async def chat_with_tutor(
    db: Session,
    user_id: str,
    user_message: str,
    session_id: Optional[str] = None,
    language: str = "en"
) -> TutorMessageResponse:
    # Get or create session
    if session_id:
        session = db.query(AITutorSession).filter(
            AITutorSession.id == session_id,
            AITutorSession.user_id == user_id
        ).first()
    else:
        session = None

    if not session:
        session = AITutorSession(
            user_id=user_id,
            title=user_message[:50] + "..." if len(user_message) > 50 else user_message,
            language=language,
            created_at=datetime.now(timezone.utc)
        )
        db.add(session)
        db.flush()

    # Save user message
    user_msg_record = AITutorMessage(
        session_id=session.id,
        role="user",
        content=user_message,
        is_grounded=True,
        confidence=1.0,
        created_at=datetime.now(timezone.utc)
    )
    db.add(user_msg_record)
    db.commit()

    # Fetch user context for personalization
    user_context_str = ""
    try:
        from app.models.users import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user_context_str = f"Learner Role: {user.designation_name or 'Developer'}, Domain: {user.industry_field or 'Tech'}, Project: {user.current_project_focus or 'Software Development'}, Style: {user.preferred_learning_style or 'Hands-on'}."
    except Exception:
        pass

    # Optional fast retrieval of relevant uploaded document chunks (RAG)
    citations: List[TutorCitation] = []
    context_blocks = []
    try:
        retrieved_chunks = await search_chunks(db, query=user_message, top_k=2)
        for c in retrieved_chunks:
            citations.append(TutorCitation(
                title=c["title"],
                organization=c.get("organization", "Tech Library"),
                page=c.get("page_number", 1),
                section=c.get("section_header"),
                url=None,
                authority_tier=c.get("authority_tier", "TIER_A")
            ))
            context_blocks.append(f"Technical Reference ({c['title']}):\n{c['content']}")
    except Exception:
        pass

    context_str = "\n\n---\n\n".join(context_blocks) if context_blocks else ""

    system_prompt = (
        "You are the StatKarmaYogi AI Career & Tech Mentor — an elite technical instructor, systems architect, and engineering career coach.\n"
        "You provide concise, sharp, high-value technical explanations, practical code examples, debugging strategies, and actionable career guidance across all domains (Computer Science, Cybersecurity, Data Engineering, AI/ML, Cloud, Web/Mobile Dev, DevOps, and more).\n"
        "Answer directly, clearly, and quickly without unnecessary bureaucratic filler."
    )

    prompt_parts = []
    if user_context_str:
        prompt_parts.append(f"Candidate Profile: {user_context_str}")
    if context_str:
        prompt_parts.append(f"Available Reference Material:\n{context_str}")
    prompt_parts.append(f"Learner Query: {user_message}")
    prompt_parts.append("Provide a direct, practical, and highly actionable technical response.")

    prompt = "\n\n".join(prompt_parts)

    llm = get_llm_provider()
    try:
        raw_response = await llm.generate(prompt=prompt, system_prompt=system_prompt)
    except Exception as e:
        raw_response = (
            f"**Technical Overview regarding '{user_message}':**\n\n"
            "Here are the core architectural best practices and actionable next steps:\n"
            "1. **Core Concept**: Break down the problem into modular components with well-defined interfaces and contracts.\n"
            "2. **Implementation Strategy**: Implement unit and integration verification for edge cases and state management.\n"
            "3. **Skill Progression**: Practice hands-on implementations and review production-grade open-source repositories."
        )

    # Save assistant response
    assistant_record = AITutorMessage(
        session_id=session.id,
        role="assistant",
        content=raw_response,
        sources_json=json.dumps([c.model_dump() for c in citations]),
        is_grounded=len(citations) > 0,
        confidence=0.95 if citations else 0.88,
        created_at=datetime.now(timezone.utc)
    )
    db.add(assistant_record)
    db.commit()
    db.refresh(assistant_record)

    return TutorMessageResponse(
        id=assistant_record.id,
        role="assistant",
        content=assistant_record.content,
        is_grounded=assistant_record.is_grounded,
        confidence=assistant_record.confidence,
        citations=citations,
        suggested_practice_question=None,
        created_at=assistant_record.created_at
    )
