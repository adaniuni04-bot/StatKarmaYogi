from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.schemas.recommendation import RecommendationResponse
from app.services.recommendations.engine import generate_recommendations
from app.api.deps import get_current_user

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/me", response_model=List[RecommendationResponse])
def get_my_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_recommendations(db=db, user_id=current_user.id)


@router.post("/generate", response_model=List[RecommendationResponse])
def trigger_recommendation_generation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return generate_recommendations(db=db, user_id=current_user.id)
