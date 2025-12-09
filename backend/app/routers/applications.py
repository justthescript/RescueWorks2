from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_APPLICATION_SCREENER,
    ROLE_SUPER_ADMIN,
    require_any_role,
)

router = APIRouter(prefix="/applications", tags=["applications"])


def _get_application_for_org(
    db: Session,
    org_id: int,
    app_id: int,
) -> models.Application:
    app = (
        db.query(models.Application)
        .filter(models.Application.id == app_id, models.Application.org_id == org_id)
        .first()
    )
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return app


@router.post("/", response_model=schemas.Application)
def create_application(
    app_in: schemas.ApplicationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new application. The applicant is always the current user."""
    if app_in.org_id != user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User org mismatch",
        )
    app = models.Application(
        org_id=app_in.org_id,
        applicant_user_id=user.id,
        pet_id=app_in.pet_id,
        type=app_in.type,
        answers_json=app_in.answers_json,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


@router.get("/", response_model=List[schemas.Application])
def list_applications(
    type: Optional[schemas.ApplicationType] = None,
    status_filter: Optional[schemas.ApplicationStatus] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    List applications for the current organization.

    Screeners and admins see all applications.
    Other users see only their own applications.
    """
    q = db.query(models.Application).filter(models.Application.org_id == user.org_id)

    # Role based visibility
    privileged = False
    for user_role in user.roles:
        # user_role is a UserRole instance, its Role object is in user_role.role
        if user_role.role and user_role.role.name in (
            ROLE_SUPER_ADMIN,
            ROLE_ADMIN,
            ROLE_APPLICATION_SCREENER,
        ):
            privileged = True
            break

    if not privileged:
        q = q.filter(models.Application.applicant_user_id == user.id)

    if type is not None:
        q = q.filter(models.Application.type == type)
    if status_filter is not None:
        q = q.filter(models.Application.status == status_filter)

    return q.order_by(models.Application.created_at.desc()).all()


@router.get("/{app_id}", response_model=schemas.Application)
def get_application(
    app_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Fetch a single application in the current organization."""
    app = _get_application_for_org(db, user.org_id, app_id)

    # Non privileged users can only see their own application
    if app.applicant_user_id != user.id:
        for role in user.roles:
            if role.role_name in (
                ROLE_SUPER_ADMIN,
                ROLE_ADMIN,
                ROLE_APPLICATION_SCREENER,
            ):
                break
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view this application",
            )
    return app


@router.patch(
    "/{app_id}",
    response_model=schemas.Application,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_SUPER_ADMIN, ROLE_ADMIN, ROLE_APPLICATION_SCREENER]
            )
        )
    ],
)
def update_application(
    app_id: int,
    app_in: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Update mutable fields on an application (status, answers_json, pet_id).

    Restricted to screeners and admins.
    """
    app = _get_application_for_org(db, user.org_id, app_id)
    for field, value in app_in.dict(exclude_unset=True).items():
        setattr(app, field, value)
    db.commit()
    db.refresh(app)
    return app


@router.get("/foster-matches")
def get_foster_matches(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Simple automated matching suggestions between pets needing foster
    and approved foster applications.

    The algorithm is intentionally lightweight:

    * Consider pets with status in ('intake', 'needs_foster').
    * Consider foster applications with status == 'approved' and type == 'foster'.
    * Prefer fosters who currently have fewer foster pets assigned.
    """
    # Pets that need foster homes
    pets = (
        db.query(models.Pet)
        .filter(
            models.Pet.org_id == user.org_id,
            models.Pet.status.in_(
                [schemas.PetStatus.intake, schemas.PetStatus.needs_foster]
            ),
        )
        .all()
    )

    # Approved foster applications
    foster_apps = (
        db.query(models.Application)
        .filter(
            models.Application.org_id == user.org_id,
            models.Application.type == schemas.ApplicationType.foster,
            models.Application.status == schemas.ApplicationStatus.approved,
        )
        .all()
    )
    if not pets or not foster_apps:
        return {"suggestions": [], "pets": [], "fosters": []}

    # Count current foster loads per user
    foster_loads = dict(
        db.query(models.Pet.foster_user_id, func.count(models.Pet.id))
        .filter(
            models.Pet.org_id == user.org_id,
            models.Pet.foster_user_id.isnot(None),
        )
        .group_by(models.Pet.foster_user_id)
        .all()
    )

    # Map applicant users
    applicant_user_ids = {app.applicant_user_id for app in foster_apps}
    users_by_id = {
        u.id: u
        for u in db.query(models.User)
        .filter(models.User.id.in_(applicant_user_ids))
        .all()
    }

    suggestions = []
    for pet in pets:
        # rank fosters by how many pets they already have
        ranked = sorted(
            foster_apps,
            key=lambda app: foster_loads.get(app.applicant_user_id, 0),
        )
        for app in ranked:
            foster = users_by_id.get(app.applicant_user_id)
            if not foster:
                continue
            suggestions.append(
                {
                    "pet_id": pet.id,
                    "pet_name": pet.name,
                    "pet_species": pet.species,
                    "foster_user_id": foster.id,
                    "foster_name": foster.full_name,
                    "current_foster_load": foster_loads.get(foster.id, 0),
                }
            )
            # Only suggest the top foster per pet for now
            break

    return {
        "pets": [
            {"id": p.id, "name": p.name, "status": p.status.value, "species": p.species}
            for p in pets
        ],
        "fosters": [
            {
                "application_id": app.id,
                "user_id": app.applicant_user_id,
                "status": app.status.value,
            }
            for app in foster_apps
        ],
        "suggestions": suggestions,
    }
