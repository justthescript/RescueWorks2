from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from .. import models, schemas
from ..database import get_db
from ..security import get_current_active_user
from ..models import PetStatus

router = APIRouter(prefix="/operations", tags=["Operations"])


# CARE UPDATES
@router.post("/care-updates", response_model=schemas.CareUpdate)
def create_care_update(
    update: schemas.CareUpdateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a care update for an animal"""
    # Verify animal exists
    animal = db.query(models.Animal).filter(
        models.Animal.id == update.animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    db_update = models.CareUpdate(
        **update.model_dump(),
        org_id=current_user.org_id,
        created_by_user_id=current_user.id
    )
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update


@router.get("/care-updates", response_model=List[schemas.CareUpdate])
def list_care_updates(
    animal_id: Optional[int] = None,
    update_type: Optional[str] = None,
    important_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List care updates with optional filters"""
    query = db.query(models.CareUpdate).filter(
        models.CareUpdate.org_id == current_user.org_id
    )

    if animal_id:
        query = query.filter(models.CareUpdate.animal_id == animal_id)
    if update_type:
        query = query.filter(models.CareUpdate.update_type == update_type)
    if important_only:
        query = query.filter(models.CareUpdate.is_important == True)

    return query.order_by(models.CareUpdate.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/care-updates/{update_id}", response_model=schemas.CareUpdate)
def get_care_update(
    update_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific care update"""
    update = db.query(models.CareUpdate).filter(
        models.CareUpdate.id == update_id,
        models.CareUpdate.org_id == current_user.org_id
    ).first()

    if not update:
        raise HTTPException(status_code=404, detail="Care update not found")

    return update


# SEARCH AND FILTER
@router.get("/search/animals", response_model=List[schemas.Animal])
def search_animals(
    query: Optional[str] = None,
    status: Optional[PetStatus] = None,
    species: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    has_medical_needs: Optional[bool] = None,
    has_behavioral_needs: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Advanced search for animals with multiple filters"""
    db_query = db.query(models.Animal).filter(
        models.Animal.org_id == current_user.org_id
    )

    # Text search in name, breed, description
    if query:
        search_filter = f"%{query}%"
        db_query = db_query.filter(
            models.Animal.name.ilike(search_filter) |
            models.Animal.breed.ilike(search_filter) |
            models.Animal.description.ilike(search_filter)
        )

    if status:
        db_query = db_query.filter(models.Animal.status == status)

    if species:
        db_query = db_query.filter(models.Animal.species.ilike(f"%{species}%"))

    if min_age is not None:
        db_query = db_query.filter(models.Animal.age_years >= min_age)

    if max_age is not None:
        db_query = db_query.filter(models.Animal.age_years <= max_age)

    if has_medical_needs is not None:
        if has_medical_needs:
            db_query = db_query.filter(models.Animal.medical_notes.isnot(None))
        else:
            db_query = db_query.filter(models.Animal.medical_notes.is_(None))

    if has_behavioral_needs is not None:
        if has_behavioral_needs:
            db_query = db_query.filter(models.Animal.behavioral_notes.isnot(None))
        else:
            db_query = db_query.filter(models.Animal.behavioral_notes.is_(None))

    return db_query.offset(skip).limit(limit).all()


# REPORTS
@router.get("/reports/animals", response_model=schemas.AnimalReport)
def generate_animal_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Generate animal statistics report"""
    query = db.query(models.Animal).filter(
        models.Animal.org_id == current_user.org_id
    )

    # Date filtering
    if start_date:
        start = datetime.fromisoformat(start_date)
        query = query.filter(models.Animal.created_at >= start)
    if end_date:
        end = datetime.fromisoformat(end_date)
        query = query.filter(models.Animal.created_at <= end)

    animals = query.all()

    # Total count
    total_count = len(animals)

    # Group by status
    by_status = {}
    for status in PetStatus:
        count = sum(1 for a in animals if a.status == status)
        by_status[status.value] = count

    # Group by species
    by_species = {}
    for animal in animals:
        species = animal.species or "Unknown"
        by_species[species] = by_species.get(species, 0) + 1

    # Calculate average time metrics
    placements = db.query(models.FosterPlacement).join(models.Animal).filter(
        models.Animal.org_id == current_user.org_id
    ).all()

    # Average time to foster (from intake to first placement)
    avg_time_to_foster = None
    if placements:
        foster_times = []
        for placement in placements:
            if placement.animal.intake_date:
                days = (placement.start_date.date() - placement.animal.intake_date).days
                if days >= 0:
                    foster_times.append(days)
        if foster_times:
            avg_time_to_foster = sum(foster_times) / len(foster_times)

    # Average time to adoption
    avg_time_to_adoption = None
    adopted_animals = [a for a in animals if a.status == PetStatus.adopted]
    if adopted_animals:
        adoption_times = []
        for animal in adopted_animals:
            if animal.intake_date:
                # Find when they were adopted (last placement outcome)
                adoption_placement = db.query(models.FosterPlacement).filter(
                    models.FosterPlacement.animal_id == animal.id,
                    models.FosterPlacement.outcome == "adopted"
                ).first()
                if adoption_placement and adoption_placement.actual_end_date:
                    days = (adoption_placement.actual_end_date.date() - animal.intake_date).days
                    if days >= 0:
                        adoption_times.append(days)
        if adoption_times:
            avg_time_to_adoption = sum(adoption_times) / len(adoption_times)

    return schemas.AnimalReport(
        total_count=total_count,
        by_status=by_status,
        by_species=by_species,
        average_time_to_foster=avg_time_to_foster,
        average_time_to_adoption=avg_time_to_adoption
    )


@router.get("/reports/foster-performance")
def generate_foster_performance_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Generate foster performance report"""
    foster_profiles = db.query(models.FosterProfile).join(models.User).filter(
        models.FosterProfile.org_id == current_user.org_id
    ).all()

    report_data = []

    for profile in foster_profiles:
        success_rate = 0
        if profile.total_fosters > 0:
            success_rate = (profile.successful_adoptions / profile.total_fosters) * 100

        report_data.append({
            "foster_name": profile.user.full_name,
            "foster_email": profile.user.email,
            "total_fosters": profile.total_fosters,
            "successful_adoptions": profile.successful_adoptions,
            "success_rate": round(success_rate, 2),
            "current_capacity": profile.current_capacity,
            "max_capacity": profile.max_capacity,
            "rating": profile.rating,
            "experience_level": profile.experience_level.value,
            "is_available": profile.is_available
        })

    return {
        "total_fosters": len(foster_profiles),
        "active_fosters": sum(1 for p in foster_profiles if p.is_available),
        "total_placements": sum(p.total_fosters for p in foster_profiles),
        "total_adoptions": sum(p.successful_adoptions for p in foster_profiles),
        "foster_details": report_data
    }


@router.get("/reports/dashboard-summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get comprehensive dashboard summary for operations"""
    org_id = current_user.org_id

    # Get counts for last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)

    new_intakes = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.created_at >= thirty_days_ago
    ).count()

    new_placements = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == org_id,
        models.FosterPlacement.created_at >= thirty_days_ago
    ).count()

    new_adoptions = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == org_id,
        models.FosterPlacement.outcome == "adopted",
        models.FosterPlacement.updated_at >= thirty_days_ago
    ).count()

    active_placements = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == org_id,
        models.FosterPlacement.outcome == "active"
    ).count()

    animals_needing_foster = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status.in_([PetStatus.intake, PetStatus.needs_foster])
    ).count()

    return {
        "last_30_days": {
            "new_intakes": new_intakes,
            "new_placements": new_placements,
            "new_adoptions": new_adoptions
        },
        "current": {
            "active_placements": active_placements,
            "animals_needing_foster": animals_needing_foster
        }
    }
