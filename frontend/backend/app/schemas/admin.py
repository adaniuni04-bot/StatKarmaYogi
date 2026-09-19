from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class HeatmapCell(BaseModel):
    competency_id: str
    competency_name: str
    department_id: str
    department_name: str
    average_score: float
    required_score: float
    gap: float
    status: str  # MET, GAP


class OrgHeatmapResponse(BaseModel):
    departments: List[str]
    competencies: List[str]
    matrix: List[HeatmapCell]


class DepartmentStatsResponse(BaseModel):
    department_id: str
    department_name: str
    employee_count: int
    avg_competency_score: float
    avg_role_readiness: float
    critical_gaps_count: int


class TrainingEffectivenessItem(BaseModel):
    competency_name: str
    domain_name: str
    before_training_score: float
    after_training_score: float
    improvement: float
    completion_rate: float
    employees_assessed: int


class FutureSkillResponse(BaseModel):
    id: str
    name: str
    domain: str
    current_readiness: float
    expected_importance: float
    gap: float
    priority: str
    recommended_training: Optional[str] = None
    trend_source: str
    rationale: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: str
    actor_id: Optional[str] = None
    actor_email: Optional[str] = None
    action: str
    resource: str
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime


class AdminDashboardSummaryResponse(BaseModel):
    total_employees: int
    total_departments: int
    total_competencies: int
    org_average_readiness: float
    critical_gaps_total: int
    active_learning_paths: int
    assessments_completed_30d: int
    top_skill_gaps: List[Dict[str, Any]]
    training_effectiveness: List[TrainingEffectivenessItem]
