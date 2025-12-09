from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN,
    require_any_role,
)

router = APIRouter(prefix="/people", tags=["people"])


def _get_person_for_org(db: Session, org_id: int, person_id: int) -> models.Person:
    person = (
        db.query(models.Person)
        .filter(models.Person.id == person_id, models.Person.org_id == org_id)
        .first()
    )
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return person


@router.post(
    "/",
    response_model=schemas.Person,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def create_person(
    person_in: schemas.PersonCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new person in the current user's organization."""
    if person_in.org_id != user.org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User org mismatch",
        )

    person = models.Person(**person_in.dict())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/", response_model=List[schemas.Person])
def list_people(
    search: Optional[str] = Query(None, description="Search by name or email"),
    tag_filter: Optional[str] = Query(None, description="Filter by tag (e.g., 'adopter', 'foster', 'volunteer')"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return all people for the current organization with optional filters."""
    q = db.query(models.Person).filter(models.Person.org_id == user.org_id)

    # Search filter
    if search:
        search_term = f"%{search}%"
        q = q.filter(
            or_(
                models.Person.first_name.ilike(search_term),
                models.Person.last_name.ilike(search_term),
                models.Person.email.ilike(search_term),
                models.Person.phone.ilike(search_term),
            )
        )

    # Tag filter
    if tag_filter:
        tag_map = {
            "adopter": models.Person.tag_adopter,
            "potential_adopter": models.Person.tag_potential_adopter,
            "adopt_waitlist": models.Person.tag_adopt_waitlist,
            "do_not_adopt": models.Person.tag_do_not_adopt,
            "foster": models.Person.tag_foster,
            "available_foster": models.Person.tag_available_foster,
            "current_foster": models.Person.tag_current_foster,
            "dormant_foster": models.Person.tag_dormant_foster,
            "foster_waitlist": models.Person.tag_foster_waitlist,
            "do_not_foster": models.Person.tag_do_not_foster,
            "volunteer": models.Person.tag_volunteer,
            "do_not_volunteer": models.Person.tag_do_not_volunteer,
            "donor": models.Person.tag_donor,
            "board_member": models.Person.tag_board_member,
            "has_dogs": models.Person.tag_has_dogs,
            "has_cats": models.Person.tag_has_cats,
            "has_kids": models.Person.tag_has_kids,
            "processing_application": models.Person.tag_processing_application,
            "owner_surrender": models.Person.tag_owner_surrender,
        }
        if tag_filter in tag_map:
            q = q.filter(tag_map[tag_filter] == True)

    return q.order_by(models.Person.last_name, models.Person.first_name).all()


@router.get("/{person_id}", response_model=schemas.Person)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Return a single person by id for the current organization."""
    return _get_person_for_org(db, user.org_id, person_id)


@router.put(
    "/{person_id}",
    response_model=schemas.Person,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def update_person(
    person_id: int,
    person_in: schemas.PersonUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Update a person's information."""
    person = _get_person_for_org(db, user.org_id, person_id)
    update_data = person_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    db.commit()
    db.refresh(person)
    return person


@router.delete(
    "/{person_id}",
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Delete a person from the organization."""
    person = _get_person_for_org(db, user.org_id, person_id)
    db.delete(person)
    db.commit()
    return {"message": "Person deleted successfully"}


# Person notes endpoints
@router.post(
    "/{person_id}/notes",
    response_model=schemas.PersonNote,
    dependencies=[
        Depends(
            require_any_role(
                [ROLE_ADMIN, ROLE_SUPER_ADMIN]
            )
        )
    ],
)
def create_person_note(
    person_id: int,
    note_in: schemas.PersonNoteBase,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Add a note to a person's profile."""
    # Verify person exists and belongs to org
    person = _get_person_for_org(db, user.org_id, person_id)

    note = models.PersonNote(
        org_id=user.org_id,
        person_id=person_id,
        created_by_user_id=user.id,
        note_text=note_in.note_text,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{person_id}/notes", response_model=List[schemas.PersonNote])
def list_person_notes(
    person_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all notes for a person."""
    # Verify person exists and belongs to org
    person = _get_person_for_org(db, user.org_id, person_id)

    notes = (
        db.query(models.PersonNote)
        .filter(models.PersonNote.person_id == person_id)
        .filter(models.PersonNote.org_id == user.org_id)
        .order_by(models.PersonNote.created_at.desc())
        .all()
    )
    return notes


@router.get("/{person_id}/applications", response_model=List[schemas.Application])
def get_person_applications(
    person_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all applications for a person."""
    # Verify person exists and belongs to org
    person = _get_person_for_org(db, user.org_id, person_id)

    applications = (
        db.query(models.Application)
        .filter(models.Application.applicant_person_id == person_id)
        .filter(models.Application.org_id == user.org_id)
        .order_by(models.Application.created_at.desc())
        .all()
    )
    return applications


@router.get("/{person_id}/documents", response_model=List[schemas.Document])
def get_person_documents(
    person_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get all documents for a person."""
    # Verify person exists and belongs to org
    person = _get_person_for_org(db, user.org_id, person_id)

    documents = (
        db.query(models.Document)
        .filter(models.Document.person_id == person_id)
        .filter(models.Document.org_id == user.org_id)
        .order_by(models.Document.created_at.desc())
        .all()
    )
    return documents
