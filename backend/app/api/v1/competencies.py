from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User, Designation
from app.models.competencies import (
    CompetencyDomain,
    Competency,
    RoleCompetency,
    UserCompetency,
    CompetencyHistory
)
from app.schemas.competency import (
    CompetencyDomainResponse,
    CompetencyResponse,
    RoleCompetencyResponse,
    UserCompetencyResponse,
    CompetencyHistoryResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/competencies", tags=["Competencies"])


@router.get("", response_model=List[CompetencyDomainResponse])
def list_competency_framework(db: Session = Depends(get_db)):
    domains = db.query(CompetencyDomain).all()
    return [CompetencyDomainResponse.model_validate(d) for d in domains]


@router.get("/me", response_model=List[UserCompetencyResponse])
def get_my_competencies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_comps = db.query(UserCompetency).filter(UserCompetency.user_id == current_user.id).all()
    result = []
    for uc in user_comps:
        comp = uc.competency
        domain = comp.domain if comp else None
        result.append(UserCompetencyResponse(
            id=uc.id,
            competency_id=uc.competency_id,
            competency_name=comp.name if comp else "Unknown",
            competency_code=comp.code if comp else "UNKNOWN",
            domain_code=domain.code if domain else "GENERAL",
            domain_name=domain.name if domain else "General",
            score=uc.score,
            level=uc.level,
            level_name=uc.level_name,
            confidence=uc.confidence,
            evidence_count=uc.evidence_count,
            last_assessed_at=uc.last_assessed_at,
            source=uc.source
        ))
    return result


@router.get("/history", response_model=List[CompetencyHistoryResponse])
def get_my_competency_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history = db.query(CompetencyHistory).filter(
        CompetencyHistory.user_id == current_user.id
    ).order_by(CompetencyHistory.created_at.desc()).all()

    result = []
    for h in history:
        comp = db.query(Competency).filter(Competency.id == h.competency_id).first()
        result.append(CompetencyHistoryResponse(
            id=h.id,
            competency_id=h.competency_id,
            competency_name=comp.name if comp else "Skill",
            previous_score=h.previous_score,
            new_score=h.new_score,
            delta=h.delta,
            reason=h.reason,
            created_at=h.created_at
        ))
    return result


@router.get("/roles/{designation_id}", response_model=List[RoleCompetencyResponse])
def get_role_competency_requirements(
    designation_id: str,
    db: Session = Depends(get_db)
):
    rcs = db.query(RoleCompetency).filter(RoleCompetency.designation_id == designation_id).all()
    results = []
    for rc in rcs:
        results.append(RoleCompetencyResponse(
            id=rc.id,
            designation_id=rc.designation_id,
            competency_id=rc.competency_id,
            competency_name=rc.competency.name,
            competency_code=rc.competency.code,
            domain_code=rc.competency.domain.code if rc.competency.domain else "GENERAL",
            required_level=rc.required_level,
            required_score=rc.required_score,
            importance=rc.importance,
            mandatory=rc.mandatory,
            future_relevance=rc.future_relevance
        ))
    return results


@router.get("/{competency_id}", response_model=CompetencyResponse)
def get_competency_detail(competency_id: str, db: Session = Depends(get_db)):
    comp = db.query(Competency).filter(Competency.id == competency_id).first()
    if not comp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competency not found")
    return CompetencyResponse.model_validate(comp)
