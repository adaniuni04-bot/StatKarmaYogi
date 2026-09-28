from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SubCompetencyResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CompetencyResponse(BaseModel):
    id: str
    domain_id: str
    code: str
    name: str
    description: Optional[str] = None
    definition: Optional[str] = None
    version: str
    future_relevance: float
    subcompetencies: List[SubCompetencyResponse] = []

    class Config:
        from_attributes = True


class CompetencyDomainResponse(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    competencies: List[CompetencyResponse] = []

    class Config:
        from_attributes = True


class RoleCompetencyResponse(BaseModel):
    id: str
    designation_id: str
    competency_id: str
    competency_name: str
    competency_code: str
    domain_code: str
    required_level: int
    required_score: float
    importance: float
    mandatory: bool
    future_relevance: float


class UserCompetencyResponse(BaseModel):
    id: str
    competency_id: str
    competency_name: str
    competency_code: str
    domain_code: str
    domain_name: str
    score: float
    level: int
    level_name: str
    confidence: float
    evidence_count: int
    last_assessed_at: datetime
    source: str


class CompetencyHistoryResponse(BaseModel):
    id: str
    competency_id: str
    competency_name: str
    previous_score: float
    new_score: float
    delta: float
    reason: str
    created_at: datetime
