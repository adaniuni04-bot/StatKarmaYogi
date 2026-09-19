import json
import re
import uuid
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.models.assessments import Assessment, Question, QuestionOption
from app.models.competencies import Competency
from app.services.ai.factory import get_llm_provider


async def generate_ai_assessment_for_gaps(
    db: Session,
    user_id: str,
    gap_skills: List[str],
    role_title: str = "Software Professional"
) -> Assessment:
    """
    Dynamically generates a diagnostic assessment using Ollama Qwen3:8b based on the candidate's exact skill gaps.
    """
    gaps_str = ", ".join(gap_skills[:4]) if gap_skills else "Core Software Engineering & System Design"

    prompt = f"""You are an Expert Technical Interviewer & Assessment Creator.
The candidate is preparing for the role of '{role_title}'.
Their active skill gaps are: {gaps_str}.

Generate 5 practical, scenario-based multiple-choice assessment questions specifically evaluating their knowledge in these gap areas.
Each question must test real-world application, not just trivia.

Output strict valid JSON with this exact structure:
{{
  "assessment_title": "AI Diagnostic Test: {role_title} Gap Evaluation",
  "description": "Custom diagnostic evaluation generated dynamically by AI for {gaps_str}.",
  "questions": [
    {{
      "question_text": "In a high-throughput microservices architecture, what is the primary benefit of deploying services in Docker containers managed by Kubernetes?",
      "skill": "Docker Containerization",
      "difficulty": "INTERMEDIATE",
      "options": [
        "Automated rolling updates, declarative self-healing, and isolation across compute resources.",
        "It replaces the need for a database by holding state in memory indefinitely.",
        "It compiles interpreted languages into raw x86 assembly for faster clock speeds.",
        "It eliminates the need for network security and SSL certificates."
      ],
      "correct_option_index": 0,
      "explanation": "Container orchestration with Kubernetes provides declarative state management, health probes, automated restarts, and resource boundary isolation."
    }}
  ]
}}
"""

    questions_data = None
    llm = get_llm_provider()

    try:
        raw_res = await asyncio.wait_for(
            llm.generate(prompt, system_prompt="You are a Principal Engineering Assessor. Respond with strict JSON only."),
            timeout=30.0
        )
        json_match = re.search(r'(\{[\s\S]*\})', raw_res)
        if json_match:
            parsed = json.loads(json_match.group(1))
            if "questions" in parsed and len(parsed["questions"]) > 0:
                questions_data = parsed
    except Exception as e:
        logger.warning(f"Ollama dynamic MCQ generation fallback activated: {e}")

    # Fallback if Ollama times out or returns non-JSON
    if not questions_data:
        questions_data = generate_fallback_questions(gaps_str, role_title)

    # Find a default competency to attach or use first available
    fallback_comp = db.query(Competency).first()
    comp_id = fallback_comp.id if fallback_comp else str(uuid.uuid4())

    # Persist the newly generated assessment in DB
    assessment = Assessment(
        title=questions_data.get("assessment_title", f"AI Diagnostic Test: {role_title} Gap Evaluation"),
        description=questions_data.get("description", f"AI-generated evaluation targeting: {gaps_str}"),
        assessment_type="DIAGNOSTIC",
        competency_id=comp_id,
        duration_minutes=15,
        passing_score=70.0,
        difficulty="INTERMEDIATE",
        active=True
    )
    db.add(assessment)
    db.flush()

    for idx, q_item in enumerate(questions_data["questions"]):
        q = Question(
            assessment_id=assessment.id,
            competency_id=comp_id,
            question_text=q_item["question_text"],
            question_type="SINGLE_CHOICE",
            difficulty=q_item.get("difficulty", "INTERMEDIATE"),
            explanation=q_item.get("explanation", "Correct understanding of key principles.")
        )
        db.add(q)
        db.flush()

        corr_idx = int(q_item.get("correct_option_index", 0))
        for o_idx, opt_text in enumerate(q_item.get("options", [])):
            opt = QuestionOption(
                question_id=q.id,
                option_text=opt_text,
                is_correct=(o_idx == corr_idx),
                order_index=o_idx + 1
            )
            db.add(opt)

    db.commit()
    db.refresh(assessment)
    return assessment


def generate_fallback_questions(gaps_str: str, role_title: str) -> Dict[str, Any]:
    return {
        "assessment_title": f"AI Diagnostic Test: {role_title} Gap Evaluation",
        "description": f"Targeted assessment focusing on: {gaps_str}",
        "questions": [
            {
                "question_text": f"When addressing critical architecture requirements in {gaps_str}, what is the recommended practice to ensure fault tolerance and low latency?",
                "skill": gaps_str,
                "difficulty": "INTERMEDIATE",
                "options": [
                    "Implement asynchronous processing, circuit breakers, and idempotent retry policies.",
                    "Execute all tasks synchronously on a single large thread to avoid context switching.",
                    "Disable database connection pooling to minimize memory footprint.",
                    "Store session state directly inside transient compute nodes without persistence."
                ],
                "correct_option_index": 0,
                "explanation": "Circuit breakers and idempotent message handling prevent cascading failures and maintain system responsiveness."
            },
            {
                "question_text": "In production systems, what is the primary purpose of writing unit and integration tests with automated CI pipelines?",
                "skill": "Quality Assurance",
                "difficulty": "INTERMEDIATE",
                "options": [
                    "To catch regressions early and enforce API contracts before merging code to main branches.",
                    "To completely eliminate the need for production monitoring.",
                    "To increase binary size so that unauthorized inspection is hindered.",
                    "To slow down deployments so that human review takes several weeks."
                ],
                "correct_option_index": 0,
                "explanation": "Automated testing verifies functional contracts and prevents regression bugs from reaching production."
            },
            {
                "question_text": "Which database indexing strategy is most effective for speeding up range queries on high-cardinality timestamp fields?",
                "skill": "Databases & Storage",
                "difficulty": "INTERMEDIATE",
                "options": [
                    "A B-tree index on the timestamp column.",
                    "A Hash index, which optimizes range lookups.",
                    "Omitting all indexes to maximize disk sequential writes.",
                    "Creating an unindexed text dump of the table."
                ],
                "correct_option_index": 0,
                "explanation": "B-tree indexes maintain sorted key order, making range queries (BETWEEN, >, <) highly efficient (O(log N))."
            }
        ]
    }
