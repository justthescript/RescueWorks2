from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models
from .deps import get_current_user, get_db

ROLE_SUPER_ADMIN = "super_admin"
ROLE_ADMIN = "admin"
ROLE_APPLICATION_SCREENER = "application_screener"
ROLE_PET_COORDINATOR = "pet_coordinator"
ROLE_EVENT_COORDINATOR = "event_coordinator"
ROLE_VETERINARIAN = "veterinarian"
ROLE_BILLING_MANAGER = "billing_manager"
ROLE_ADOPTER = "adopter"
ROLE_FOSTER = "foster"
ROLE_VOLUNTEER = "volunteer"
ROLE_BOARD_MEMBER = "board_member"


def _user_has_any_role(user: models.User, db: Session, role_names: List[str]) -> bool:
    if not role_names:
        return True
    q = (
        db.query(models.Role)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .filter(models.UserRole.user_id == user.id)
    )
    user_roles = [r.name for r in q.all()]
    return any(r in user_roles for r in role_names)


def require_any_role(role_names: List[str]):
    def dependency(
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> models.User:
        if not _user_has_any_role(current_user, db, role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return dependency
