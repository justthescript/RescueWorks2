from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/adoptable", response_model=List[schemas.Pet])
def list_adoptable_pets(org_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Pet)
        .filter(
            models.Pet.org_id == org_id,
            models.Pet.status.in_(
                [models.PetStatus.available, models.PetStatus.pending]
            ),
        )
        .all()
    )


@router.post("/adopt", response_model=schemas.Application)
def request_adoption(
    org_id: int, pet_id: int, email: str, full_name: str, db: Session = Depends(get_db)
):
    org = db.query(models.Organization).filter(models.Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=400, detail="Organization not found")
    # Find or create a bare user record for this email in the org
    user = (
        db.query(models.User)
        .filter(models.User.email == email, models.User.org_id == org_id)
        .first()
    )
    if not user:
        user = models.User(
            org_id=org_id,
            email=email,
            full_name=full_name,
            phone=None,
            hashed_password="",  # indicates portal setup needed
            is_active=True,
        )
        db.add(user)
        db.flush()
    app = models.Application(
        org_id=org_id,
        applicant_user_id=user.id,
        pet_id=pet_id,
        type=models.ApplicationType.adoption,
        status=models.ApplicationStatus.submitted,
        answers_json=None,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app
