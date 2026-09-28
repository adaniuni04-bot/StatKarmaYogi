from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSkillInput(BaseModel):
    skill: str
    level: str = "Intermediate"  # Foundation, Beginner, Intermediate, Advanced, Expert


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "EMPLOYEE"
    field: Optional[str] = "Computer Science & Software Engineering"
    position: Optional[str] = "Full-Stack Engineer"
    skills: Optional[List[UserSkillInput]] = []
    years_experience: Optional[int] = 0
    education: Optional[str] = "Bachelor's Degree in Computer Science"
    career_goal: Optional[str] = "Lead Solutions Architect"
    organization: Optional[str] = "Enterprise Tech"
    preferred_learning_style: Optional[str] = "Hands-on projects & labs"
    weekly_hours: Optional[str] = "10 hours/week"
    current_project_focus: Optional[str] = "Full-stack web application development"

    # Backward compatibility optional parameters
    designation_id: Optional[str] = None
    designation_name: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    cadre: Optional[str] = None
    current_assignment: Optional[str] = None
    technical_skills: Optional[str] = None
    preferred_language: Optional[str] = "en"


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    field: Optional[str] = None
    position: Optional[str] = None
    organization: Optional[str] = None
    years_experience: Optional[int] = None
    education: Optional[str] = None
    career_goal: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    weekly_hours: Optional[str] = None
    current_project_focus: Optional[str] = None
    preferred_language: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    field: Optional[str] = None
    position: Optional[str] = None
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    designation_id: Optional[str] = None
    designation_name: Optional[str] = None
    organization: str
    years_experience: int
    education: Optional[str] = None
    current_assignment: Optional[str] = None
    career_goal: Optional[str] = None
    preferred_learning_style: Optional[str] = None
    weekly_hours: Optional[str] = None
    current_project_focus: Optional[str] = None
    skills: Optional[List[Dict[str, Any]]] = None
    preferred_language: str
    status: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class FrameworkMetadataOptions(BaseModel):
    job_fields: List[Dict[str, Any]]
    skills_by_category: List[Dict[str, Any]]
    proficiency_levels: List[Dict[str, Any]]
    qualifications: List[str]

    # Backward compatibility
    designations: List[dict] = []
    departments: List[dict] = []
    cadres: List[str] = []
    common_assignments: List[str] = []
