from typing import Optional

from sqlalchemy.orm import Session

from . import models


def log_action(
    db: Session,
    org_id: int,
    user_id: Optional[int],
    entity_type: str,
    entity_id: Optional[int],
    action: str,
    details: Optional[str] = None,
) -> models.AuditLog:
    log = models.AuditLog(
        org_id=org_id,
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        details=details,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
