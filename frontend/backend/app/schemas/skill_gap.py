from typing import List, Optional, Any, Dict
from pydantic import BaseModel


class SkillGapItem(BaseModel):
    competency_id: str = "comp-generic"
    competency_name: str
    competency_code: str = "TECH"
    domain_code: str = "FIELD"
    domain_name: str = "Engineering & Technology"
    current_score: float
    required_score: float
    gap: float
    status: str = "GAP"  # MET or GAP
    priority_score: float = 0.0
    priority_level: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float = 0.8
    mandatory: bool = True
    importance: float = 1.0
    recommended_action: str = ""
    current_level: Optional[str] = None
    required_level: Optional[str] = None
    is_missing: Optional[bool] = False
    reason: Optional[str] = None


class SkillGapSummaryResponse(BaseModel):
    user_id: str
    designation_name: str
    overall_readiness_percentage: float
    readiness_status: str  # Ready, Near Ready, Needs Development
    total_competencies: int = 0
    met_count: int = 0
    gap_count: int = 0
    critical_gaps_count: int = 0
    high_gaps_count: int = 0
    gaps: List[SkillGapItem] = []
    ai_summary: Optional[str] = None
    strengths: Optional[List[Dict[str, Any]]] = []
    missing_skills: Optional[List[str]] = []


class CareerRoleComparisonRequest(BaseModel):
    target_designation_id: str


class CareerRoleComparisonResponse(BaseModel):
    current_role: str
    target_role: str
    current_readiness: float
    target_readiness: float
    additional_gaps: List[SkillGapItem]
