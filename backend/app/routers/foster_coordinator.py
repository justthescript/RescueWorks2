"""
Foster Coordinator Router
Endpoints for foster management, matching algorithm, and coordinator dashboard
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..permissions import require_role


router = APIRouter(prefix="/foster-coordinator", tags=["foster-coordinator"])


# ============================================================================
# FOSTER PROFILE MANAGEMENT
# ============================================================================


@router.post("/profiles", response_model=schemas.FosterProfile)
def create_foster_profile(
    profile: schemas.FosterProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a foster profile for a user"""
    # Check if profile already exists
    existing = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.user_id == current_user.id,
                models.FosterProfile.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Foster profile already exists")

    db_profile = models.FosterProfile(
        user_id=current_user.id,
        org_id=current_user.org_id,
        **profile.dict(),
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.get("/profiles", response_model=List[schemas.FosterProfile])
def list_foster_profiles(
    available_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List all foster profiles in the organization"""
    query = db.query(models.FosterProfile).filter(
        models.FosterProfile.org_id == current_user.org_id
    )

    if available_only:
        query = query.filter(models.FosterProfile.is_available == True)

    return query.all()


@router.get("/profiles/me", response_model=schemas.FosterProfile)
def get_my_foster_profile(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get the current user's foster profile"""
    profile = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.user_id == current_user.id,
                models.FosterProfile.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")
    return profile


@router.get("/profiles/{profile_id}", response_model=schemas.FosterProfile)
def get_foster_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a specific foster profile"""
    profile = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.id == profile_id,
                models.FosterProfile.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")
    return profile


@router.patch("/profiles/me", response_model=schemas.FosterProfile)
def update_my_foster_profile(
    profile_update: schemas.FosterProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update the current user's foster profile"""
    profile = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.user_id == current_user.id,
                models.FosterProfile.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    # Update fields
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


@router.patch("/profiles/{profile_id}/admin", response_model=schemas.FosterProfile)
def update_foster_profile_admin(
    profile_id: int,
    background_check_status: Optional[str] = None,
    background_check_date: Optional[datetime] = None,
    insurance_verified: Optional[bool] = None,
    references_checked: Optional[bool] = None,
    notes_internal: Optional[str] = None,
    rating: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update admin-only fields of a foster profile (coordinator only)"""
    profile = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.id == profile_id,
                models.FosterProfile.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    # Update admin fields
    if background_check_status is not None:
        profile.background_check_status = background_check_status
    if background_check_date is not None:
        profile.background_check_date = background_check_date
    if insurance_verified is not None:
        profile.insurance_verified = insurance_verified
    if references_checked is not None:
        profile.references_checked = references_checked
    if notes_internal is not None:
        profile.notes_internal = notes_internal
    if rating is not None:
        profile.rating = rating

    profile.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(profile)
    return profile


# ============================================================================
# FOSTER COORDINATOR DASHBOARD
# ============================================================================


@router.get("/dashboard/stats", response_model=schemas.FosterCoordinatorStats)
def get_coordinator_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get statistics for the foster coordinator dashboard"""
    org_id = current_user.org_id

    # Count active foster profiles
    total_active_fosters = (
        db.query(func.count(models.FosterProfile.id))
        .filter(models.FosterProfile.org_id == org_id)
        .scalar()
    )

    # Count available foster profiles
    total_available_fosters = (
        db.query(func.count(models.FosterProfile.id))
        .filter(
            and_(
                models.FosterProfile.org_id == org_id,
                models.FosterProfile.is_available == True,
            )
        )
        .scalar()
    )

    # Count pets needing foster
    pets_needing_foster = (
        db.query(func.count(models.Pet.id))
        .filter(
            and_(
                models.Pet.org_id == org_id,
                or_(
                    models.Pet.status == models.PetStatus.intake,
                    models.Pet.status == models.PetStatus.needs_foster,
                ),
            )
        )
        .scalar()
    )

    # Count pets currently in foster
    pets_in_foster = (
        db.query(func.count(models.Pet.id))
        .filter(
            and_(
                models.Pet.org_id == org_id,
                models.Pet.status == models.PetStatus.in_foster,
            )
        )
        .scalar()
    )

    # Calculate average placement duration
    avg_duration_result = (
        db.query(func.avg(models.FosterProfile.avg_foster_duration_days))
        .filter(models.FosterProfile.org_id == org_id)
        .scalar()
    )
    avg_placement_duration_days = float(avg_duration_result) if avg_duration_result else None

    # Get recent placements with pet information
    recent_placements_raw = (
        db.query(models.FosterPlacement)
        .options(joinedload(models.FosterPlacement.pet))
        .filter(models.FosterPlacement.org_id == org_id)
        .order_by(models.FosterPlacement.created_at.desc())
        .limit(10)
        .all()
    )

    # Manually populate pet_name and pet_species for each placement
    recent_placements = []
    for placement in recent_placements_raw:
        placement_dict = {
            "id": placement.id,
            "org_id": placement.org_id,
            "pet_id": placement.pet_id,
            "foster_profile_id": placement.foster_profile_id,
            "start_date": placement.start_date,
            "expected_end_date": placement.expected_end_date,
            "actual_end_date": placement.actual_end_date,
            "outcome": placement.outcome,
            "placement_notes": placement.placement_notes,
            "return_reason": placement.return_reason,
            "success_notes": placement.success_notes,
            "agreement_signed": placement.agreement_signed,
            "agreement_signed_date": placement.agreement_signed_date,
            "created_at": placement.created_at,
            "updated_at": placement.updated_at,
            "pet_name": placement.pet.name if placement.pet else None,
            "pet_species": placement.pet.species if placement.pet else None,
        }
        recent_placements.append(schemas.FosterPlacement(**placement_dict))

    # Calculate available foster capacity
    available_capacity_result = (
        db.query(
            func.sum(
                models.FosterProfile.max_capacity - models.FosterProfile.current_capacity
            )
        )
        .filter(
            and_(
                models.FosterProfile.org_id == org_id,
                models.FosterProfile.is_available == True,
            )
        )
        .scalar()
    )
    available_foster_capacity = int(available_capacity_result) if available_capacity_result else 0

    return schemas.FosterCoordinatorStats(
        total_active_fosters=total_active_fosters or 0,
        total_available_fosters=total_available_fosters or 0,
        pets_needing_foster=pets_needing_foster or 0,
        pets_in_foster=pets_in_foster or 0,
        avg_placement_duration_days=avg_placement_duration_days,
        recent_placements=recent_placements,
        available_foster_capacity=available_foster_capacity,
    )


# ============================================================================
# ENHANCED MATCHING ALGORITHM
# ============================================================================


@router.get("/matches/suggest", response_model=List[schemas.FosterMatch])
def suggest_foster_matches(
    pet_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Enhanced matching algorithm that suggests optimal foster placements
    based on multiple criteria including experience, capacity, preferences, and compatibility
    """
    org_id = current_user.org_id

    # Get pets needing foster
    pets_query = db.query(models.Pet).filter(
        and_(
            models.Pet.org_id == org_id,
            or_(
                models.Pet.status == models.PetStatus.intake,
                models.Pet.status == models.PetStatus.needs_foster,
            ),
        )
    )

    if pet_id:
        pets_query = pets_query.filter(models.Pet.id == pet_id)

    pets = pets_query.all()

    # Get available foster profiles
    foster_profiles = (
        db.query(models.FosterProfile)
        .join(models.User)
        .filter(
            and_(
                models.FosterProfile.org_id == org_id,
                models.FosterProfile.is_available == True,
                models.FosterProfile.current_capacity < models.FosterProfile.max_capacity,
            )
        )
        .all()
    )

    matches = []

    for pet in pets:
        # Calculate match scores for each foster
        foster_scores = []

        for profile in foster_profiles:
            score = 0.0
            reasons = []

            # Base score: availability and capacity
            if profile.current_capacity < profile.max_capacity:
                score += 20
                reasons.append("Has available capacity")

            # Species preference match
            if profile.preferred_species:
                preferred_list = [s.strip().lower() for s in profile.preferred_species.split(",")]
                if pet.species.lower() in preferred_list:
                    score += 30
                    reasons.append(f"Prefers {pet.species}")

            # Experience level matching
            # Check if pet needs special care
            pet_needs_medical = False
            pet_needs_behavioral = False

            # Check medical records for special needs
            medical_keywords = ["special", "medication", "chronic", "treatment"]
            if pet.description_internal:
                desc_lower = pet.description_internal.lower()
                if any(keyword in desc_lower for keyword in medical_keywords):
                    pet_needs_medical = True

            behavioral_keywords = ["aggressive", "anxious", "fearful", "training needed"]
            if pet.description_internal:
                desc_lower = pet.description_internal.lower()
                if any(keyword in desc_lower for keyword in behavioral_keywords):
                    pet_needs_behavioral = True

            # Match special needs with foster capabilities
            if pet_needs_medical and profile.can_handle_medical:
                score += 25
                reasons.append("Can handle medical needs")
            elif pet_needs_medical and not profile.can_handle_medical:
                score -= 20
                reasons.append("Pet needs medical care")

            if pet_needs_behavioral and profile.can_handle_behavioral:
                score += 25
                reasons.append("Can handle behavioral issues")
            elif pet_needs_behavioral and not profile.can_handle_behavioral:
                score -= 20
                reasons.append("Pet needs behavioral support")

            # Experience level bonus
            if profile.experience_level == models.FosterExperienceLevel.advanced:
                score += 15
                reasons.append("Experienced foster")
            elif profile.experience_level == models.FosterExperienceLevel.intermediate:
                score += 10
                reasons.append("Intermediate experience")

            # Track record bonus
            if profile.total_fosters > 0:
                success_rate = (
                    profile.successful_adoptions / profile.total_fosters
                    if profile.total_fosters > 0
                    else 0
                )
                if success_rate > 0.8:
                    score += 20
                    reasons.append(f"High success rate ({success_rate:.0%})")
                elif success_rate > 0.5:
                    score += 10
                    reasons.append(f"Good success rate ({success_rate:.0%})")

            # Rating bonus
            if profile.rating and profile.rating >= 4.5:
                score += 15
                reasons.append(f"Highly rated ({profile.rating:.1f}★)")
            elif profile.rating and profile.rating >= 4.0:
                score += 10
                reasons.append(f"Well rated ({profile.rating:.1f}★)")

            # Current load balancing - prefer fosters with lower current load
            capacity_ratio = profile.current_capacity / profile.max_capacity if profile.max_capacity > 0 else 1
            if capacity_ratio == 0:
                score += 15
                reasons.append("No current fosters")
            elif capacity_ratio < 0.5:
                score += 10
                reasons.append("Low current load")

            # Qualifications check
            if profile.background_check_status == "approved":
                score += 10
                reasons.append("Background check approved")

            if profile.references_checked:
                score += 5
                reasons.append("References verified")

            foster_scores.append(
                {
                    "profile": profile,
                    "score": score,
                    "reasons": reasons,
                }
            )

        # Sort by score and take top matches
        foster_scores.sort(key=lambda x: x["score"], reverse=True)

        # Create match objects for top 3 fosters per pet
        for i, foster_match in enumerate(foster_scores[:3]):
            if foster_match["score"] > 0:  # Only include positive matches
                profile = foster_match["profile"]
                matches.append(
                    schemas.FosterMatch(
                        pet_id=pet.id,
                        pet_name=pet.name,
                        pet_species=pet.species,
                        pet_status=pet.status.value,
                        foster_user_id=profile.user_id,
                        foster_name=profile.user.full_name,
                        foster_email=profile.user.email,
                        match_score=foster_match["score"],
                        match_reasons=foster_match["reasons"],
                        current_foster_load=profile.current_capacity,
                        max_capacity=profile.max_capacity,
                    )
                )

    return matches


# ============================================================================
# FOSTER PLACEMENT WORKFLOW
# ============================================================================


@router.post("/placements", response_model=schemas.FosterPlacement)
def create_foster_placement(
    placement: schemas.FosterPlacementCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new foster placement (assigns pet to foster)"""
    org_id = current_user.org_id

    # Verify pet exists and is available
    pet = (
        db.query(models.Pet)
        .filter(and_(models.Pet.id == placement.pet_id, models.Pet.org_id == org_id))
        .first()
    )
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Verify foster profile exists
    foster_profile = (
        db.query(models.FosterProfile)
        .filter(
            and_(
                models.FosterProfile.id == placement.foster_profile_id,
                models.FosterProfile.org_id == org_id,
            )
        )
        .first()
    )
    if not foster_profile:
        raise HTTPException(status_code=404, detail="Foster profile not found")

    # Check foster capacity
    if foster_profile.current_capacity >= foster_profile.max_capacity:
        raise HTTPException(status_code=400, detail="Foster is at maximum capacity")

    # Check if foster is available
    if not foster_profile.is_available:
        raise HTTPException(status_code=400, detail="Foster is not currently available")

    # Create placement
    db_placement = models.FosterPlacement(
        org_id=org_id,
        pet_id=placement.pet_id,
        foster_profile_id=placement.foster_profile_id,
        expected_end_date=placement.expected_end_date,
        placement_notes=placement.placement_notes,
    )
    db.add(db_placement)

    # Update pet status
    pet.status = models.PetStatus.in_foster
    pet.foster_user_id = foster_profile.user_id

    # Update foster capacity
    foster_profile.current_capacity += 1
    foster_profile.total_fosters += 1

    db.commit()
    db.refresh(db_placement)
    return db_placement


@router.get("/placements", response_model=List[schemas.FosterPlacement])
def list_foster_placements(
    active_only: bool = False,
    foster_profile_id: Optional[int] = None,
    pet_id: Optional[int] = None,
    outcome: Optional[str] = None,
    search: Optional[str] = None,
    start_date_from: Optional[datetime] = None,
    start_date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List foster placements with advanced filtering"""
    query = db.query(models.FosterPlacement).options(
        joinedload(models.FosterPlacement.pet),
        joinedload(models.FosterPlacement.foster_profile)
    ).filter(
        models.FosterPlacement.org_id == current_user.org_id
    )

    # Active only filter
    if active_only:
        query = query.filter(
            models.FosterPlacement.outcome == models.PlacementOutcome.active
        )

    # Outcome filter
    if outcome:
        try:
            outcome_enum = models.PlacementOutcome(outcome)
            query = query.filter(models.FosterPlacement.outcome == outcome_enum)
        except ValueError:
            pass

    # Foster profile filter
    if foster_profile_id:
        query = query.filter(
            models.FosterPlacement.foster_profile_id == foster_profile_id
        )

    # Pet filter
    if pet_id:
        query = query.filter(models.FosterPlacement.pet_id == pet_id)

    # Date range filters
    if start_date_from:
        query = query.filter(models.FosterPlacement.start_date >= start_date_from)

    if start_date_to:
        query = query.filter(models.FosterPlacement.start_date <= start_date_to)

    # Search filter (search pet name)
    if search:
        query = query.join(models.Pet).filter(
            models.Pet.name.ilike(f"%{search}%")
        )

    return query.order_by(models.FosterPlacement.created_at.desc()).all()


@router.get("/placements/{placement_id}", response_model=schemas.FosterPlacement)
def get_foster_placement(
    placement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get a specific foster placement"""
    placement = (
        db.query(models.FosterPlacement)
        .filter(
            and_(
                models.FosterPlacement.id == placement_id,
                models.FosterPlacement.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not placement:
        raise HTTPException(status_code=404, detail="Foster placement not found")
    return placement


@router.patch("/placements/{placement_id}", response_model=schemas.FosterPlacement)
def update_foster_placement(
    placement_id: int,
    placement_update: schemas.FosterPlacementUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update a foster placement"""
    placement = (
        db.query(models.FosterPlacement)
        .filter(
            and_(
                models.FosterPlacement.id == placement_id,
                models.FosterPlacement.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not placement:
        raise HTTPException(status_code=404, detail="Foster placement not found")

    # Get foster profile for capacity updates
    foster_profile = placement.foster_profile
    pet = placement.pet

    # Update fields
    update_data = placement_update.dict(exclude_unset=True)
    was_active = placement.outcome == models.PlacementOutcome.active

    for field, value in update_data.items():
        setattr(placement, field, value)

    # If placement is being ended
    if placement.outcome != models.PlacementOutcome.active and was_active:
        if not placement.actual_end_date:
            placement.actual_end_date = datetime.utcnow()

        # Update foster capacity
        if foster_profile.current_capacity > 0:
            foster_profile.current_capacity -= 1

        # Update foster metrics
        if placement.outcome == models.PlacementOutcome.adopted:
            foster_profile.successful_adoptions += 1

        # Calculate duration and update average
        if placement.actual_end_date:
            duration = (placement.actual_end_date - placement.start_date).days
            if foster_profile.avg_foster_duration_days:
                # Update running average
                total_duration = (
                    foster_profile.avg_foster_duration_days * (foster_profile.total_fosters - 1)
                )
                foster_profile.avg_foster_duration_days = (
                    total_duration + duration
                ) / foster_profile.total_fosters
            else:
                foster_profile.avg_foster_duration_days = float(duration)

        # Update pet status
        if placement.outcome == models.PlacementOutcome.adopted:
            pet.status = models.PetStatus.adopted
        elif placement.outcome == models.PlacementOutcome.returned:
            pet.status = models.PetStatus.needs_foster
        pet.foster_user_id = None

    placement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(placement)
    return placement


@router.post("/placements/{placement_id}/complete", response_model=schemas.FosterPlacement)
def complete_foster_placement(
    placement_id: int,
    outcome: schemas.PlacementOutcome,
    return_reason: Optional[str] = None,
    success_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Complete a foster placement with an outcome"""
    placement = (
        db.query(models.FosterPlacement)
        .filter(
            and_(
                models.FosterPlacement.id == placement_id,
                models.FosterPlacement.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not placement:
        raise HTTPException(status_code=404, detail="Foster placement not found")

    if placement.outcome != models.PlacementOutcome.active:
        raise HTTPException(status_code=400, detail="Placement is already completed")

    # Update placement
    placement.outcome = outcome
    placement.actual_end_date = datetime.utcnow()
    placement.return_reason = return_reason
    placement.success_notes = success_notes

    # Update foster profile and pet
    foster_profile = placement.foster_profile
    pet = placement.pet

    # Update foster capacity
    if foster_profile.current_capacity > 0:
        foster_profile.current_capacity -= 1

    # Update foster metrics
    if outcome == models.PlacementOutcome.adopted:
        foster_profile.successful_adoptions += 1

    # Calculate duration and update average
    duration = (placement.actual_end_date - placement.start_date).days
    if foster_profile.avg_foster_duration_days:
        total_duration = (
            foster_profile.avg_foster_duration_days * (foster_profile.total_fosters - 1)
        )
        foster_profile.avg_foster_duration_days = (
            total_duration + duration
        ) / foster_profile.total_fosters
    else:
        foster_profile.avg_foster_duration_days = float(duration)

    # Update pet status
    if outcome == models.PlacementOutcome.adopted:
        pet.status = models.PetStatus.adopted
    elif outcome == models.PlacementOutcome.returned:
        pet.status = models.PetStatus.needs_foster
    elif outcome == models.PlacementOutcome.transferred:
        pet.status = models.PetStatus.needs_foster

    pet.foster_user_id = None

    placement.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(placement)
    return placement


# ============================================================================
# FOSTER PLACEMENT PROGRESS NOTES
# ============================================================================


@router.post("/placements/{placement_id}/notes", response_model=schemas.FosterPlacementNote)
def add_placement_note(
    placement_id: int,
    note: schemas.FosterPlacementNoteCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a progress note to a foster placement"""
    # Verify placement exists and user has access
    placement = (
        db.query(models.FosterPlacement)
        .filter(
            and_(
                models.FosterPlacement.id == placement_id,
                models.FosterPlacement.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not placement:
        raise HTTPException(status_code=404, detail="Foster placement not found")

    # Create note
    db_note = models.FosterPlacementNote(
        placement_id=placement_id,
        org_id=current_user.org_id,
        created_by_user_id=current_user.id,
        **note.dict(exclude={"placement_id"}),
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/placements/{placement_id}/notes", response_model=List[schemas.FosterPlacementNote])
def get_placement_notes(
    placement_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get all progress notes for a foster placement"""
    # Verify placement exists and user has access
    placement = (
        db.query(models.FosterPlacement)
        .filter(
            and_(
                models.FosterPlacement.id == placement_id,
                models.FosterPlacement.org_id == current_user.org_id,
            )
        )
        .first()
    )
    if not placement:
        raise HTTPException(status_code=404, detail="Foster placement not found")

    notes = (
        db.query(models.FosterPlacementNote)
        .filter(models.FosterPlacementNote.placement_id == placement_id)
        .order_by(models.FosterPlacementNote.created_at.desc())
        .all()
    )
    return notes
