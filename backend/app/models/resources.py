import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    provider = Column(String(50), nullable=False, index=True)  # IGOT, NSSTA, INTERNAL, UN_STATS
    external_id = Column(String(100), nullable=True)
    resource_type = Column(String(50), nullable=False)  # IGOT_COURSE, NSSTA_PROGRAM, VIDEO, PDF, ARTICLE, LAB
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, default=60)
    difficulty = Column(String(50), default="INTERMEDIATE")  # FOUNDATION, BASIC, INTERMEDIATE, ADVANCED, EXPERT
    language = Column(String(20), default="en")
    authority_tier = Column(String(10), default="TIER_A", index=True)  # TIER_A, TIER_B, TIER_C, TIER_D
    source_organization = Column(String(255), default="MoSPI")
    learning_outcomes = Column(Text, nullable=True)
    mock_data = Column(Boolean, default=True)  # Clearly labels demo mock data
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    competencies = relationship("ResourceCompetency", back_populates="resource", cascade="all, delete-orphan")
    learning_path_items = relationship("LearningPathItem", back_populates="resource")


class ResourceCompetency(Base):
    __tablename__ = "resource_competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resource_id = Column(String(36), ForeignKey("resources.id"), nullable=False, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    relevance_score = Column(Float, default=1.0)  # 0.1 to 1.0

    resource = relationship("Resource", back_populates="competencies")
    competency = relationship("Competency", back_populates="resource_competencies")


class TrainingProgramme(Base):
    __tablename__ = "training_programmes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_days = Column(Integer, default=5)
    target_cadre = Column(String(100), default="Statistical Officers / ISS")
    mode = Column(String(50), default="RESIDENTIAL")  # RESIDENTIAL, ONLINE, HYBRID
    location = Column(String(255), default="NSSTA Greater Noida")
    schedule = Column(String(255), nullable=True)
    eligibility = Column(Text, nullable=True)
    competency_focus = Column(String(255), nullable=True)
    authority_tier = Column(String(10), default="TIER_A")
    mock_data = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
