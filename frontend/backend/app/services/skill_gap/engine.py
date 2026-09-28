from datetime import datetime, timezone
from typing import List, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.users import User
from app.models.competencies import Competency, RoleCompetency, UserCompetency
from app.models.recommendations import SkillGap
from app.schemas.skill_gap import SkillGapItem, SkillGapSummaryResponse


def calculate_gap(current_score: float, required_score: float) -> Tuple[float, str]:
    gap = round(required_score - current_score, 2)
    if gap <= 0.0:
        return 0.0, "MET"
    return gap, "GAP"


def calculate_priority(
    gap: float,
    importance: float = 1.0,
    mandatory: bool = True,
    future_relevance: float = 1.0,
    confidence: float = 0.5
) -> Tuple[float, str]:
    """
    Priority formula specified in Section 12:
    priority_score = gap * importance * mandatory_weight * future_relevance * confidence_adjustment
    """
    if gap <= 0.0:
        return 0.0, "LOW"

    mandatory_weight = 1.3 if mandatory else 1.0
    # Lower confidence slightly elevates priority to verify/solidify the skill
    confidence_adj = 1.0 + max(0.0, (1.0 - confidence) * 0.25)

    priority_score = round(gap * importance * mandatory_weight * future_relevance * confidence_adj, 2)

    if priority_score >= 35.0 or (gap >= 30.0 and mandatory):
        level = "CRITICAL"
    elif priority_score >= 20.0:
        level = "HIGH"
    elif priority_score >= 10.0:
        level = "MEDIUM"
    else:
        level = "LOW"

    return priority_score, level


def calculate_role_readiness(items: List[SkillGapItem]) -> Tuple[float, str]:
    if not items:
        return 100.0, "Ready"

    total_weighted_points = 0.0
    earned_weighted_points = 0.0

    for item in items:
        weight = item.importance * (1.5 if item.mandatory else 1.0)
        total_weighted_points += weight
        # If current score is at or above required, award full weight; else award proportional ratio
        ratio = min(1.0, item.current_score / max(1.0, item.required_score))
        earned_weighted_points += ratio * weight

    readiness = round((earned_weighted_points / max(1.0, total_weighted_points)) * 100.0, 1)

    if readiness >= settings.ROLE_READINESS_READY_THRESHOLD:
        status = "Ready"
    elif readiness >= settings.ROLE_READINESS_NEAR_READY_THRESHOLD:
        status = "Near Ready"
    else:
        status = "Needs Development"

    return readiness, status


def evaluate_user_skill_gaps(db: Session, user_id: str, designation_id: str = None) -> SkillGapSummaryResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found")

    target_designation_id = designation_id or user.designation_id
    if not target_designation_id:
        # Return default empty response
        return SkillGapSummaryResponse(
            user_id=user_id,
            designation_name="Not Assigned",
            overall_readiness_percentage=0.0,
            readiness_status="Needs Development",
            total_competencies=0,
            met_count=0,
            gap_count=0,
            critical_gaps_count=0,
            high_gaps_count=0,
            gaps=[]
        )

    # Fetch required competencies for role
    role_comps = db.query(RoleCompetency).filter(
        RoleCompetency.designation_id == target_designation_id
    ).all()

    # Fetch current user competencies
    user_comps_map = {
        uc.competency_id: uc
        for uc in db.query(UserCompetency).filter(UserCompetency.user_id == user_id).all()
    }

    gap_items: List[SkillGapItem] = []
    critical_count = 0
    high_count = 0
    met_count = 0
    gap_count = 0

    for rc in role_comps:
        comp = rc.competency
        uc = user_comps_map.get(rc.competency_id)
        current_score = uc.score if uc else 0.0
        confidence = uc.confidence if uc else 0.4

        gap, status = calculate_gap(current_score, rc.required_score)
        priority_score, priority_level = calculate_priority(
            gap=gap,
            importance=rc.importance,
            mandatory=rc.mandatory,
            future_relevance=rc.future_relevance,
            confidence=confidence
        )

        if status == "MET":
            met_count += 1
            recommended_action = "Maintain mastery through refresher modules."
        else:
            gap_count += 1
            if priority_level == "CRITICAL":
                critical_count += 1
                recommended_action = "Immediate priority: Enroll in designated iGOT/NSSTA core module."
            elif priority_level == "HIGH":
                high_count += 1
                recommended_action = "High priority: Schedule targeted practice and assessment."
            else:
                recommended_action = "Recommended for next learning sprint."

        item = SkillGapItem(
            competency_id=comp.id,
            competency_name=comp.name,
            competency_code=comp.code,
            domain_code=comp.domain.code if comp.domain else "GENERAL",
            domain_name=comp.domain.name if comp.domain else "General",
            current_score=current_score,
            required_score=rc.required_score,
            gap=gap,
            status=status,
            priority_score=priority_score,
            priority_level=priority_level,
            confidence=confidence,
            mandatory=rc.mandatory,
            importance=rc.importance,
            recommended_action=recommended_action
        )
        gap_items.append(item)

        # Upsert SkillGap in DB for persistent indexing
        existing_gap = db.query(SkillGap).filter(
            SkillGap.user_id == user_id,
            SkillGap.competency_id == comp.id
        ).first()

        if existing_gap:
            existing_gap.current_score = current_score
            existing_gap.required_score = rc.required_score
            existing_gap.gap = gap
            existing_gap.status = status
            existing_gap.priority_score = priority_score
            existing_gap.priority_level = priority_level
            existing_gap.confidence = confidence
            existing_gap.last_updated_at = datetime.now(timezone.utc)
        else:
            db.add(SkillGap(
                user_id=user_id,
                competency_id=comp.id,
                current_score=current_score,
                required_score=rc.required_score,
                gap=gap,
                status=status,
                priority_score=priority_score,
                priority_level=priority_level,
                confidence=confidence,
                last_updated_at=datetime.now(timezone.utc)
            ))

    db.commit()

    # Sort items: CRITICAL first, then HIGH, then MEDIUM, then LOW, then MET
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    gap_items.sort(key=lambda x: (
        0 if x.status == "GAP" else 1,
        priority_order.get(x.priority_level, 4),
        -x.gap
    ))

    readiness_percentage, readiness_status = calculate_role_readiness(gap_items)
    designation_name = user.designation_rel.name if user.designation_rel else (user.designation_name or "Official")

    return SkillGapSummaryResponse(
        user_id=user_id,
        designation_name=designation_name,
        overall_readiness_percentage=readiness_percentage,
        readiness_status=readiness_status,
        total_competencies=len(gap_items),
        met_count=met_count,
        gap_count=gap_count,
        critical_gaps_count=critical_count,
        high_gaps_count=high_count,
        gaps=gap_items
    )
