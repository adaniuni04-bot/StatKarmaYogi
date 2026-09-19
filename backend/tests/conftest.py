import pytest
from app.db.session import SessionLocal
from app.models.users import User
from app.models.competencies import Competency, UserCompetency


BASELINE_SCORES = {
    "SAMPLING": 42.0,
    "PYTHON": 70.0,
    "SQL": 30.0,
    "GIS": 20.0,
    "AI_ML": 31.0,
    "DATA_VISUALIZATION": 74.0,
}


@pytest.fixture(autouse=True)
def reset_demo_user_competencies():
    """Ensures Rahul's baseline scores are reset for repeatable testing."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "employee@example.com").first()
        if user:
            for code, score in BASELINE_SCORES.items():
                comp = db.query(Competency).filter(Competency.code == code).first()
                if comp:
                    uc = db.query(UserCompetency).filter(
                        UserCompetency.user_id == user.id,
                        UserCompetency.competency_id == comp.id
                    ).first()
                    if uc:
                        uc.score = score
            db.commit()
        yield
    finally:
        db.close()
