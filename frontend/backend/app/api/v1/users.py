from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User, Designation, Department
from app.schemas.auth import UserResponse, UserProfileUpdate
from app.api.deps import get_current_user, RoleChecker
from app.services.audit.service import log_audit_event

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.first_name is not None:
        current_user.first_name = update_data.first_name
    if update_data.last_name is not None:
        current_user.last_name = update_data.last_name
    if update_data.years_experience is not None:
        current_user.years_experience = update_data.years_experience
    if update_data.education is not None:
        current_user.education = update_data.education
    if update_data.current_assignment is not None:
        current_user.current_assignment = update_data.current_assignment
    if update_data.career_goal is not None:
        current_user.career_goal = update_data.career_goal
    if update_data.preferred_language is not None:
        current_user.preferred_language = update_data.preferred_language
    if update_data.designation_name is not None:
        current_user.designation_name = update_data.designation_name
        desig = db.query(Designation).filter(Designation.name == update_data.designation_name).first()
        if desig:
            current_user.designation_id = desig.id

    db.commit()
    db.refresh(current_user)
    log_audit_event(db, action="PROFILE_UPDATE", resource="User", actor_id=current_user.id, actor_email=current_user.email)
    return UserResponse.model_validate(current_user)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse.model_validate(user)
