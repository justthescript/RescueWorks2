from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    ROLE_VETERINARIAN,
    require_any_role,
)

router = APIRouter(prefix="/vet", tags=["vet"])


@router.get("/pets", response_model=List[schemas.Pet])
def list_pets_for_vet(
    db: Session = Depends(get_db),
    user=Depends(require_any_role([ROLE_VETERINARIAN, ROLE_ADMIN, ROLE_SUPER_ADMIN])),
):
    pets = (
        db.query(models.Pet)
        .filter(models.Pet.org_id == user.org_id)
        .order_by(models.Pet.name)
        .all()
    )
    return pets


@router.get("/pets/{pet_id}/medical", response_model=List[schemas.MedicalRecord])
def get_pet_medical_records(
    pet_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_any_role([ROLE_VETERINARIAN, ROLE_ADMIN, ROLE_SUPER_ADMIN])),
):
    pet = (
        db.query(models.Pet)
        .filter(models.Pet.id == pet_id, models.Pet.org_id == user.org_id)
        .first()
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    records = (
        db.query(models.MedicalRecord)
        .filter(models.MedicalRecord.pet_id == pet.id)
        .order_by(models.MedicalRecord.created_at.desc())
        .all()
    )
    return records
