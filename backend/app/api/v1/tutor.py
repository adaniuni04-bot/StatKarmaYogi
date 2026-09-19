import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.models.tutor import AITutorSession, AITutorMessage
from app.schemas.tutor import TutorChatRequest, TutorMessageResponse, TutorSessionResponse, TutorCitation
from app.services.tutor.service import chat_with_tutor
from app.api.deps import get_current_user

router = APIRouter(prefix="/tutor", tags=["AI Tutor"])


@router.post("/chat", response_model=TutorMessageResponse)
async def tutor_chat(
    request: TutorChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await chat_with_tutor(
        db=db,
        user_id=current_user.id,
        user_message=request.message,
        session_id=request.session_id,
        language=request.language or "en"
    )


@router.get("/sessions", response_model=List[TutorSessionResponse])
def list_tutor_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(AITutorSession).filter(
        AITutorSession.user_id == current_user.id
    ).order_by(AITutorSession.updated_at.desc()).all()

    results = []
    for s in sessions:
        results.append(TutorSessionResponse(
            id=s.id,
            title=s.title,
            topic=s.topic,
            language=s.language,
            created_at=s.created_at,
            messages=[]
        ))
    return results


@router.get("/sessions/{session_id}", response_model=TutorSessionResponse)
def get_tutor_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(AITutorSession).filter(
        AITutorSession.id == session_id,
        AITutorSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tutor session not found")

    messages_resp = []
    for m in session.messages:
        citations = []
        if m.sources_json:
            try:
                raw_cits = json.loads(m.sources_json)
                citations = [TutorCitation(**c) for c in raw_cits]
            except Exception:
                pass

        messages_resp.append(TutorMessageResponse(
            id=m.id,
            role=m.role,
            content=m.content,
            is_grounded=m.is_grounded,
            confidence=m.confidence,
            citations=citations,
            suggested_practice_question=m.suggested_practice_question,
            created_at=m.created_at
        ))

    return TutorSessionResponse(
        id=session.id,
        title=session.title,
        topic=session.topic,
        language=session.language,
        created_at=session.created_at,
        messages=messages_resp
    )
