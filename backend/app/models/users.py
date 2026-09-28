import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="department")


class Designation(Base):
    __tablename__ = "designations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    cadre = Column(String(100), default="Indian Statistical Service (ISS)")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="designation_rel")
    role_competencies = relationship("RoleCompetency", back_populates="designation")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(50), default="EMPLOYEE")  # EMPLOYEE, TRAINER, ADMIN, SUPER_ADMIN
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True, index=True)
    designation_id = Column(String(36), ForeignKey("designations.id"), nullable=True, index=True)
    designation_name = Column(String(255), nullable=True)  # denormalized for convenience
    organization = Column(String(255), default="Ministry of Statistics and Programme Implementation (MoSPI)")
    years_experience = Column(Integer, default=0)
    education = Column(String(255), nullable=True)
    current_assignment = Column(String(255), nullable=True)
    career_goal = Column(String(255), nullable=True)
    industry_field = Column(String(255), nullable=True)
    ai_profile_json = Column(Text, nullable=True)
    preferred_learning_style = Column(String(255), nullable=True)
    weekly_hours = Column(String(50), nullable=True)
    current_project_focus = Column(Text, nullable=True)
    preferred_language = Column(String(10), default="en")
    status = Column(String(50), default="ACTIVE")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    department = relationship("Department", back_populates="users")
    designation_rel = relationship("Designation", back_populates="users")
    user_competencies = relationship("UserCompetency", back_populates="user", cascade="all, delete-orphan")
    competency_history = relationship("CompetencyHistory", back_populates="user", cascade="all, delete-orphan")
    assessment_attempts = relationship("AssessmentAttempt", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")
    tutor_sessions = relationship("AITutorSession", back_populates="user", cascade="all, delete-orphan")
