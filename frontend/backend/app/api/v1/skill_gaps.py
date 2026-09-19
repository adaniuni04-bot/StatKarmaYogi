import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User, Designation
from app.schemas.skill_gap import (
    SkillGapItem,
    SkillGapSummaryResponse,
    CareerRoleComparisonRequest,
    CareerRoleComparisonResponse
)
from app.services.skill_gap.engine import evaluate_user_skill_gaps
from app.services.skill_gap.ai_engine import (
    evaluate_dynamic_skill_gaps_with_ai,
    save_user_ai_profile,
    get_user_ai_profile
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/skill-gaps", tags=["Skill Gaps"])


@router.get("/me", response_model=SkillGapSummaryResponse)
def get_my_skill_gaps(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = get_user_ai_profile(db, current_user.id)
    if profile and "gaps" in profile:
        raw_gaps = profile.get("gaps", [])
        gap_items = []
        crit_count = 0
        high_count = 0

        for g in raw_gaps:
            p_lvl = g.get("priority_level", "MEDIUM")
            if p_lvl == "CRITICAL":
                crit_count += 1
            elif p_lvl == "HIGH":
                high_count += 1

            gap_val = float(g.get("gap", 0.0))
            gap_items.append(SkillGapItem(
                competency_id=f"comp-{hash(g.get('skill', '')) % 100000}",
                competency_name=g.get("skill", "Unknown Competency"),
                competency_code=g.get("skill", "SKILL").upper()[:10],
                domain_code="FIELD",
                domain_name=g.get("domain", profile.get("industry_field", "Engineering")),
                current_score=float(g.get("current_score", 0.0)),
                required_score=float(g.get("required_score", 80.0)),
                gap=gap_val,
                status="GAP" if gap_val > 0 else "MET",
                priority_score=round(gap_val * 1.3, 1),
                priority_level=p_lvl,
                confidence=0.85,
                mandatory=True,
                importance=1.2,
                recommended_action=g.get("recommended_action", "Review study modules"),
                current_level=g.get("current_level", "None"),
                required_level=g.get("required_level", "Intermediate"),
                is_missing=g.get("is_missing", False),
                reason=g.get("reason", "Required for role performance.")
            ))

        total_comps = len(gap_items) + len(profile.get("strengths", []))
        met_count = len(profile.get("strengths", []))

        return SkillGapSummaryResponse(
            user_id=current_user.id,
            designation_name=profile.get("target_role", current_user.designation_name or "Professional"),
            overall_readiness_percentage=float(profile.get("overall_readiness_percentage", 50.0)),
            readiness_status=profile.get("readiness_status", "Needs Development"),
            total_competencies=total_comps,
            met_count=met_count,
            gap_count=len(gap_items),
            critical_gaps_count=crit_count,
            high_gaps_count=high_count,
            gaps=gap_items,
            ai_summary=profile.get("ai_summary", "AI Skill Gap Evaluation complete."),
            strengths=profile.get("strengths", [])
        )

    # Fallback to database evaluate_user_skill_gaps
    return evaluate_user_skill_gaps(db, current_user.id)


@router.post("/reanalyze", response_model=SkillGapSummaryResponse)
async def reanalyze_skill_gaps(
    data: dict = {},
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_profile = get_user_ai_profile(db, current_user.id) or {}
    target_role = data.get("position") or existing_profile.get("target_role") or current_user.career_goal or current_user.designation_name or "Full-Stack Engineer"
    industry_field = data.get("field") or existing_profile.get("industry_field") or current_user.industry_field or "Computer Science & Software"
    skills = data.get("skills") if (data.get("skills") and len(data.get("skills")) > 0) else existing_profile.get("declared_skills", [])

    if not skills:
        recovered = []
        for g in existing_profile.get("gaps", []):
            c_score = float(g.get("current_score", 0.0))
            if c_score > 0.0 or g.get("current_level") not in ["None", "Not Assessed", None]:
                recovered.append({
                    "skill": g.get("skill"),
                    "level": g.get("current_level", "Intermediate"),
                    "score": c_score if c_score > 0.0 else 60.0
                })
        for s in existing_profile.get("strengths", []):
            recovered.append({
                "skill": s.get("skill"),
                "level": s.get("level", "Advanced"),
                "score": float(s.get("score", 80.0))
            })
        skills = recovered

    ai_profile = await evaluate_dynamic_skill_gaps_with_ai(
        target_role=target_role,
        industry_field=industry_field,
        declared_skills=skills,
        years_experience=current_user.years_experience or 0,
        career_goal=current_user.career_goal or target_role
    )
    save_user_ai_profile(db, current_user, ai_profile)
    return get_my_skill_gaps(current_user=current_user, db=db)


@router.get("/{user_id}", response_model=SkillGapSummaryResponse)
def get_user_skill_gaps(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return get_my_skill_gaps(current_user=target_user, db=db)


@router.post("/career-compare", response_model=CareerRoleComparisonResponse)
def compare_career_target_role(
    request: CareerRoleComparisonRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_eval = evaluate_user_skill_gaps(db, current_user.id)
    target_eval = evaluate_user_skill_gaps(db, current_user.id, designation_id=request.target_designation_id)

    target_desig = db.query(Designation).filter(Designation.id == request.target_designation_id).first()
    target_name = target_desig.name if target_desig else "Target Role"

    return CareerRoleComparisonResponse(
        current_role=current_eval.designation_name,
        target_role=target_name,
        current_readiness=current_eval.overall_readiness_percentage,
        target_readiness=target_eval.overall_readiness_percentage,
        additional_gaps=target_eval.gaps
    )
