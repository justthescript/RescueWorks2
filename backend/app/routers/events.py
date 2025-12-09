from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_EVENT_COORDINATOR,
    ROLE_SUPER_ADMIN,
    require_any_role,
)

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=schemas.Event)
def create_event(
    event_in: schemas.EventCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role([ROLE_EVENT_COORDINATOR, ROLE_ADMIN, ROLE_SUPER_ADMIN])
    ),
):
    if user.org_id != event_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    ev = models.Event(
        org_id=event_in.org_id,
        name=event_in.name,
        description=event_in.description,
        start_datetime=event_in.start_datetime,
        end_datetime=event_in.end_datetime,
        location_name=event_in.location_name,
        location_address=event_in.location_address,
        capacity=event_in.capacity,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/", response_model=List[schemas.Event])
def list_events(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Event).filter(models.Event.org_id == user.org_id).all()
