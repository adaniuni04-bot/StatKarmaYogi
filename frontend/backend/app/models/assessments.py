import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    assessment_type = Column(String(50), default="SKILL")  # DIAGNOSTIC, SKILL, COURSE, ADAPTIVE, FINAL
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=True, index=True)
    difficulty = Column(String(50), default="INTERMEDIATE")
    duration_minutes = Column(Integer, default=30)
    passing_score = Column(Float, default=60.0)
    is_adaptive = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    questions = relationship("Question", back_populates="assessment", cascade="all, delete-orphan")
    attempts = relationship("AssessmentAttempt", back_populates="assessment", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=True, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    subcompetency_code = Column(String(100), nullable=True)
    question_type = Column(String(50), default="SINGLE_CHOICE")  # SINGLE_CHOICE, SCENARIO, TRUE_FALSE, SHORT_ANSWER
    difficulty = Column(String(50), default="INTERMEDIATE")  # FOUNDATION, BASIC, INTERMEDIATE, ADVANCED, EXPERT
    question_text = Column(Text, nullable=False)
    scenario_text = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)  # e.g. "MoSPI Sampling Techniques Manual (Section 4.2)"
    source_page = Column(Integer, nullable=True)
    source_tier = Column(String(10), default="TIER_A")
    generated_by = Column(String(50), default="SYSTEM")  # SYSTEM, AI_QWEN, AI_GEMINI, TRAINER
    validation_status = Column(String(50), default="PUBLISHED")  # DRAFT, GENERATED, VALIDATED, APPROVED, PUBLISHED
    ai_validation_score = Column(Float, default=1.0)
    validation_feedback = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    assessment = relationship("Assessment", back_populates="questions")
    competency_rel = relationship("Competency", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.order_index")


class QuestionOption(Base):
    __tablename__ = "question_options"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)
    explanation = Column(Text, nullable=True)

    question = relationship("Question", back_populates="options")


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    assessment_id = Column(String(36), ForeignKey("assessments.id"), nullable=False, index=True)
    status = Column(String(50), default="IN_PROGRESS")  # IN_PROGRESS, SUBMITTED, EVALUATED
    score = Column(Float, default=0.0)  # Percentage 0-100
    points_earned = Column(Float, default=0.0)
    total_points = Column(Float, default=0.0)
    passed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    submitted_at = Column(DateTime, nullable=True)
    time_taken_seconds = Column(Integer, default=0)

    user = relationship("User", back_populates="assessment_attempts")
    assessment = relationship("Assessment", back_populates="attempts")
    responses = relationship("AssessmentResponse", back_populates="attempt", cascade="all, delete-orphan")


class AssessmentResponse(Base):
    __tablename__ = "assessment_responses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    attempt_id = Column(String(36), ForeignKey("assessment_attempts.id"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id"), nullable=False, index=True)
    selected_option_id = Column(String(36), ForeignKey("question_options.id"), nullable=True)
    text_response = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    points_awarded = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)

    attempt = relationship("AssessmentAttempt", back_populates="responses")
    question = relationship("Question")
    selected_option = relationship("QuestionOption")
