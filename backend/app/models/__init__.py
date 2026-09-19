from app.db.base import Base
from app.models.users import User, Department, Designation
from app.models.competencies import (
    CompetencyDomain,
    Competency,
    SubCompetency,
    CompetencyLevel,
    RoleCompetency,
    UserCompetency,
    CompetencyHistory,
)
from app.models.resources import (
    Resource,
    ResourceCompetency,
    TrainingProgramme,
)
from app.models.assessments import (
    Assessment,
    Question,
    QuestionOption,
    AssessmentAttempt,
    AssessmentResponse,
)
from app.models.learning import (
    LearningPath,
    LearningPathItem,
    Enrollment,
)
from app.models.documents import (
    Document,
    DocumentChunk,
)
from app.models.recommendations import (
    Recommendation,
    SkillGap,
)
from app.models.tutor import (
    AITutorSession,
    AITutorMessage,
)
from app.models.future_skills import FutureSkill
from app.models.audit import AuditLog, SystemConfig

__all__ = [
    "Base",
    "User",
    "Department",
    "Designation",
    "CompetencyDomain",
    "Competency",
    "SubCompetency",
    "CompetencyLevel",
    "RoleCompetency",
    "UserCompetency",
    "CompetencyHistory",
    "Resource",
    "ResourceCompetency",
    "TrainingProgramme",
    "Assessment",
    "Question",
    "QuestionOption",
    "AssessmentAttempt",
    "AssessmentResponse",
    "LearningPath",
    "LearningPathItem",
    "Enrollment",
    "Document",
    "DocumentChunk",
    "Recommendation",
    "SkillGap",
    "AITutorSession",
    "AITutorMessage",
    "FutureSkill",
    "AuditLog",
    "SystemConfig",
]
