from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier"
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        # Check if the token carries the user's registered profile (stateless serverless recovery)
        user_data = payload.get("user_data")
        if user_data:
            import json
            ai_prof = user_data.get("ai_profile")
            ai_prof_str = json.dumps(ai_prof) if isinstance(ai_prof, (dict, list)) else (ai_prof or "")
            user = User(
                id=user_id,
                email=user_data.get("email", f"{user_id}@example.com"),
                password_hash=user_data.get("password_hash", "serverless_hash"),
                first_name=user_data.get("first_name", "Candidate"),
                last_name=user_data.get("last_name", ""),
                role=user_data.get("role", payload.get("role", "EMPLOYEE")),
                designation_name=user_data.get("position", user_data.get("designation_name", "Professional")),
                industry_field=user_data.get("field", user_data.get("industry_field", "Computer Science")),
                organization=user_data.get("organization", "Enterprise Tech"),
                years_experience=user_data.get("years_experience", 0),
                education=user_data.get("education", ""),
                current_assignment=user_data.get("current_assignment", ""),
                career_goal=user_data.get("career_goal", ""),
                preferred_learning_style=user_data.get("preferred_learning_style", "Hands-on projects & labs"),
                weekly_hours=user_data.get("weekly_hours", "10 hours/week"),
                current_project_focus=user_data.get("current_project_focus", ""),
                preferred_language=user_data.get("preferred_language", "en"),
                status="ACTIVE",
                is_active=True,
                ai_profile_json=ai_prof_str
            )
            try:
                db.add(user)
                db.commit()
                db.refresh(user)
            except Exception:
                db.rollback()
                user = db.query(User).filter(User.id == user_id).first() or db.query(User).filter(User.email == user_data.get("email")).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles and user.role != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current user role"
            )
        return user
