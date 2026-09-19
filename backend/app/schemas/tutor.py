from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TutorCitation(BaseModel):
    title: str
    organization: str
    page: Optional[int] = None
    section: Optional[str] = None
    url: Optional[str] = None
    authority_tier: str  # TIER_A, TIER_B, TIER_C, TIER_D


class TutorChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: Optional[str] = "en"


class TutorMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    is_grounded: bool
    confidence: float
    citations: List[TutorCitation] = []
    suggested_practice_question: Optional[str] = None
    created_at: datetime


class TutorSessionResponse(BaseModel):
    id: str
    title: str
    topic: Optional[str] = None
    language: str
    created_at: datetime
    messages: List[TutorMessageResponse] = []
