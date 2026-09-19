from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.models.assessments import Question, QuestionOption
from app.schemas.quiz import (
    MCQGenerateRequest,
    MCQGenerateResponse,
    QuestionReviewActionRequest
)
from app.services.quiz.generator import generate_mcqs_pipeline
from app.api.deps import get_current_user, RoleChecker
from app.services.audit.service import log_audit_event

router = APIRouter(prefix="/quiz", tags=["AI Quiz & Question Review"])


@router.post("/generate", response_model=MCQGenerateResponse)
async def generate_questions(
    request: MCQGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = await generate_mcqs_pipeline(db, request)
    log_audit_event(
        db,
        action="QUESTION_GENERATED",
        resource="Question",
        actor_id=current_user.id,
        details={"count": result.total_generated, "competency": request.competency_code}
    )
    return result


@router.get("/questions")
def list_reviewable_questions(
    validation_status: Optional[str] = None,
    competency_code: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    if validation_status:
        query = query.filter(Question.validation_status == validation_status.upper())
    if competency_code:
        query = query.filter(Question.competency_rel.has(code=competency_code.upper()))

    questions = query.order_by(Question.created_at.desc()).all()
    results = []
    for q in questions:
        results.append({
            "id": q.id,
            "competency_code": q.competency_rel.code if q.competency_rel else "GENERAL",
            "competency_name": q.competency_rel.name if q.competency_rel else "General",
            "question_text": q.question_text,
            "difficulty": q.difficulty,
            "validation_status": q.validation_status,
            "ai_validation_score": q.ai_validation_score,
            "validation_feedback": q.validation_feedback,
            "source_reference": q.source_reference,
            "options": [{"id": o.id, "text": o.option_text, "is_correct": o.is_correct} for o in q.options]
        })
    return results


@router.post("/questions/{question_id}/review")
def review_question(
    question_id: str,
    action_data: QuestionReviewActionRequest,
    current_user: User = Depends(RoleChecker(["TRAINER", "ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    act = action_data.action.upper()
    if act == "APPROVE":
        question.validation_status = "APPROVED"
    elif act == "PUBLISH":
        question.validation_status = "PUBLISHED"
    elif act == "REJECT":
        question.validation_status = "REJECTED"
    elif act == "EDIT":
        if action_data.edited_text:
            question.question_text = action_data.edited_text
        if action_data.edited_explanation:
            question.explanation = action_data.edited_explanation
        question.validation_status = "VALIDATED"

    db.commit()
    db.refresh(question)

    log_audit_event(
        db,
        action=f"QUESTION_{act}",
        resource="Question",
        actor_id=current_user.id,
        resource_id=question.id
    )

    return {"status": "success", "question_id": question.id, "validation_status": question.validation_status}
