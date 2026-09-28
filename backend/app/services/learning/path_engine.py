from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.users import User
from app.models.resources import Resource
from app.models.learning import LearningPath, LearningPathItem
from app.models.assessments import Assessment
from app.schemas.learning import LearningPathResponse, LearningPathItemResponse
from app.services.skill_gap.ai_engine import get_user_ai_profile


def generate_or_update_learning_path(db: Session, user_id: str) -> LearningPathResponse:
    """
    Dynamically generates or recalculates a 5-stage personalized learning path
    based on the user's ACTUAL identified AI skill gaps and target role.
    Zero hardcoded statistical or legacy content.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    # 1. Fetch dynamic AI profile
    profile = get_user_ai_profile(db, user_id) or {}
    target_role = profile.get("target_role") or user.designation_name or "Technical Specialist"
    industry_field = profile.get("industry_field") or user.industry_field or "Technology"
    gaps: List[Dict[str, Any]] = profile.get("gaps", [])

    # Sort gaps: CRITICAL first, then HIGH, then MEDIUM
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_gaps = sorted(gaps, key=lambda g: priority_order.get(g.get("priority_level", "MEDIUM"), 2))

    gap_names = [g.get("skill") for g in sorted_gaps if g.get("skill")]
    focus_summary = ", ".join(gap_names[:3]) if gap_names else "Core Industry Competencies"

    # 2. Check for existing active path
    path = db.query(LearningPath).filter(
        LearningPath.user_id == user_id,
        LearningPath.status == "ACTIVE"
    ).first()

    path_title = f"Career Mastery Learning Path: {target_role}"
    path_desc = f"Personalized 5-stage developmental roadmap targeting active skill gaps in {focus_summary} for {target_role} production readiness."

    if not path:
        path = LearningPath(
            user_id=user_id,
            title=path_title,
            description=path_desc,
            target_role=target_role,
            status="ACTIVE",
            overall_progress=0.0,
            created_at=datetime.now(timezone.utc)
        )
        db.add(path)
        db.flush()
    else:
        path.title = path_title
        path.description = path_desc
        path.target_role = target_role
        db.flush()

    # Clear old items to regenerate fresh stages matching the current role and gaps
    for old_item in list(path.items):
        db.delete(old_item)
    db.flush()

    # 3. Formulate 5 dynamic stages tailored directly to the candidate's gaps
    g1 = gap_names[0] if len(gap_names) > 0 else f"{target_role} Core Fundamentals"
    g2 = gap_names[1] if len(gap_names) > 1 else (gap_names[0] if gap_names else "Technical Architecture")
    g3 = gap_names[2] if len(gap_names) > 2 else (gap_names[1] if len(gap_names) > 1 else "Advanced Systems")
    g4 = gap_names[3] if len(gap_names) > 3 else "Scenario Diagnostic Assessment"
    g5 = gap_names[4] if len(gap_names) > 4 else "Enterprise Production Integration"

    stage_configs = [
        {
            "stage_order": 1,
            "stage_name": "Stage 1: Foundational Prerequisites & Environment Mastery",
            "title": f"Foundation Phase: {g1} Core Principles & Tools",
            "description": f"Master the underlying concepts, environment setup, and foundational principles for {g1}. Bridge basic proficiency gaps before advancing to active execution.",
            "competency_focus": g1,
            "estimated_minutes": 240,
            "status": "IN_PROGRESS"
        },
        {
            "stage_order": 2,
            "stage_name": "Stage 2: Core Tooling & Technical Competency",
            "title": f"Applied Execution: {g2} Deep Practice",
            "description": f"Hands-on technical mastery of {g2}. Focus on practical implementation, protocol interaction, and eliminating critical operational deficits.",
            "competency_focus": g2,
            "estimated_minutes": 360,
            "status": "NOT_STARTED"
        },
        {
            "stage_order": 3,
            "stage_name": "Stage 3: Advanced Specialization & Deep Dives",
            "title": f"Advanced Specialization: {g3} & Complex Scenarios",
            "description": f"Tackle advanced industry challenges involving {g3}. Master privilege boundaries, architecture resilience, and edge-case execution.",
            "competency_focus": g3,
            "estimated_minutes": 420,
            "status": "NOT_STARTED"
        },
        {
            "stage_order": 4,
            "stage_name": "Stage 4: AI Diagnostic Assessment & Verification",
            "title": f"Diagnostic Milestone: AI Evaluation for {target_role} Gaps",
            "description": f"Undergo a customized scenario-based AI diagnostic test evaluating your retention across {g1}, {g2}, and {g3} to confirm gap closure.",
            "competency_focus": f"{g1}, {g2}",
            "estimated_minutes": 60,
            "status": "NOT_STARTED"
        },
        {
            "stage_order": 5,
            "stage_name": "Stage 5: Production Capstone & Industry Readiness",
            "title": f"Capstone Defense: Full-Scale {target_role} Production Challenge",
            "description": f"Execute an end-to-end practical capstone verifying your readiness for enterprise {target_role} responsibilities.",
            "competency_focus": f"{target_role} Mastery",
            "estimated_minutes": 480,
            "status": "NOT_STARTED"
        }
    ]

    # Check for available assessment
    active_assessment = db.query(Assessment).filter(Assessment.active == True).first()

    for cfg in stage_configs:
        item = LearningPathItem(
            learning_path_id=path.id,
            stage_order=cfg["stage_order"],
            stage_name=cfg["stage_name"],
            title=cfg["title"],
            description=cfg["description"],
            resource_id=None,
            competency_focus=cfg["competency_focus"],
            status=cfg["status"],
            estimated_minutes=cfg["estimated_minutes"]
        )
        db.add(item)

    db.commit()
    db.refresh(path)

    total_stages = len(path.items)
    completed_stages = sum(1 for it in path.items if it.status == "COMPLETED")
    path.overall_progress = round((completed_stages / max(1, total_stages)) * 100.0, 1)
    db.commit()

    return LearningPathResponse.model_validate(path)
