import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Text
from app.db.base import Base


class FutureSkill(Base):
    __tablename__ = "future_skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    domain = Column(String(100), default="Technical / AI")
    current_readiness = Column(Float, default=25.0)  # Percentage org readiness 0-100
    expected_importance = Column(Float, default=85.0)  # Expected future importance 0-100
    gap = Column(Float, default=60.0)
    priority = Column(String(20), default="HIGH")  # CRITICAL, HIGH, MEDIUM
    recommended_training = Column(Text, nullable=True)
    trend_source = Column(String(255), default="UN Statistical Commission / MoSPI Modernization Vision 2026")
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
