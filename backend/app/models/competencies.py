import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class CompetencyDomain(Base):
    __tablename__ = "competency_domains"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), nullable=False, unique=True, index=True)  # STATISTICAL, TECHNICAL, DIGITAL_GOVERNANCE, BEHAVIOURAL
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    competencies = relationship("Competency", back_populates="domain", cascade="all, delete-orphan")


class Competency(Base):
    __tablename__ = "competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    domain_id = Column(String(36), ForeignKey("competency_domains.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    definition = Column(Text, nullable=True)
    version = Column(String(20), default="1.0")
    active = Column(Boolean, default=True)
    future_relevance = Column(Float, default=1.0)  # Multiplier for future importance
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    domain = relationship("CompetencyDomain", back_populates="competencies")
    subcompetencies = relationship("SubCompetency", back_populates="competency", cascade="all, delete-orphan")
    role_competencies = relationship("RoleCompetency", back_populates="competency", cascade="all, delete-orphan")
    user_competencies = relationship("UserCompetency", back_populates="competency", cascade="all, delete-orphan")
    resource_competencies = relationship("ResourceCompetency", back_populates="competency", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="competency_rel")


class SubCompetency(Base):
    __tablename__ = "subcompetencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    competency = relationship("Competency", back_populates="subcompetencies")


class CompetencyLevel(Base):
    __tablename__ = "competency_levels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(Integer, nullable=False, unique=True)  # 1, 2, 3, 4, 5
    name = Column(String(100), nullable=False)  # Foundation, Basic, Intermediate, Advanced, Expert
    description = Column(Text, nullable=True)
    score_min = Column(Float, nullable=False)
    score_max = Column(Float, nullable=False)


class RoleCompetency(Base):
    __tablename__ = "role_competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    designation_id = Column(String(36), ForeignKey("designations.id"), nullable=False, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    required_level = Column(Integer, default=3)  # 1-5
    required_score = Column(Float, nullable=False)  # 0-100
    importance = Column(Float, default=1.0)  # 0.5 to 1.5 multiplier
    mandatory = Column(Boolean, default=True)
    future_relevance = Column(Float, default=1.0)
    department_specific = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    designation = relationship("Designation", back_populates="role_competencies")
    competency = relationship("Competency", back_populates="role_competencies")


class UserCompetency(Base):
    __tablename__ = "user_competencies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)  # Normalized 0-100
    level = Column(Integer, default=1)  # 1-5
    level_name = Column(String(50), default="Foundation")
    confidence = Column(Float, default=0.5)  # 0.0 to 1.0
    evidence_count = Column(Integer, default=1)
    last_assessed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String(50), default="DIAGNOSTIC")  # SELF, DIAGNOSTIC, ASSESSMENT, TRAINING

    user = relationship("User", back_populates="user_competencies")
    competency = relationship("Competency", back_populates="user_competencies")


class CompetencyHistory(Base):
    __tablename__ = "competency_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    competency_id = Column(String(36), ForeignKey("competencies.id"), nullable=False, index=True)
    previous_score = Column(Float, nullable=False)
    new_score = Column(Float, nullable=False)
    delta = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)  # e.g. "Completed Assessment: Sampling Techniques"
    assessment_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="competency_history")
