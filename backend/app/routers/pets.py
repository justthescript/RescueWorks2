from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_PET_COORDINATOR,
    ROLE_SUPER_ADMIN,
    require_any_role,
)

router = APIRouter(prefix="/pets", tags=["pets"])


def _get_pet_for_org(db: Session, org_id: int, pet_id: int) -> models.Pet:
    pet = (
        db.query(models.Pet)
        .filter(models.Pet.id == pet_id, models.Pet.org_id == org_id)
        .first()
    )
    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pet not found",
        )
    return pet


@router.post(
    "/",
    response_model=schemas.Pet,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_PET_COORDINATOR, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def create_pet(
    pet_in: schemas.PetCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new pet in the current user's organization."""
    # Auto-populate org_id from authenticated user if not provided
    if pet_in.org_id is None:
        pet_in.org_id = user.org_id
    elif pet_in.org_id != user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User org mismatch",
        )

    pet = models.Pet(**pet_in.dict())
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


@router.get("/", response_model=List[schemas.Pet])
def list_pets(
    status_filter: Optional[schemas.PetStatus] = None,
    species: Optional[str] = None,
    breed: Optional[str] = None,
    sex: Optional[str] = None,
    search: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    altered_status: Optional[str] = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return all pets for the current organization with advanced filtering."""
    q = db.query(models.Pet).filter(models.Pet.org_id == user.org_id)

    # Status filter
    if status_filter is not None:
        q = q.filter(models.Pet.status == status_filter)

    # Species filter
    if species:
        q = q.filter(models.Pet.species.ilike(f"%{species}%"))

    # Breed filter
    if breed:
        q = q.filter(models.Pet.breed.ilike(f"%{breed}%"))

    # Sex filter
    if sex:
        q = q.filter(models.Pet.sex == sex)

    # Altered status filter
    if altered_status:
        q = q.filter(models.Pet.altered_status == altered_status)

    # Search across name, species, breed
    if search:
        search_term = f"%{search}%"
        q = q.filter(
            (models.Pet.name.ilike(search_term)) |
            (models.Pet.species.ilike(search_term)) |
            (models.Pet.breed.ilike(search_term))
        )

    # Age filters (approximate calculation if date_of_birth exists)
    # Note: This is a simplified version. Production code would calculate age properly

    return q.order_by(models.Pet.created_at.desc()).all()


@router.get("/{pet_id}", response_model=schemas.Pet)
def get_pet(
    pet_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return a single pet by id for the current organization."""
    return _get_pet_for_org(db, user.org_id, pet_id)


@router.put(
    "/{pet_id}",
    response_model=schemas.Pet,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_PET_COORDINATOR, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def update_pet(
    pet_id: int,
    pet_in: schemas.PetUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a pet's core fields and status."""
    pet = _get_pet_for_org(db, user.org_id, pet_id)
    update_data = pet_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pet, field, value)
    db.commit()
    db.refresh(pet)
    return pet


@router.post(
    "/{pet_id}/assign-foster",
    response_model=schemas.Pet,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_PET_COORDINATOR, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def assign_foster(
    pet_id: int,
    foster_user_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Assign a foster to a pet.

    The foster must belong to the same organization.
    """
    pet = _get_pet_for_org(db, user.org_id, pet_id)

    foster = (
        db.query(models.User)
        .filter(models.User.id == foster_user_id, models.User.org_id == user.org_id)
        .first()
    )
    if not foster:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foster user not found",
        )

    if not foster.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot assign inactive user as foster",
        )

    pet.foster_user_id = foster.id
    # Move status to in_foster when appropriate
    if pet.status in [schemas.PetStatus.intake, schemas.PetStatus.needs_foster]:
        pet.status = schemas.PetStatus.in_foster

    db.commit()
    db.refresh(pet)
    return pet


@router.delete(
    "/{pet_id}/assign-foster",
    response_model=schemas.Pet,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_PET_COORDINATOR, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def unassign_foster(
    pet_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Remove a foster assignment from a pet and move it back to needs_foster when appropriate."""
    pet = _get_pet_for_org(db, user.org_id, pet_id)

    pet.foster_user_id = None
    if pet.status == schemas.PetStatus.in_foster:
        pet.status = schemas.PetStatus.needs_foster

    db.commit()
    db.refresh(pet)
    return pet
