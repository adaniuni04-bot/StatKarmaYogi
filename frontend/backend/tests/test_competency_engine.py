import pytest
from app.services.competency.engine import calculate_competency_score, get_proficiency_level


def test_proficiency_levels():
    assert get_proficiency_level(15.0) == (1, "Foundation")
    assert get_proficiency_level(20.0) == (1, "Foundation")
    assert get_proficiency_level(21.0) == (2, "Basic")
    assert get_proficiency_level(40.0) == (2, "Basic")
    assert get_proficiency_level(42.0) == (3, "Intermediate")
    assert get_proficiency_level(60.0) == (3, "Intermediate")
    assert get_proficiency_level(75.0) == (4, "Advanced")
    assert get_proficiency_level(85.0) == (5, "Expert")


def test_deterministic_weighted_scoring():
    # Weights: self 0.10, knowledge 0.35, practical 0.40, training 0.15
    evidence = {
        "self_assessment": 50.0,
        "knowledge_assessment": 80.0,
        "practical_assessment": 90.0,
        "training_evidence": 70.0
    }
    # Expected: (50*0.1) + (80*0.35) + (90*0.4) + (70*0.15) = 5 + 28 + 36 + 10.5 = 79.5
    score, confidence, level, level_name = calculate_competency_score(evidence)
    assert score == 79.5
    assert level == 4
    assert level_name == "Advanced"
    assert confidence > 0.8


def test_partial_evidence_scoring():
    # Only self and knowledge
    evidence = {
        "self_assessment": 40.0,
        "knowledge_assessment": 60.0
    }
    # Total weight: 0.10 + 0.35 = 0.45.
    # Weighted sum: (40*0.1) + (60*0.35) = 4 + 21 = 25.
    # Normalized: 25 / 0.45 = 55.56
    score, confidence, level, level_name = calculate_competency_score(evidence)
    assert round(score, 2) == 55.56
    assert level == 3
    assert level_name == "Intermediate"
