from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user, oauth2_scheme
from ..security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from ..permissions import require_any_role, ROLE_ADMIN, ROLE_SUPER_ADMIN

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

    # Create refresh token
    refresh_token_str = create_refresh_token()
    refresh_token = models.RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token_str,
    }


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


@router.get("/roles", response_model=List[schemas.Role])
def get_roles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all available roles"""
    roles = db.query(models.Role).order_by(models.Role.name).all()
    return roles


@router.get("/me/roles", response_model=List[schemas.Role])
def get_current_user_roles(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get roles for the currently authenticated user"""
    roles = (
        db.query(models.Role)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .filter(models.UserRole.user_id == current_user.id)
        .all()
    )
    return roles


@router.get("/users/{user_id}/roles", response_model=List[schemas.Role])
def get_user_roles(
    user_id: int,
    current_user: models.User = Depends(require_any_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])),
    db: Session = Depends(get_db),
):
    """Get roles for a specific user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Cannot access users from other organizations")

    roles = (
        db.query(models.Role)
        .join(models.UserRole, models.UserRole.role_id == models.Role.id)
        .filter(models.UserRole.user_id == user_id)
        .all()
    )
    return roles


@router.post("/users/{user_id}/roles", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
def assign_role_to_user(
    user_id: int,
    role_assignment: schemas.UserRoleAssignment,
    current_user: models.User = Depends(require_any_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])),
    db: Session = Depends(get_db),
):
    """Assign a role to a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Cannot manage users from other organizations")

    role = db.query(models.Role).filter(models.Role.id == role_assignment.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    existing = (
        db.query(models.UserRole)
        .filter(models.UserRole.user_id == user_id)
        .filter(models.UserRole.role_id == role_assignment.role_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already has this role")

    user_role = models.UserRole(user_id=user_id, role_id=role_assignment.role_id)
    db.add(user_role)
    db.commit()

    return role


@router.delete("/users/{user_id}/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_role_from_user(
    user_id: int,
    role_id: int,
    current_user: models.User = Depends(require_any_role([ROLE_ADMIN, ROLE_SUPER_ADMIN])),
    db: Session = Depends(get_db),
):
    """Remove a role from a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.org_id != current_user.org_id:
        raise HTTPException(status_code=403, detail="Cannot manage users from other organizations")

    user_role = (
        db.query(models.UserRole)
        .filter(models.UserRole.user_id == user_id)
        .filter(models.UserRole.role_id == role_id)
        .first()
    )
    if not user_role:
        raise HTTPException(status_code=404, detail="User does not have this role")

    db.delete(user_role)
    db.commit()


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout by blacklisting the current access token"""
    try:
        payload = decode_token(token)
        exp = payload.get("exp")
        if exp:
            expires_at = datetime.fromtimestamp(exp)
        else:
            expires_at = datetime.utcnow() + timedelta(days=1)

        blacklist_entry = models.TokenBlacklist(
            token=token,
            expires_at=expires_at,
        )
        db.add(blacklist_entry)
        db.commit()

        return {"message": "Successfully logged out"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token",
        )


@router.post("/refresh")
def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db),
):
    """Exchange a refresh token for a new access token"""
    refresh_token_obj = (
        db.query(models.RefreshToken)
        .filter(models.RefreshToken.token == refresh_token)
        .first()
    )

    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if refresh_token_obj.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    if refresh_token_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired",
        )

    user = db.query(models.User).filter(models.User.id == refresh_token_obj.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    access_token = create_access_token(
        subject=user.email, expires_delta=timedelta(minutes=60 * 24)
    )

    return {"access_token": access_token, "token_type": "bearer"}
