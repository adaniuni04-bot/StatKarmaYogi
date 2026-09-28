from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.models.resources import Resource
from app.models.learning import LearningPath, Enrollment
from app.schemas.learning import LearningPathResponse, EnrollmentResponse
from app.services.learning.path_engine import generate_or_update_learning_path
from app.api.deps import get_current_user

router = APIRouter(prefix="/learning", tags=["Learning & Resources"])


@router.get("/paths/me", response_model=LearningPathResponse)
def get_my_learning_path(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_or_update_learning_path(db, current_user.id)


@router.post("/paths/recalculate", response_model=LearningPathResponse)
def recalculate_path(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_or_update_learning_path(db, current_user.id)


@router.get("/resources")
def list_resources(
    provider: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Resource).filter(Resource.active == True)
    if provider:
        query = query.filter(Resource.provider == provider.upper())
    if difficulty:
        query = query.filter(Resource.difficulty == difficulty.upper())
    if search:
        query = query.filter(Resource.title.ilike(f"%{search}%"))

    resources = query.all()
    results = []
    for r in resources:
        results.append({
            "id": r.id,
            "title": r.title,
            "description": r.description,
            "provider": r.provider,
            "resource_type": r.resource_type,
            "url": r.url,
            "duration_minutes": r.duration_minutes,
            "difficulty": r.difficulty,
            "language": r.language,
            "authority_tier": r.authority_tier,
            "source_organization": r.source_organization,
            "mock_data": r.mock_data,
        })
    return results


@router.get("/resources/{resource_id}")
def get_resource(resource_id: str, db: Session = Depends(get_db)):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")
    return res


@router.post("/resources/{resource_id}/enroll")
def enroll_in_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = db.query(Resource).filter(Resource.id == resource_id).first()
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    existing = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.resource_id == resource_id
    ).first()

    if existing:
        return {"status": "already_enrolled", "enrollment_id": existing.id}

    enrollment = Enrollment(
        user_id=current_user.id,
        resource_id=resource_id,
        status="ENROLLED",
        progress_percentage=0.0
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return {"status": "success", "enrollment_id": enrollment.id, "resource_title": res.title}
