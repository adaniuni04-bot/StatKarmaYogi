import pytest
from app.services.skill_gap.engine import calculate_gap, calculate_priority, calculate_role_readiness
from app.schemas.skill_gap import SkillGapItem


def test_sampling_gap_acceptance_criterion():
    """Section 67 & 13: Given Sampling current=42, required=80 -> gap=38, status='GAP'"""
    gap, status = calculate_gap(current_score=42.0, required_score=80.0)
    assert gap == 38.0
    assert status == "GAP"

    priority_score, priority_level = calculate_priority(
        gap=gap,
        importance=1.2,
        mandatory=True,
        future_relevance=1.2,
        confidence=0.55
    )
    assert priority_score > 35.0
    assert priority_level == "CRITICAL"


def test_python_met_acceptance_criterion():
    """Section 67 & 13: Given Python current=70, required=60 -> gap=0, status='MET'"""
    gap, status = calculate_gap(current_score=70.0, required_score=60.0)
    assert gap == 0.0
    assert status == "MET"

    priority_score, priority_level = calculate_priority(
        gap=gap,
        importance=1.0,
        mandatory=True,
        future_relevance=1.0,
        confidence=0.85
    )
    assert priority_score == 0.0
    assert priority_level == "LOW"


def test_role_readiness_calculation():
    items = [
        SkillGapItem(
            competency_id="1",
            competency_name="Sampling",
            competency_code="SAMPLING",
            domain_code="STAT",
            domain_name="Statistical",
            current_score=80.0,
            required_score=80.0,
            gap=0.0,
            status="MET",
            priority_score=0.0,
            priority_level="LOW",
            confidence=0.9,
            mandatory=True,
            importance=1.0,
            recommended_action="Maintain"
        ),
        SkillGapItem(
            competency_id="2",
            competency_name="Python",
            competency_code="PYTHON",
            domain_code="TECH",
            domain_name="Technical",
            current_score=60.0,
            required_score=60.0,
            gap=0.0,
            status="MET",
            priority_score=0.0,
            priority_level="LOW",
            confidence=0.9,
            mandatory=True,
            importance=1.0,
            recommended_action="Maintain"
        )
    ]
    readiness, status_label = calculate_role_readiness(items)
    assert readiness == 100.0
    assert status_label == "Ready"
