from datetime import datetime, timezone
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.users import User
from app.models.assessments import Assessment, Question, QuestionOption, AssessmentAttempt, AssessmentResponse
from app.models.competencies import Competency, UserCompetency
from app.services.competency.engine import update_user_competency
from app.services.skill_gap.engine import evaluate_user_skill_gaps
from app.services.learning.path_engine import generate_or_update_learning_path
from app.schemas.assessment import AssessmentSubmitRequest, AssessmentResultResponse, QuestionEvaluationResult


def submit_and_evaluate_assessment(
    db: Session,
    user_id: str,
    submission: AssessmentSubmitRequest
) -> AssessmentResultResponse:
    attempt = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.id == submission.attempt_id,
        AssessmentAttempt.user_id == user_id
    ).first()

    if not attempt:
        raise ValueError("Assessment attempt not found")

    assessment = attempt.assessment
    questions = assessment.questions

    total_questions = len(questions)
    correct_count = 0
    question_results: List[QuestionEvaluationResult] = []
    competency_points: Dict[str, Dict[str, float]] = {}

    answer_map = {ans.question_id: ans for ans in submission.answers}

    for q in questions:
        user_ans = answer_map.get(q.id)
        selected_option_id = user_ans.selected_option_id if user_ans else None

        correct_opt = next((opt for opt in q.options if opt.is_correct), None)
        correct_option_id = correct_opt.id if correct_opt else None

        is_correct = (selected_option_id is not None) and (selected_option_id == correct_option_id)
        points_awarded = 1.0 if is_correct else 0.0

        if is_correct:
            correct_count += 1

        # Track per-competency performance
        comp_id = q.competency_id
        if comp_id not in competency_points:
            competency_points[comp_id] = {"earned": 0.0, "total": 0.0}
        competency_points[comp_id]["earned"] += points_awarded
        competency_points[comp_id]["total"] += 1.0

        # Save response record
        db_resp = AssessmentResponse(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option_id=selected_option_id,
            is_correct=is_correct,
            points_awarded=points_awarded,
            feedback=q.explanation
        )
        db.add(db_resp)

        question_results.append(QuestionEvaluationResult(
            question_id=q.id,
            question_text=q.question_text,
            user_selected_option_id=selected_option_id,
            correct_option_id=correct_option_id,
            is_correct=is_correct,
            explanation=q.explanation,
            source_reference=q.source_reference,
            source_tier=q.source_tier
        ))

    score_pct = round((correct_count / max(1, total_questions)) * 100.0, 1)
    passed = score_pct >= assessment.passing_score

    attempt.status = "EVALUATED"
    attempt.score = score_pct
    attempt.points_earned = float(correct_count)
    attempt.total_points = float(total_questions)
    attempt.passed = passed
    attempt.submitted_at = datetime.now(timezone.utc)
    attempt.time_taken_seconds = submission.time_taken_seconds or 180

    db.commit()

    # Deterministically update competencies based on validated evidence
    competency_updates = []
    for comp_id, stats in competency_points.items():
        comp = db.query(Competency).filter(Competency.id == comp_id).first()
        if not comp:
            continue

        raw_test_pct = (stats["earned"] / max(1.0, stats["total"])) * 100.0

        # Fetch current score
        user_comp = db.query(UserCompetency).filter(
            UserCompetency.user_id == user_id,
            UserCompetency.competency_id == comp_id
        ).first()

        current_score = user_comp.score if user_comp else 0.0

        # Deterministic formula:
        # If test performance is higher than current, raise competency by weighted assessment delta
        if raw_test_pct >= current_score:
            improvement_delta = (raw_test_pct - current_score) * 0.55
            new_score = round(current_score + improvement_delta, 1)
        else:
            # Minor regression buffer if score is lower
            drop_delta = (current_score - raw_test_pct) * 0.15
            new_score = round(current_score - drop_delta, 1)

        new_score = max(0.0, min(100.0, new_score))

        updated_record = update_user_competency(
            db=db,
            user_id=user_id,
            competency_id=comp_id,
            new_score=new_score,
            reason=f"Completed Assessment: {assessment.title} (Score: {score_pct}%)",
            source="ASSESSMENT",
            assessment_id=assessment.id
        )

        competency_updates.append({
            "competency_id": comp_id,
            "competency_name": comp.name,
            "previous_score": current_score,
            "new_score": new_score,
            "delta": round(new_score - current_score, 1),
            "level": updated_record.level_name
        })

    # Trigger re-evaluation of Skill Gaps and Learning Path
    evaluate_user_skill_gaps(db, user_id)
    generate_or_update_learning_path(db, user_id)

    return AssessmentResultResponse(
        attempt_id=attempt.id,
        assessment_id=assessment.id,
        assessment_title=assessment.title,
        score_percentage=score_pct,
        passed=passed,
        points_earned=float(correct_count),
        total_points=float(total_questions),
        time_taken_seconds=attempt.time_taken_seconds,
        competency_updates=competency_updates,
        question_results=question_results
    )
