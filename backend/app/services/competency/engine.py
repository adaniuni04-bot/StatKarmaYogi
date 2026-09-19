from datetime import datetime, timezone
from typing import Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.competencies import Competency, UserCompetency, CompetencyHistory


def get_proficiency_level(score: float) -> Tuple[int, str]:
    score = max(0.0, min(100.0, score))
    if score <= settings.LEVEL_1_MAX:
        return 1, "Foundation"
    elif score <= settings.LEVEL_2_MAX:
        return 2, "Basic"
    elif score <= settings.LEVEL_3_MAX:
        return 3, "Intermediate"
    elif score <= settings.LEVEL_4_MAX:
        return 4, "Advanced"
    else:
        return 5, "Expert"


def calculate_competency_score(
    evidence: Dict[str, Optional[float]],
    current_evidence_count: int = 1
) -> Tuple[float, float, int, str]:
    """
    Deterministic calculation of a user's competency score from validated evidence sources.
    Rule 1 & 2: 100% deterministic, no LLM hallucinations.
    
    Default weights:
    - Self assessment: 10%
    - Knowledge assessment: 35%
    - Practical assessment: 40%
    - Training evidence: 15%
    """
    weights = {
        "self_assessment": settings.WEIGHT_SELF_ASSESSMENT,
        "knowledge_assessment": settings.WEIGHT_KNOWLEDGE_ASSESSMENT,
        "practical_assessment": settings.WEIGHT_PRACTICAL_ASSESSMENT,
        "training_evidence": settings.WEIGHT_TRAINING_EVIDENCE,
    }

    total_weight = 0.0
    weighted_sum = 0.0
    valid_sources = 0

    for source, weight in weights.items():
        val = evidence.get(source)
        if val is not None:
            normalized_val = max(0.0, min(100.0, float(val)))
            weighted_sum += normalized_val * weight
            total_weight += weight
            valid_sources += 1

    if total_weight > 0:
        final_score = round(weighted_sum / total_weight, 2)
    else:
        final_score = 0.0

    # Confidence calculation: function of evidence quantity and source diversity
    confidence_base = min(1.0, 0.4 + (valid_sources * 0.15) + (current_evidence_count * 0.05))
    confidence = round(confidence_base, 2)

    level, level_name = get_proficiency_level(final_score)
    return final_score, confidence, level, level_name


def update_user_competency(
    db: Session,
    user_id: str,
    competency_id: str,
    new_score: float,
    reason: str,
    source: str = "ASSESSMENT",
    assessment_id: Optional[str] = None
) -> UserCompetency:
    user_comp = db.query(UserCompetency).filter(
        UserCompetency.user_id == user_id,
        UserCompetency.competency_id == competency_id
    ).first()

    level, level_name = get_proficiency_level(new_score)

    if user_comp:
        prev_score = user_comp.score
        delta = round(new_score - prev_score, 2)
        user_comp.score = new_score
        user_comp.level = level
        user_comp.level_name = level_name
        user_comp.evidence_count += 1
        user_comp.confidence = min(1.0, round(user_comp.confidence + 0.1, 2))
        user_comp.last_assessed_at = datetime.now(timezone.utc)
        user_comp.source = source
    else:
        prev_score = 0.0
        delta = round(new_score, 2)
        user_comp = UserCompetency(
            user_id=user_id,
            competency_id=competency_id,
            score=new_score,
            level=level,
            level_name=level_name,
            confidence=0.6,
            evidence_count=1,
            last_assessed_at=datetime.now(timezone.utc),
            source=source
        )
        db.add(user_comp)

    # Record immutable historical ledger
    history = CompetencyHistory(
        user_id=user_id,
        competency_id=competency_id,
        previous_score=prev_score,
        new_score=new_score,
        delta=delta,
        reason=reason,
        assessment_id=assessment_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(history)
    db.commit()
    db.refresh(user_comp)
    return user_comp
