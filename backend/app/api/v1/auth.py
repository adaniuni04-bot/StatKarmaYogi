import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.users import User, Department, Designation
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    FrameworkMetadataOptions
)
from app.services.audit.service import log_audit_event
from app.services.skill_gap.ai_engine import evaluate_dynamic_skill_gaps_with_ai, save_user_ai_profile
from app.services.learning.path_engine import generate_or_update_learning_path
from app.core.skills_catalog import get_skills_by_category
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/options", response_model=FrameworkMetadataOptions)
def get_registration_options(db: Session = Depends(get_db)):
    job_fields = [
        {
            "id": "cs_software",
            "name": "Computer Science & Software Engineering",
            "popular_positions": [
                "Full-Stack Engineer",
                "Frontend Engineer",
                "Backend Engineer",
                "Mobile App Developer (iOS / Android)",
                "Systems Software Engineer",
                "Embedded Systems Engineer",
                "API & Platform Engineer"
            ]
        },
        {
            "id": "ai_ml",
            "name": "Artificial Intelligence & Machine Learning",
            "popular_positions": [
                "AI Engineer",
                "Machine Learning Engineer",
                "AI Research Scientist",
                "Natural Language Processing (NLP) Engineer",
                "Computer Vision Engineer",
                "Generative AI & LLM Solutions Engineer",
                "MLOps Engineer"
            ]
        },
        {
            "id": "cloud_devops",
            "name": "Cloud Computing, DevOps & SRE",
            "popular_positions": [
                "Cloud Solutions Architect",
                "DevOps Engineer",
                "Site Reliability Engineer (SRE)",
                "Platform & Infrastructure Engineer",
                "Kubernetes & Container Specialist"
            ]
        },
        {
            "id": "data_analytics",
            "name": "Data Science, Analytics & Big Data",
            "popular_positions": [
                "Data Scientist",
                "Data Analyst",
                "Data Engineer",
                "Business Intelligence (BI) Architect",
                "Quantitative Analyst"
            ]
        },
        {
            "id": "cybersecurity",
            "name": "Cybersecurity & Information Assurance",
            "popular_positions": [
                "Cybersecurity Analyst",
                "Penetration Tester / Ethical Hacker",
                "Security Operations Center (SOC) Specialist",
                "Cloud Security Architect",
                "Application Security (AppSec) Engineer"
            ]
        },
        {
            "id": "product_tech_mgmt",
            "name": "Product Management & Tech Leadership",
            "popular_positions": [
                "Technical Product Manager",
                "Engineering Manager",
                "Scrum Master / Agile Coach",
                "Enterprise Solutions Consultant"
            ]
        },
        {
            "id": "design_uiux",
            "name": "UI/UX & Digital Product Design",
            "popular_positions": [
                "Product Designer",
                "UI/UX Designer",
                "Design Systems Engineer",
                "User Experience Researcher"
            ]
        },
        {
            "id": "finance_fintech",
            "name": "Finance, FinTech & Quantitative Trading",
            "popular_positions": [
                "Quantitative Developer",
                "FinTech Software Engineer",
                "Algorithmic Trading Analyst",
                "Financial Risk Data Modeler"
            ]
        },
        {
            "id": "other_custom",
            "name": "Other Industry / Custom Role",
            "popular_positions": [
                "Specialist Consultant",
                "Research Fellow",
                "Technical Educator",
                "Custom Position"
            ]
        }
    ]

    skills_by_category = get_skills_by_category()

    proficiency_levels = [
        {"code": "Foundation", "name": "Foundation (Level 1)", "numeric_score": 20, "description": "Basic theoretical knowledge and core terminology."},
        {"code": "Beginner", "name": "Beginner (Level 2)", "numeric_score": 40, "description": "Can perform standard tasks with guidance and code examples."},
        {"code": "Intermediate", "name": "Intermediate (Level 3)", "numeric_score": 60, "description": "Builds features and resolves issues independently in production."},
        {"code": "Advanced", "name": "Advanced (Level 4)", "numeric_score": 80, "description": "Deep architectural mastery, optimization, and code review leadership."},
        {"code": "Expert", "name": "Expert (Level 5)", "numeric_score": 100, "description": "Domain authority, complex innovation, and high-impact design."}
    ]

    qualifications = [
        "Bachelor of Science in Computer Science / Engineering",
        "Master of Science in Computer Science / AI / Data Science",
        "Bachelor of Technology (B.Tech / B.E.)",
        "Master of Technology (M.Tech)",
        "Bachelor's Degree in Mathematics / Statistics",
        "Master's Degree in Statistics / Econometrics",
        "Professional Coding Bootcamp Graduate",
        "Self-Taught / Open Source Contributor",
        "Ph.D. in Computer Science / Artificial Intelligence"
    ]

    return FrameworkMetadataOptions(
        job_fields=job_fields,
        skills_by_category=skills_by_category,
        proficiency_levels=proficiency_levels,
        qualifications=qualifications,
        designations=[],
        departments=[],
        cadres=[],
        common_assignments=[]
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    access_token = create_access_token(subject=user.id, role=user.role)
    log_audit_event(db, action="LOGIN", resource="User", actor_id=user.id, actor_email=user.email)

    user_skills = []
    if user.ai_profile_json:
        try:
            profile = json.loads(user.ai_profile_json)
            user_skills = profile.get("strengths", [])
        except Exception:
            pass

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            field=user.industry_field,
            position=user.designation_name,
            department_id=user.department_id,
            department_name=user.industry_field,
            designation_id=user.designation_id,
            designation_name=user.designation_name,
            organization=user.organization,
            years_experience=user.years_experience,
            education=user.education,
            current_assignment=user.current_assignment,
            career_goal=user.career_goal,
            skills=user_skills,
            preferred_language=user.preferred_language,
            status=user.status,
            created_at=user.created_at
        )
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )

    target_position = request.position or request.designation_name or "Full-Stack Engineer"
    target_field = request.field or request.department_name or "Computer Science & Software Engineering"

    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        role=request.role or "EMPLOYEE",
        designation_name=target_position,
        industry_field=target_field,
        organization=request.organization or "Tech Organization",
        years_experience=request.years_experience or 0,
        education=request.education,
        current_assignment=f"{target_position} - {target_field}",
        career_goal=request.career_goal or "Senior Lead Architect",
        preferred_learning_style=request.preferred_learning_style or "Hands-on projects & labs",
        weekly_hours=request.weekly_hours or "10 hours/week",
        current_project_focus=request.current_project_focus or "Full-stack development",
        preferred_language=request.preferred_language or "en",
        status="ACTIVE"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Convert declared skills from request
    declared_skills_list = []
    if request.skills:
        for s in request.skills:
            declared_skills_list.append({"skill": s.skill, "level": s.level})

    # Trigger dynamic AI evaluation using Ollama Qwen3:8b
    ai_profile = await evaluate_dynamic_skill_gaps_with_ai(
        target_role=target_position,
        industry_field=target_field,
        declared_skills=declared_skills_list,
        years_experience=request.years_experience or 0,
        career_goal=request.career_goal or target_position,
        preferred_learning_style=new_user.preferred_learning_style,
        weekly_hours=new_user.weekly_hours,
        current_project_focus=new_user.current_project_focus
    )

    # Persist the dynamic profile
    save_user_ai_profile(db, new_user, ai_profile)

    # Generate initial personalized learning path
    try:
        generate_or_update_learning_path(db, new_user.id)
    except Exception:
        pass

    access_token = create_access_token(subject=new_user.id, role=new_user.role)
    log_audit_event(db, action="REGISTER_DYNAMIC", resource="User", actor_id=new_user.id, actor_email=new_user.email)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            role=new_user.role,
            field=new_user.industry_field,
            position=new_user.designation_name,
            department_id=new_user.department_id,
            department_name=new_user.industry_field,
            designation_id=new_user.designation_id,
            designation_name=new_user.designation_name,
            organization=new_user.organization,
            years_experience=new_user.years_experience,
            education=new_user.education,
            current_assignment=new_user.current_assignment,
            career_goal=new_user.career_goal,
            preferred_learning_style=new_user.preferred_learning_style,
            weekly_hours=new_user.weekly_hours,
            current_project_focus=new_user.current_project_focus,
            skills=ai_profile.get("strengths", []),
            preferred_language=new_user.preferred_language,
            status=new_user.status,
            created_at=new_user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(user: User = Depends(get_current_user)):
    user_skills = []
    if user.ai_profile_json:
        try:
            profile = json.loads(user.ai_profile_json)
            user_skills = profile.get("strengths", [])
        except Exception:
            pass

    return UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        field=user.industry_field,
        position=user.designation_name,
        department_id=user.department_id,
        department_name=user.industry_field,
        designation_id=user.designation_id,
        designation_name=user.designation_name,
        organization=user.organization,
        years_experience=user.years_experience,
        education=user.education,
        current_assignment=user.current_assignment,
        career_goal=user.career_goal,
        preferred_learning_style=user.preferred_learning_style,
        weekly_hours=user.weekly_hours,
        current_project_focus=user.current_project_focus,
        skills=user_skills,
        preferred_language=user.preferred_language,
        status=user.status,
        created_at=user.created_at
    )


@router.post("/logout")
def logout(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log_audit_event(db, action="LOGOUT", resource="User", actor_id=user.id, actor_email=user.email)
    return {"status": "ok", "message": "Logged out successfully"}
