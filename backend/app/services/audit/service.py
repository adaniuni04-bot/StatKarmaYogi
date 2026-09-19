import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def log_audit_event(
    db: Session,
    action: str,
    resource: str,
    actor_id: Optional[str] = None,
    actor_email: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    # Rule 37: Never log passwords or secrets
    sanitized_details = dict(details or {})
    for secret_key in ["password", "token", "secret", "authorization"]:
        sanitized_details.pop(secret_key, None)

    audit_entry = AuditLog(
        actor_id=actor_id,
        actor_email=actor_email,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details_json=json.dumps(sanitized_details),
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc)
    )
    db.add(audit_entry)
    db.commit()
    return audit_entry
