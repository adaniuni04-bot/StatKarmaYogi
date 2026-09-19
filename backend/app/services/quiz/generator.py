from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.competencies import Competency
from app.models.assessments import Question, QuestionOption
from app.models.documents import Document
from app.services.ai.factory import get_llm_provider
from app.services.rag.vector_store import search_chunks
from app.services.quiz.validator import validate_mcq_deterministic
from app.schemas.quiz import MCQGenerateRequest, MCQGenerateResponse, GeneratedMCQSchema


async def generate_mcqs_pipeline(
    db: Session,
    request: MCQGenerateRequest
) -> MCQGenerateResponse:
    # 1. Retrieve authoritative content chunks
    query_topic = request.focus_topic or request.competency_code
    chunks = await search_chunks(db, query=query_topic, top_k=3, competency_code=request.competency_code)

    context_text = "\n\n".join([f"Source ({c['title']}, Page {c['page_number']}):\n{c['content']}" for c in chunks])
    if not context_text:
        context_text = f"Official Statistical Standards and Guidelines relating to {request.competency_code}."

    # 2. Build structured generation prompt
    prompt = (
        f"Generate {request.count} challenging, high-quality multiple choice assessment questions for government statistical officials.\n\n"
        f"Target Competency: {request.competency_code}\n"
        f"Difficulty: {request.difficulty}\n"
        f"Official Context:\n{context_text}\n\n"
        "Format requirements: JSON with an array of objects with fields:\n"
        "- question_text\n"
        "- question_type ('SINGLE_CHOICE')\n"
        "- options (array of 4 unique strings)\n"
        "- correct_option_index (0 to 3 integer)\n"
        "- explanation (comprehensive rationale grounded in statistical principles)\n"
        "- competency_code\n"
        "- subcompetency_code\n"
        "- difficulty\n"
        "- source_reference"
    )

    llm = get_llm_provider()
    raw_data = await llm.generate_structured(prompt=prompt)

    generated_items = raw_data.get("questions", [])
    valid_mcqs: List[GeneratedMCQSchema] = []

    # Competency reference lookup
    comp = db.query(Competency).filter(Competency.code == request.competency_code).first()
    comp_id = comp.id if comp else None

    for item in generated_items:
        try:
            mcq_schema = GeneratedMCQSchema(
                question_text=item.get("question_text", ""),
                question_type="SINGLE_CHOICE",
                options=item.get("options", []),
                correct_option_index=int(item.get("correct_option_index", 0)),
                explanation=item.get("explanation", ""),
                competency_code=request.competency_code,
                subcompetency_code=item.get("subcompetency_code"),
                difficulty=request.difficulty,
                source_reference=item.get("source_reference", "MoSPI Official Reference Manual")
            )

            is_valid, validation_errors = validate_mcq_deterministic(mcq_schema)
            if not is_valid:
                continue

            valid_mcqs.append(mcq_schema)

            # Persist question as GENERATED or VALIDATED for trainer review
            if comp_id:
                db_question = Question(
                    competency_id=comp_id,
                    subcompetency_code=mcq_schema.subcompetency_code,
                    question_type=mcq_schema.question_type,
                    difficulty=mcq_schema.difficulty,
                    question_text=mcq_schema.question_text,
                    explanation=mcq_schema.explanation,
                    source_reference=mcq_schema.source_reference,
                    source_tier="TIER_A",
                    generated_by="AI_QWEN",
                    validation_status="VALIDATED" if is_valid else "DRAFT",
                    ai_validation_score=1.0 if is_valid else 0.5,
                    validation_feedback="; ".join(validation_errors) if validation_errors else "Passed all deterministic quality checks."
                )
                db.add(db_question)
                db.flush()

                for opt_idx, opt_text in enumerate(mcq_schema.options):
                    db_opt = QuestionOption(
                        question_id=db_question.id,
                        option_text=opt_text,
                        is_correct=(opt_idx == mcq_schema.correct_option_index),
                        order_index=opt_idx
                    )
                    db.add(db_opt)

        except Exception:
            continue

    db.commit()

    return MCQGenerateResponse(
        questions=valid_mcqs,
        total_generated=len(valid_mcqs),
        model_used=type(llm).__name__,
        source_grounded=len(chunks) > 0
    )
