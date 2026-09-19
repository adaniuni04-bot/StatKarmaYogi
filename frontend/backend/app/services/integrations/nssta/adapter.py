from typing import List, Dict, Any, Optional
from app.services.integrations.base import TrainingProvider
from app.core.config import settings
from app.models.resources import TrainingProgramme, Resource, ResourceCompetency
from app.models.competencies import Competency


MOCK_NSSTA_PROGRAMMES = [
    {
        "code": "NSSTA-PROG-2026-01",
        "title": "Advanced Survey Sampling & Variance Estimation Workshop",
        "description": "Intensive 5-day residential programme at NSSTA Greater Noida focusing on complex multistage sampling, calibration weighting, and Jackknife/Bootstrap variance.",
        "duration_days": 5,
        "target_cadre": "Indian Statistical Service (ISS) & Subordinate Statistical Service (SSS)",
        "mode": "RESIDENTIAL",
        "location": "NSSTA Campus, Greater Noida, Uttar Pradesh",
        "schedule": "Oct 12 - Oct 16, 2026",
        "eligibility": "Officers working in FOD, SDRD, and State Directorates of Economics and Statistics (DES).",
        "competency_codes": ["SAMPLING", "SURVEY_DESIGN"],
        "authority_tier": "TIER_A",
        "mock_data": True
    },
    {
        "code": "NSSTA-PROG-2026-02",
        "title": "System of National Accounts (SNA 2008) & State Income Compilation",
        "description": "Methodological training on gross state domestic product (GSDP), supply and use tables (SUT), and financial intermediation services indirectly measured (FISIM).",
        "duration_days": 5,
        "target_cadre": "Statistical Officers & Research Officers (National Accounts Division)",
        "mode": "RESIDENTIAL",
        "location": "NSSTA Campus, Greater Noida",
        "schedule": "Nov 02 - Nov 06, 2026",
        "eligibility": "Minimum 2 years experience in economic statistics or macro compilation.",
        "competency_codes": ["NATIONAL_ACCOUNTS", "OFFICIAL_STATISTICS"],
        "authority_tier": "TIER_A",
        "mock_data": True
    },
    {
        "code": "NSSTA-PROG-2026-03",
        "title": "Geospatial Data Processing (GIS) in Official Statistics & Census",
        "description": "Hands-on application of QGIS, coordinate reference systems (CRS), spatial joins, and thematic cartography for census and survey planning.",
        "duration_days": 3,
        "target_cadre": "Survey Officers, FOD Officials, GIS Unit",
        "mode": "HYBRID",
        "location": "Online + NSSTA Greater Noida",
        "schedule": "Nov 18 - Nov 20, 2026",
        "eligibility": "Open to all MoSPI and state statistical personnel.",
        "competency_codes": ["GIS", "DATA_VISUALIZATION"],
        "authority_tier": "TIER_A",
        "mock_data": True
    },
    {
        "code": "NSSTA-PROG-2026-04",
        "title": "Machine Learning & Big Data for Price Statistics (CPI/WPI)",
        "description": "Modern methods for web-scraping online retail prices, automated barcode scanner data processing, and scanner price index construction.",
        "duration_days": 4,
        "target_cadre": "Price Statistics Division / Economic Statistics",
        "mode": "RESIDENTIAL",
        "location": "NSSTA Campus, Greater Noida",
        "schedule": "Dec 07 - Dec 10, 2026",
        "eligibility": "Familiarity with basic Python or R is recommended.",
        "competency_codes": ["PRICE_STATISTICS", "AI_ML", "PYTHON"],
        "authority_tier": "TIER_A",
        "mock_data": True
    }
]


class MockNSSTAProvider(TrainingProvider):
    async def get_programmes(self) -> List[Dict[str, Any]]:
        return MOCK_NSSTA_PROGRAMMES

    async def sync_calendar(self, db_session: Any) -> int:
        count = 0
        for item in MOCK_NSSTA_PROGRAMMES:
            existing = db_session.query(TrainingProgramme).filter(
                TrainingProgramme.code == item["code"]
            ).first()

            if not existing:
                prog = TrainingProgramme(
                    code=item["code"],
                    title=item["title"],
                    description=item["description"],
                    duration_days=item["duration_days"],
                    target_cadre=item["target_cadre"],
                    mode=item["mode"],
                    location=item["location"],
                    schedule=item["schedule"],
                    eligibility=item["eligibility"],
                    competency_focus=", ".join(item["competency_codes"]),
                    authority_tier=item["authority_tier"],
                    mock_data=True
                )
                db_session.add(prog)

                # Also insert as a learning resource so recommendation engine can recommend NSSTA courses!
                res = Resource(
                    provider="NSSTA",
                    external_id=item["code"],
                    resource_type="NSSTA_PROGRAM",
                    title=item["title"],
                    description=f"{item['description']} (Mode: {item['mode']}, Location: {item['location']})",
                    url="https://nssta.gov.in/calendar-2026",
                    duration_minutes=item["duration_days"] * 360,
                    difficulty="ADVANCED",
                    language="en",
                    authority_tier="TIER_A",
                    source_organization="National Statistical Systems Training Academy (NSSTA)",
                    learning_outcomes=f"Executive certification in {', '.join(item['competency_codes'])}",
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
                            relevance_score=1.0
                        ))
                count += 1
        db_session.commit()
        return count


class RealNSSTAProvider(TrainingProvider):
    async def get_programmes(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("Real NSSTA API credentials not configured. Use MockNSSTAProvider.")

    async def sync_calendar(self, db_session: Any) -> int:
        raise NotImplementedError("Real NSSTA API credentials not configured.")


def get_nssta_provider() -> TrainingProvider:
    if settings.NSSTA_MODE == "real":
        return RealNSSTAProvider()
    return MockNSSTAProvider()
