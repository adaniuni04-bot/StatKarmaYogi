import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class AITutorSession(Base):
    __tablename__ = "ai_tutor_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), default="Statistical Discussion")
    topic = Column(String(100), nullable=True)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="tutor_sessions")
    messages = relationship("AITutorMessage", back_populates="session", cascade="all, delete-orphan", order_by="AITutorMessage.created_at")


class AITutorMessage(Base):
    __tablename__ = "ai_tutor_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("ai_tutor_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)  # JSON list of citations: title, org, page, tier
    confidence = Column(Float, default=1.0)
    is_grounded = Column(Boolean, default=True)
    suggested_practice_question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("AITutorSession", back_populates="messages")
