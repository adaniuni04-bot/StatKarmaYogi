from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class WhyRecommendedDetails(BaseModel):
    reason_codes: List[str]
    matched_competencies: List[str]
    gap_addressed: Dict[str, Any]
    explanation: str


class RecommendationResponse(BaseModel):
    id: str
    resource_id: str
    title: str
    description: Optional[str] = None
    provider: str  # IGOT, NSSTA, INTERNAL
    resource_type: str  # IGOT_COURSE, NSSTA_PROGRAM, VIDEO, etc.
    url: Optional[str] = None
    duration_minutes: int
    difficulty: str
    language: str
    authority_tier: str
    source_organization: str
    learning_outcomes: Optional[str] = None
    mock_data: bool
    recommendation_score: float
    rank: int
    why_recommended: WhyRecommendedDetails
