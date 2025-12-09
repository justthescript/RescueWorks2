from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/messages", tags=["messaging"])


@router.post("/threads", response_model=schemas.MessageThread)
def create_thread(
    thread_in: schemas.MessageThreadCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.org_id != thread_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    thread = models.MessageThread(
        org_id=thread_in.org_id,
        subject=thread_in.subject,
        created_by_user_id=user.id,
        related_pet_id=thread_in.related_pet_id,
        related_application_id=thread_in.related_application_id,
        is_external=thread_in.is_external,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@router.get("/threads", response_model=List[schemas.MessageThread])
def list_threads(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(models.MessageThread)
        .filter(models.MessageThread.org_id == user.org_id)
        .all()
    )


@router.post("/threads/{thread_id}/messages", response_model=schemas.Message)
def post_message(
    thread_id: int,
    msg_in: schemas.MessageCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    thread = (
        db.query(models.MessageThread)
        .filter(
            models.MessageThread.id == thread_id,
            models.MessageThread.org_id == user.org_id,
        )
        .first()
    )
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    msg = models.Message(
        thread_id=thread_id,
        sender_user_id=user.id,
        body_text=msg_in.body_text,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@router.get("/threads/{thread_id}/messages", response_model=List[schemas.Message])
def list_messages(
    thread_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    thread = (
        db.query(models.MessageThread)
        .filter(
            models.MessageThread.id == thread_id,
            models.MessageThread.org_id == user.org_id,
        )
        .first()
    )
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return db.query(models.Message).filter(models.Message.thread_id == thread_id).all()
