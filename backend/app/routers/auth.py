from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user
from ..security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.User)
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    org = (
        db.query(models.Organization)
        .filter(models.Organization.id == user_in.org_id)
        .first()
    )
    if not org:
        raise HTTPException(status_code=400, detail="Organization not found")
    user = models.User(
        org_id=user_in.org_id,
        email=user_in.email,
        full_name=user_in.full_name,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    access_token = create_access_token(
        subject=user.email, expires_delta=timedelta(minutes=60 * 24)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users", response_model=List[schemas.User])
def get_users(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all users in the current user's organization"""
    users = (
        db.query(models.User)
        .filter(models.User.org_id == current_user.org_id)
        .filter(models.User.is_active == True)
        .order_by(models.User.full_name)
        .all()
    )
    return users
