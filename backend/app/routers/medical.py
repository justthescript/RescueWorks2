from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_PET_COORDINATOR,
    ROLE_SUPER_ADMIN,
    ROLE_VETERINARIAN,
    require_any_role,
)

router = APIRouter(prefix="/medical", tags=["medical"])


@router.post("/records", response_model=schemas.MedicalRecord)
def create_medical_record(
    record_in: schemas.MedicalRecordCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role(
            [ROLE_VETERINARIAN, ROLE_PET_COORDINATOR, ROLE_ADMIN, ROLE_SUPER_ADMIN]
        )
    ),
):
    if user.org_id != record_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    pet = (
        db.query(models.Pet)
        .filter(models.Pet.id == record_in.pet_id, models.Pet.org_id == user.org_id)
        .first()
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    rec = models.MedicalRecord(
        org_id=record_in.org_id,
        pet_id=record_in.pet_id,
        created_by_user_id=user.id,
        record_type=record_in.record_type,
        notes=record_in.notes,
        visibility=record_in.visibility,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/records/{pet_id}", response_model=List[schemas.MedicalRecord])
def list_medical_records(
    pet_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return (
        db.query(models.MedicalRecord)
        .filter(
            models.MedicalRecord.pet_id == pet_id,
            models.MedicalRecord.org_id == user.org_id,
        )
        .all()
    )


@router.post("/appointments", response_model=schemas.Appointment)
def create_appointment(
    appt_in: schemas.AppointmentCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role(
            [ROLE_VETERINARIAN, ROLE_PET_COORDINATOR, ROLE_ADMIN, ROLE_SUPER_ADMIN]
        )
    ),
):
    if user.org_id != appt_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    appt = models.Appointment(
        org_id=appt_in.org_id,
        pet_id=appt_in.pet_id,
        type=appt_in.type,
        date_time=appt_in.date_time,
        location=appt_in.location,
        notes=appt_in.notes,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("/appointments", response_model=List[schemas.Appointment])
def list_appointments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.org_id == user.org_id)
        .all()
    )
