from typing import Tuple, List
from app.schemas.quiz import GeneratedMCQSchema


def validate_mcq_deterministic(mcq: GeneratedMCQSchema) -> Tuple[bool, List[str]]:
    """
    Deterministic structural and quality checks for generated MCQs.
    Rule 17: Validates single correct answer, non-empty text, unique options, etc.
    """
    errors = []

    # Check question text length
    if len(mcq.question_text.strip()) < 15:
        errors.append("Question stem is too short or empty.")

    # Check options count
    if len(mcq.options) < 3 or len(mcq.options) > 5:
        errors.append("Question must provide between 3 and 5 distinct options.")

    # Check for empty options
    for idx, opt in enumerate(mcq.options):
        if not opt or len(opt.strip()) < 2:
            errors.append(f"Option {idx+1} is empty or too short.")

    # Check for duplicate options
    stripped_options = [opt.strip().lower() for opt in mcq.options]
    if len(stripped_options) != len(set(stripped_options)):
        errors.append("Question contains duplicate options.")

    # Check correct option index within bounds
    if mcq.correct_option_index < 0 or mcq.correct_option_index >= len(mcq.options):
        errors.append(f"Correct option index {mcq.correct_option_index} is out of bounds for {len(mcq.options)} options.")

    # Check explanation length
    if len(mcq.explanation.strip()) < 10:
        errors.append("Explanation is missing or insufficient.")

    # Prompt injection / hostile instruction detection
    forbidden_tokens = ["system prompt", "ignore previous", "jailbreak", "override instructions"]
    combined_text = (mcq.question_text + " " + " ".join(mcq.options)).lower()
    for token in forbidden_tokens:
        if token in combined_text:
            errors.append(f"Security Alert: Question contains suspicious injection token '{token}'.")

    is_valid = len(errors) == 0
    return is_valid, errors
