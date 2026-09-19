import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User
from app.models.future_skills import FutureSkill
from app.models.audit import AuditLog
from app.schemas.admin import (
    AdminDashboardSummaryResponse,
    OrgHeatmapResponse,
    DepartmentStatsResponse,
    FutureSkillResponse,
    AuditLogResponse
)
from app.schemas.auth import UserResponse
from app.services.analytics.engine import get_admin_summary, get_org_heatmap, get_department_stats
from app.api.deps import get_current_user, RoleChecker

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])


@router.get("/dashboard", response_model=AdminDashboardSummaryResponse)
def get_dashboard_metrics(
    current_user: User = Depends(RoleChecker(["ADMIN", "TRAINER", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    return get_admin_summary(db)


@router.get("/heatmap", response_model=OrgHeatmapResponse)
def get_organization_heatmap(
    current_user: User = Depends(RoleChecker(["ADMIN", "TRAINER", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    return get_org_heatmap(db)


@router.get("/departments", response_model=List[DepartmentStatsResponse])
def get_departments_breakdown(
    current_user: User = Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    return get_department_stats(db)


@router.get("/future-skills", response_model=List[FutureSkillResponse])
def get_future_skills(db: Session = Depends(get_db)):
    skills = db.query(FutureSkill).all()
    return [FutureSkillResponse(
        id=s.id,
        name=s.name,
        domain=s.domain,
        current_readiness=s.current_readiness,
        expected_importance=s.expected_importance,
        gap=s.gap,
        priority=s.priority,
        recommended_training=s.recommended_training,
        trend_source=s.trend_source,
        rationale=s.rationale
    ) for s in skills]


@router.get("/audit-logs", response_model=List[AuditLogResponse])
def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    results = []
    for log in logs:
        details = None
        if log.details_json:
            try:
                details = json.loads(log.details_json)
            except Exception:
                pass

        results.append(AuditLogResponse(
            id=log.id,
            actor_id=log.actor_id,
            actor_email=log.actor_email,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            details=details,
            ip_address=log.ip_address,
            created_at=log.created_at
        ))
    return results


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    current_user: User = Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    users = db.query(User).all()
    return [UserResponse.model_validate(u) for u in users]
