from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class QuestionOptionResponse(BaseModel):
    id: str
    option_text: str
    order_index: int

    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    id: str
    competency_id: str
    question_type: str
    difficulty: str
    question_text: str
    scenario_text: Optional[str] = None
    options: List[QuestionOptionResponse] = []

    class Config:
        from_attributes = True


class AssessmentListResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    assessment_type: str
    competency_id: Optional[str] = None
    competency_name: Optional[str] = None
    difficulty: str
    duration_minutes: int
    passing_score: float
    question_count: int

    class Config:
        from_attributes = True


class AssessmentDetailResponse(AssessmentListResponse):
    questions: List[QuestionResponse] = []


class SubmitAnswerItem(BaseModel):
    question_id: str
    selected_option_id: Optional[str] = None
    text_response: Optional[str] = None


class AssessmentSubmitRequest(BaseModel):
    attempt_id: str
    answers: List[SubmitAnswerItem]
    time_taken_seconds: Optional[int] = 0


class QuestionEvaluationResult(BaseModel):
    question_id: str
    question_text: str
    user_selected_option_id: Optional[str] = None
    correct_option_id: Optional[str] = None
    is_correct: bool
    explanation: Optional[str] = None
    source_reference: Optional[str] = None
    source_tier: Optional[str] = None


class AssessmentResultResponse(BaseModel):
    attempt_id: str
    assessment_id: str
    assessment_title: str
    score_percentage: float
    passed: bool
    points_earned: float
    total_points: float
    time_taken_seconds: int
    competency_updates: List[dict] = []
    question_results: List[QuestionEvaluationResult] = []
