from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.models.assessments import Assessment, AssessmentAttempt, Question
from app.schemas.assessment import (
    AssessmentListResponse,
    AssessmentDetailResponse,
    AssessmentSubmitRequest,
    AssessmentResultResponse
)
from app.services.assessments.engine import submit_and_evaluate_assessment
from app.services.ai.gap_assessment_generator import generate_ai_assessment_for_gaps
from app.services.skill_gap.ai_engine import get_user_ai_profile
from app.api.deps import get_current_user
from app.services.audit.service import log_audit_event

router = APIRouter(prefix="/assessments", tags=["Assessments"])


@router.post("/generate-for-gaps", response_model=AssessmentListResponse)
async def create_assessment_for_my_gaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_user_ai_profile(db, current_user.id)
    gap_skills = []
    if profile and "gaps" in profile:
        gap_skills = [g.get("skill") for g in profile["gaps"] if g.get("skill")]

    role = profile.get("target_role") if profile else (current_user.designation_name or "Software Engineer")
    assessment = await generate_ai_assessment_for_gaps(db, current_user.id, gap_skills, role)

    return AssessmentListResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        assessment_type=assessment.assessment_type,
        competency_id=assessment.competency_id,
        competency_name=f"Skill Gaps: {', '.join(gap_skills[:2])}" if gap_skills else "General Evaluation",
        difficulty=assessment.difficulty,
        duration_minutes=assessment.duration_minutes,
        passing_score=assessment.passing_score,
        question_count=len(assessment.questions)
    )


@router.get("", response_model=List[AssessmentListResponse])
def list_assessments(db: Session = Depends(get_db)):
    assessments = db.query(Assessment).filter(Assessment.active == True).all()
    results = []
    for a in assessments:
        comp = a.questions[0].competency_rel if a.questions else None
        results.append(AssessmentListResponse(
            id=a.id,
            title=a.title,
            description=a.description,
            assessment_type=a.assessment_type,
            competency_id=a.competency_id,
            competency_name=comp.name if comp else None,
            difficulty=a.difficulty,
            duration_minutes=a.duration_minutes,
            passing_score=a.passing_score,
            question_count=len(a.questions)
        ))
    return results


@router.get("/{assessment_id}", response_model=AssessmentDetailResponse)
def get_assessment_detail(assessment_id: str, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    comp = assessment.questions[0].competency_rel if assessment.questions else None
    return AssessmentDetailResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        assessment_type=assessment.assessment_type,
        competency_id=assessment.competency_id,
        competency_name=comp.name if comp else None,
        difficulty=assessment.difficulty,
        duration_minutes=assessment.duration_minutes,
        passing_score=assessment.passing_score,
        question_count=len(assessment.questions),
        questions=assessment.questions
    )


@router.post("/{assessment_id}/start")
def start_assessment_attempt(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")

    attempt = AssessmentAttempt(
        user_id=current_user.id,
        assessment_id=assessment.id,
        status="IN_PROGRESS"
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    log_audit_event(db, action="ASSESSMENT_STARTED", resource="Assessment", actor_id=current_user.id, resource_id=assessment_id)
    return {"attempt_id": attempt.id, "started_at": attempt.started_at}


@router.post("/{assessment_id}/submit", response_model=AssessmentResultResponse)
def submit_assessment(
    assessment_id: str,
    submission: AssessmentSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        result = submit_and_evaluate_assessment(db=db, user_id=current_user.id, submission=submission)
        log_audit_event(
            db,
            action="ASSESSMENT_SUBMITTED",
            resource="Assessment",
            actor_id=current_user.id,
            resource_id=assessment_id,
            details={"score": result.score_percentage, "passed": result.passed}
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
