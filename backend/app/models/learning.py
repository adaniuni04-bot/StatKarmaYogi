import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    target_role = Column(String(100), nullable=True)
    status = Column(String(50), default="ACTIVE")  # ACTIVE, COMPLETED, ARCHIVED
    overall_progress = Column(Float, default=0.0)  # 0 to 100%
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="learning_paths")
    items = relationship("LearningPathItem", back_populates="learning_path", cascade="all, delete-orphan", order_by="LearningPathItem.stage_order")


class LearningPathItem(Base):
    __tablename__ = "learning_path_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    learning_path_id = Column(String(36), ForeignKey("learning_paths.id"), nullable=False, index=True)
    stage_order = Column(Integer, default=1)  # 1: Foundation, 2: Core Knowledge, 3: Practical, 4: Assessment, 5: Advanced
    stage_name = Column(String(100), default="Foundation")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=True)
    competency_focus = Column(String(100), nullable=True)
    status = Column(String(50), default="NOT_STARTED")  # NOT_STARTED, IN_PROGRESS, COMPLETED
    estimated_minutes = Column(Integer, default=60)
    completed_at = Column(DateTime, nullable=True)

    learning_path = relationship("LearningPath", back_populates="items")
    resource = relationship("Resource", back_populates="learning_path_items")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False, index=True)
    status = Column(String(50), default="ENROLLED")  # ENROLLED, IN_PROGRESS, COMPLETED
    progress_percentage = Column(Float, default=0.0)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    resource = relationship("Resource")
