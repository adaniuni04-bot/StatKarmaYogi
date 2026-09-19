from typing import List, Dict, Any, Optional
from app.services.integrations.base import LearningProvider
from app.core.config import settings
from app.models.resources import Resource, ResourceCompetency
from app.models.competencies import Competency


MOCK_IGOT_COURSES = [
    {
        "external_id": "igot-stat-101",
        "title": "Sampling Techniques and Estimation in Official Surveys",
        "description": "Comprehensive course covering stratified sampling, probability proportional to size (PPS), and variance estimation for NSS/PLFS surveys.",
        "url": "https://igotkarmayogi.gov.in/course/sampling-techniques-official-surveys",
        "duration_minutes": 180,
        "difficulty": "INTERMEDIATE",
        "language": "en",
        "authority_tier": "TIER_A",
        "source_organization": "iGOT Karmayogi / MoSPI",
        "learning_outcomes": "Design stratified multistage samples and apply multiplier weights for survey estimates.",
        "competency_codes": ["SAMPLING", "SURVEY_DESIGN"],
        "mock_data": True
    },
    {
        "external_id": "igot-stat-102",
        "title": "Python for Statistical Production & Microdata Analytics",
        "description": "Practical hands-on training on Pandas, NumPy, and Statsmodels for processing large-scale NSS unit-level datasets.",
        "url": "https://igotkarmayogi.gov.in/course/python-microdata-analytics",
        "duration_minutes": 240,
        "difficulty": "INTERMEDIATE",
        "language": "en",
        "authority_tier": "TIER_A",
        "source_organization": "iGOT Karmayogi",
        "learning_outcomes": "Clean, merge, and tabulate survey microdata using Python scripting.",
        "competency_codes": ["PYTHON", "DATA_ANALYTICS"],
        "mock_data": True
    },
    {
        "external_id": "igot-stat-103",
        "title": "SQL for Government Database Querying & Administrative Records",
        "description": "Learn relational querying, aggregation, window functions, and indexing on state-level statistical databases.",
        "url": "https://igotkarmayogi.gov.in/course/sql-government-databases",
        "duration_minutes": 120,
        "difficulty": "BASIC",
        "language": "en",
        "authority_tier": "TIER_A",
        "source_organization": "iGOT Karmayogi",
        "learning_outcomes": "Write complex SQL joins, aggregations, and subqueries on administrative registers.",
        "competency_codes": ["SQL", "DATA_QUALITY"],
        "mock_data": True
    },
    {
        "external_id": "igot-stat-104",
        "title": "Artificial Intelligence & Machine Learning in Official Statistics",
        "description": "Exploration of modern machine learning for automated classification, satellite image crop estimation, and anomaly detection.",
        "url": "https://igotkarmayogi.gov.in/course/ai-ml-official-statistics",
        "duration_minutes": 180,
        "difficulty": "INTERMEDIATE",
        "language": "en",
        "authority_tier": "TIER_A",
        "source_organization": "iGOT Karmayogi / NSO",
        "learning_outcomes": "Understand AI use cases in official data collection, imputation, and validation.",
        "competency_codes": ["AI_ML", "BIG_DATA"],
        "mock_data": True
    },
    {
        "external_id": "igot-stat-105",
        "title": "National Quality Assurance Framework (NQAF) Implementation",
        "description": "Operational guidelines for assuring quality across institutional environment, statistical processes, and statistical outputs.",
        "url": "https://igotkarmayogi.gov.in/course/nqaf-implementation",
        "duration_minutes": 150,
        "difficulty": "FOUNDATION",
        "language": "en",
        "authority_tier": "TIER_A",
        "source_organization": "iGOT Karmayogi / UNSD",
        "learning_outcomes": "Audit statistical outputs against international NQAF quality dimensions.",
        "competency_codes": ["DATA_QUALITY", "OFFICIAL_STATISTICS"],
        "mock_data": True
    }
]


class MockIGOTProvider(LearningProvider):
    async def get_courses(self) -> List[Dict[str, Any]]:
        return MOCK_IGOT_COURSES

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        for c in MOCK_IGOT_COURSES:
            if c["external_id"] == course_id:
                return c
        return None

    async def sync_catalog(self, db_session: Any) -> int:
        count = 0
        for item in MOCK_IGOT_COURSES:
            existing = db_session.query(Resource).filter(
                Resource.provider == "IGOT",
                Resource.external_id == item["external_id"]
            ).first()

            if not existing:
                res = Resource(
                    provider="IGOT",
                    external_id=item["external_id"],
                    resource_type="IGOT_COURSE",
                    title=item["title"],
                    description=item["description"],
                    url=item["url"],
                    duration_minutes=item["duration_minutes"],
                    difficulty=item["difficulty"],
                    language=item["language"],
                    authority_tier=item["authority_tier"],
                    source_organization=item["source_organization"],
                    learning_outcomes=item["learning_outcomes"],
                    mock_data=True,
                    active=True
                )
                db_session.add(res)
                db_session.flush()

                for c_code in item["competency_codes"]:
                    comp = db_session.query(Competency).filter(Competency.code == c_code).first()
                    if comp:
                        db_session.add(ResourceCompetency(
                            resource_id=res.id,
                            competency_id=comp.id,
                            relevance_score=0.95
                        ))
                count += 1
        db_session.commit()
        return count


class RealIGOTProvider(LearningProvider):
    """Placeholder adapter for real iGOT API once official credentials and specs are provided."""
    async def get_courses(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Real iGOT API credentials not configured. Use MockIGOTProvider.")

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Real iGOT API credentials not configured.")

    async def sync_catalog(self, db_session: Any) -> int:
        raise NotImplementedError("Real iGOT API credentials not configured.")


def get_igot_provider() -> LearningProvider:
    if settings.IGOT_MODE == "real":
        return RealIGOTProvider()
    return MockIGOTProvider()
