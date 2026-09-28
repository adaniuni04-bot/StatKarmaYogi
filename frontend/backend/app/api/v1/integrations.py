from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.services.integrations.igot.adapter import get_igot_provider
from app.services.integrations.nssta.adapter import get_nssta_provider
from app.api.deps import get_current_user, RoleChecker
from app.services.audit.service import log_audit_event

router = APIRouter(prefix="/integrations", tags=["Integrations (iGOT & NSSTA)"])


@router.get("/status")
def get_integrations_status():
    return {
        "igot_karmayogi": {
            "mode": settings.IGOT_MODE,
            "status": "active (mock adapter)" if settings.IGOT_MODE == "mock" else "active",
            "provider_class": "MockIGOTProvider" if settings.IGOT_MODE == "mock" else "RealIGOTProvider",
            "mock_data_notice": "DEMO/MOCK Courses seeded. Ready for official API token."
        },
        "nssta_academy": {
            "mode": settings.NSSTA_MODE,
            "status": "active (mock adapter)" if settings.NSSTA_MODE == "mock" else "active",
            "provider_class": "MockNSSTAProvider" if settings.NSSTA_MODE == "mock" else "RealNSSTAProvider",
            "mock_data_notice": "DEMO/MOCK Training calendar seeded. Ready for academy sync."
        }
    }


@router.post("/igot/sync")
async def sync_igot(
    current_user = Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    provider = get_igot_provider()
    count = await provider.sync_catalog(db)
    log_audit_event(db, action="IGOT_SYNC", resource="Integration", actor_id=current_user.id, details={"synced": count})
    return {"status": "success", "synced_courses": count, "provider": "iGOT Karmayogi [DEMO]"}


@router.post("/nssta/sync")
async def sync_nssta(
    current_user = Depends(RoleChecker(["ADMIN", "SUPER_ADMIN"])),
    db: Session = Depends(get_db)
):
    provider = get_nssta_provider()
    count = await provider.sync_calendar(db)
    log_audit_event(db, action="NSSTA_SYNC", resource="Integration", actor_id=current_user.id, details={"synced": count})
    return {"status": "success", "synced_programmes": count, "provider": "NSSTA Training Academy [DEMO]"}
