from typing import List, Optional
from pydantic import BaseModel, Field


class MCQOptionInput(BaseModel):
    option_text: str
    is_correct: bool


class GeneratedMCQSchema(BaseModel):
    question_text: str = Field(..., description="Clear question stem grounded in statistical concepts")
    question_type: str = Field(default="SINGLE_CHOICE")
    options: List[str] = Field(..., min_length=2, max_length=5, description="List of options")
    correct_option_index: int = Field(..., ge=0, le=4, description="0-indexed position of the correct answer")
    explanation: str = Field(..., description="Authoritative explanation of why the correct option is right")
    competency_code: str
    subcompetency_code: Optional[str] = None
    difficulty: str = Field(default="INTERMEDIATE")
    source_reference: Optional[str] = None


class MCQGenerateRequest(BaseModel):
    document_id: Optional[str] = None
    competency_code: str = "SAMPLING"
    count: int = Field(default=3, ge=1, le=10)
    difficulty: str = "INTERMEDIATE"
    focus_topic: Optional[str] = None


class MCQGenerateResponse(BaseModel):
    questions: List[GeneratedMCQSchema]
    total_generated: int
    model_used: str
    source_grounded: bool


class QuestionReviewActionRequest(BaseModel):
    question_id: str
    action: str  # APPROVE, REJECT, EDIT
    edited_text: Optional[str] = None
    edited_explanation: Optional[str] = None
