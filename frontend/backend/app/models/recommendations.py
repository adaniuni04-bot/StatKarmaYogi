import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False, index=True)
    recommendation_score = Column(Float, nullable=False)  # 0.0 to 1.0 (or 0-100)
    rank = Column(Integer, default=1)
    reason_codes = Column(Text, nullable=True)  # JSON array: ["CRITICAL_SKILL_GAP", "ROLE_RELEVANT"]
    matched_competencies = Column(Text, nullable=True)  # JSON array
    gap_addressed = Column(Text, nullable=True)  # JSON object
    explanation = Column(Text, nullable=False)  # Deterministic generated explanation
    expected_outcome = Column(Text, nullable=True)
    is_saved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="recommendations")
    resource = relationship("Resource")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    current_score = Column(Float, nullable=False)
    required_score = Column(Float, nullable=False)
    gap = Column(Float, nullable=False)  # max(0, required - current)
    status = Column(String(20), default="GAP")  # MET, GAP
    priority_score = Column(Float, default=0.0)
    priority_level = Column(String(20), default="MEDIUM")  # CRITICAL, HIGH, MEDIUM, LOW
    confidence = Column(Float, default=0.5)
    last_updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    competency = relationship("Competency")
