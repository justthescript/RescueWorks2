from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..security import get_current_active_user, require_role
from ..models import UserRole

router = APIRouter(prefix="/animals", tags=["Animals"])


@router.post("/", response_model=schemas.Animal)
def create_animal(
    animal: schemas.AnimalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new animal intake record"""
    db_animal = models.Animal(
        **animal.model_dump(),
        org_id=current_user.org_id
    )
    db.add(db_animal)
    db.commit()
    db.refresh(db_animal)
    return db_animal


@router.post("/{animal_id}/upload-photo")
async def upload_animal_photo(
    animal_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Upload a photo for an animal"""
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    # Create uploads directory if it doesn't exist
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    filename = f"animal_{animal_id}_{datetime.now().timestamp()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update animal photo_url
    animal.photo_url = f"/uploads/{filename}"
    db.commit()

    return {"photo_url": animal.photo_url}


@router.get("/", response_model=List[schemas.Animal])
def list_animals(
    status: Optional[str] = None,
    species: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all animals with optional filters"""
    query = db.query(models.Animal).filter(models.Animal.org_id == current_user.org_id)

    if status:
        query = query.filter(models.Animal.status == status)
    if species:
        query = query.filter(models.Animal.species.ilike(f"%{species}%"))

    animals = query.offset(skip).limit(limit).all()
    return animals


@router.get("/{animal_id}", response_model=schemas.Animal)
def get_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific animal by ID"""
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    return animal


@router.patch("/{animal_id}", response_model=schemas.Animal)
def update_animal(
    animal_id: int,
    animal_update: schemas.AnimalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update an animal record"""
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    update_data = animal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(animal, field, value)

    db.commit()
    db.refresh(animal)
    return animal


@router.delete("/{animal_id}")
def delete_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin, UserRole.coordinator]))
):
    """Delete an animal record (admin only)"""
    animal = db.query(models.Animal).filter(
        models.Animal.id == animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    db.delete(animal)
    db.commit()
    return {"message": "Animal deleted successfully"}
