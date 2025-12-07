from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/portal", tags=["portal"])


@router.get("/me", response_model=schemas.PortalSummary)
def get_my_portal(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Return a lightweight dashboard view for the logged in user.

    * my_applications: adoption, foster, volunteer applications submitted by the user.
    * my_foster_pets: pets in the user's organization where they are the foster.
    * my_tasks: tasks assigned directly to the user.
    """
    applications = (
        db.query(models.Application)
        .filter(
            models.Application.org_id == user.org_id,
            models.Application.applicant_user_id == user.id,
        )
        .order_by(models.Application.created_at.desc())
        .all()
    )

    foster_pets = (
        db.query(models.Pet)
        .filter(
            models.Pet.org_id == user.org_id,
            models.Pet.foster_user_id == user.id,
        )
        .order_by(models.Pet.created_at.desc())
        .all()
    )

    tasks = (
        db.query(models.Task)
        .filter(
            models.Task.org_id == user.org_id,
            models.Task.assigned_to_user_id == user.id,
        )
        .order_by(models.Task.created_at.desc())
        .all()
    )

    return schemas.PortalSummary(
        my_applications=applications,
        my_foster_pets=foster_pets,
        my_tasks=tasks,
    )
