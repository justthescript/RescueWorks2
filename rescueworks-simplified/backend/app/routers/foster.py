from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime
from .. import models, schemas
from ..database import get_db
from ..security import get_current_active_user
from ..models import PetStatus, PlacementOutcome

router = APIRouter(prefix="/foster", tags=["Foster Management"])


# FOSTER PROFILES
@router.post("/profiles", response_model=schemas.FosterProfile)
def create_foster_profile(
    profile: schemas.FosterProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a foster profile for the current user"""
    # Check if profile already exists
    existing = db.query(models.FosterProfile).filter(
        models.FosterProfile.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Foster profile already exists")

    db_profile = models.FosterProfile(
        **profile.model_dump(),
        user_id=current_user.id,
        org_id=current_user.org_id
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/profiles", response_model=List[schemas.FosterProfile])
def list_foster_profiles(
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List all foster profiles in the organization"""
    query = db.query(models.FosterProfile).filter(
        models.FosterProfile.org_id == current_user.org_id
    )

    if available_only:
        query = query.filter(
            models.FosterProfile.is_available == True,
            models.FosterProfile.current_capacity < models.FosterProfile.max_capacity
        )

    return query.all()


@router.get("/profiles/me", response_model=schemas.FosterProfile)
def get_my_foster_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get the current user's foster profile"""
    profile = db.query(models.FosterProfile).filter(
        models.FosterProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    return profile


@router.patch("/profiles/me", response_model=schemas.FosterProfile)
def update_my_foster_profile(
    profile_update: schemas.FosterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update the current user's foster profile"""
    profile = db.query(models.FosterProfile).filter(
        models.FosterProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


# MATCHING ALGORITHM
@router.get("/matches", response_model=List[schemas.FosterMatch])
def get_suggested_matches(
    animal_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get suggested foster matches using the matching algorithm"""
    # Get animals that need foster care
    animals_query = db.query(models.Animal).filter(
        models.Animal.org_id == current_user.org_id,
        models.Animal.status.in_([PetStatus.intake, PetStatus.needs_foster])
    )

    if animal_id:
        animals_query = animals_query.filter(models.Animal.id == animal_id)

    animals = animals_query.all()

    # Get available foster profiles
    fosters = db.query(models.FosterProfile).join(models.User).filter(
        models.FosterProfile.org_id == current_user.org_id,
        models.FosterProfile.is_available == True,
        models.FosterProfile.current_capacity < models.FosterProfile.max_capacity
    ).all()

    matches = []

    for animal in animals:
        for foster in fosters:
            score = 0
            reasons = []

            # Availability & Capacity (20 points)
            if foster.current_capacity < foster.max_capacity:
                score += 20
                reasons.append("Has available capacity")

            # Species preference (30 points)
            if foster.preferred_species and animal.species.lower() in foster.preferred_species.lower():
                score += 30
                reasons.append("Species preference match")

            # Medical needs (25 points)
            if animal.medical_notes and foster.can_handle_medical:
                score += 25
                reasons.append("Can handle medical needs")

            # Behavioral needs (25 points)
            if animal.behavioral_notes and foster.can_handle_behavioral:
                score += 25
                reasons.append("Can handle behavioral needs")

            # Experience level (15 points)
            if foster.experience_level == "advanced":
                score += 15
                reasons.append("Advanced experience level")
            elif foster.experience_level == "intermediate":
                score += 10
                reasons.append("Intermediate experience level")

            # Track record (20 points)
            if foster.total_fosters > 0:
                success_rate = foster.successful_adoptions / foster.total_fosters
                if success_rate > 0.8:
                    score += 20
                    reasons.append("Excellent success rate")
                elif success_rate > 0.5:
                    score += 10
                    reasons.append("Good success rate")

            # Rating (15 points)
            if foster.rating and foster.rating >= 4.5:
                score += 15
                reasons.append("High rating (4.5+)")
            elif foster.rating and foster.rating >= 4.0:
                score += 10
                reasons.append("Good rating (4.0+)")

            # Workload balancing (15 points)
            if foster.current_capacity == 0:
                score += 15
                reasons.append("No current fosters")
            elif foster.current_capacity < foster.max_capacity / 2:
                score += 10
                reasons.append("Low current workload")

            if score >= 20:  # Minimum threshold
                match = schemas.FosterMatch(
                    animal_id=animal.id,
                    animal_name=animal.name,
                    foster_profile_id=foster.id,
                    foster_name=foster.user.full_name,
                    foster_email=foster.user.email,
                    score=score,
                    reasons=reasons
                )
                matches.append(match)

    # Sort by score descending
    matches.sort(key=lambda x: x.score, reverse=True)

    return matches


# FOSTER PLACEMENTS
@router.post("/placements", response_model=schemas.FosterPlacement)
def create_placement(
    placement: schemas.FosterPlacementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new foster placement"""
    # Verify foster profile exists and has capacity
    foster_profile = db.query(models.FosterProfile).filter(
        models.FosterProfile.id == placement.foster_profile_id,
        models.FosterProfile.org_id == current_user.org_id
    ).first()

    if not foster_profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    if foster_profile.current_capacity >= foster_profile.max_capacity:
        raise HTTPException(status_code=400, detail="Foster at maximum capacity")

    # Verify animal exists
    animal = db.query(models.Animal).filter(
        models.Animal.id == placement.animal_id,
        models.Animal.org_id == current_user.org_id
    ).first()

    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    # Create placement
    db_placement = models.FosterPlacement(
        **placement.model_dump(),
        org_id=current_user.org_id
    )
    db.add(db_placement)

    # Update animal status and foster assignment
    animal.status = PetStatus.in_foster
    animal.foster_user_id = foster_profile.user_id

    # Update foster profile capacity and stats
    foster_profile.current_capacity += 1
    foster_profile.total_fosters += 1

    db.commit()
    db.refresh(db_placement)
    return db_placement


@router.get("/placements", response_model=List[schemas.FosterPlacement])
def list_placements(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """List foster placements"""
    query = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == current_user.org_id
    )

    if active_only:
        query = query.filter(models.FosterPlacement.outcome == PlacementOutcome.active)

    return query.order_by(models.FosterPlacement.created_at.desc()).all()


@router.get("/placements/{placement_id}", response_model=schemas.FosterPlacement)
def get_placement(
    placement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific placement"""
    placement = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.id == placement_id,
        models.FosterPlacement.org_id == current_user.org_id
    ).first()

    if not placement:
        raise HTTPException(status_code=404, detail="Placement not found")

    return placement


@router.patch("/placements/{placement_id}", response_model=schemas.FosterPlacement)
def update_placement(
    placement_id: int,
    placement_update: schemas.FosterPlacementUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update a foster placement"""
    placement = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.id == placement_id,
        models.FosterPlacement.org_id == current_user.org_id
    ).first()

    if not placement:
        raise HTTPException(status_code=404, detail="Placement not found")

    update_data = placement_update.model_dump(exclude_unset=True)

    # Handle outcome changes
    if "outcome" in update_data and update_data["outcome"] != PlacementOutcome.active:
        placement.actual_end_date = datetime.utcnow()

        # Update animal status
        animal = placement.animal
        if update_data["outcome"] == PlacementOutcome.adopted:
            animal.status = PetStatus.adopted
            placement.foster_profile.successful_adoptions += 1
        else:
            animal.status = PetStatus.needs_foster

        animal.foster_user_id = None

        # Update foster capacity
        placement.foster_profile.current_capacity -= 1

    for field, value in update_data.items():
        setattr(placement, field, value)

    db.commit()
    db.refresh(placement)
    return placement


# DASHBOARD
@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get foster coordinator dashboard statistics"""
    org_id = current_user.org_id

    # Animal counts by status
    total_animals = db.query(models.Animal).filter(models.Animal.org_id == org_id).count()
    animals_in_intake = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.intake
    ).count()
    animals_needs_foster = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.needs_foster
    ).count()
    animals_in_foster = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.in_foster
    ).count()
    animals_available = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.available
    ).count()
    animals_adopted = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.adopted
    ).count()

    # Foster stats
    active_fosters = db.query(models.FosterProfile).filter(
        models.FosterProfile.org_id == org_id,
        models.FosterProfile.is_available == True
    ).count()

    # Available capacity
    available_capacity = db.query(
        func.sum(models.FosterProfile.max_capacity - models.FosterProfile.current_capacity)
    ).filter(
        models.FosterProfile.org_id == org_id,
        models.FosterProfile.is_available == True
    ).scalar() or 0

    # Recent intakes
    recent_intakes = db.query(models.Animal).filter(
        models.Animal.org_id == org_id,
        models.Animal.status == PetStatus.intake
    ).order_by(models.Animal.created_at.desc()).limit(5).all()

    # Recent placements
    recent_placements = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == org_id
    ).order_by(models.FosterPlacement.created_at.desc()).limit(5).all()

    return schemas.DashboardStats(
        total_animals=total_animals,
        animals_in_intake=animals_in_intake,
        animals_needs_foster=animals_needs_foster,
        animals_in_foster=animals_in_foster,
        animals_available=animals_available,
        animals_adopted=animals_adopted,
        active_fosters=active_fosters,
        available_foster_capacity=int(available_capacity),
        recent_intakes=recent_intakes,
        recent_placements=recent_placements
    )
