from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class LearningPathItemResponse(BaseModel):
    id: str
    stage_order: int
    stage_name: str
    title: str
    description: Optional[str] = None
    resource_id: Optional[str] = None
    competency_focus: Optional[str] = None
    status: str
    estimated_minutes: int
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    target_role: Optional[str] = None
    status: str
    overall_progress: float
    items: List[LearningPathItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    id: str
    resource_id: str
    resource_title: str
    provider: str
    status: str
    progress_percentage: float
    enrolled_at: datetime
