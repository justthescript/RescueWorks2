from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db
from ..permissions import ROLE_ADMIN, ROLE_SUPER_ADMIN, require_any_role

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/org", response_model=schemas.OrganizationSettings)
def get_org_settings(
    db: Session = Depends(get_db),
    current_user=Depends(require_any_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])),
):
    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.org_id == current_user.org_id)
        .first()
    )
    if not settings:
        settings = models.OrganizationSettings(org_id=current_user.org_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("/org", response_model=schemas.OrganizationSettings)
def update_org_settings(
    settings_in: schemas.OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_any_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])),
):
    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.org_id == current_user.org_id)
        .first()
    )
    if not settings:
        settings = models.OrganizationSettings(org_id=current_user.org_id)
        db.add(settings)
        db.flush()
    for field, value in settings_in.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
