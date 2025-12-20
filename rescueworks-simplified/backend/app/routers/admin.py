from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from ..security import get_current_active_user, require_role, get_password_hash
from ..models import UserRole

router = APIRouter(prefix="/admin", tags=["Admin"])


# USER MANAGEMENT
@router.get("/users", response_model=List[schemas.User])
def list_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin, UserRole.coordinator]))
):
    """List all users in the organization (admin/coordinator only)"""
    users = db.query(models.User).filter(
        models.User.org_id == current_user.org_id
    ).all()
    return users


@router.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin, UserRole.coordinator]))
):
    """Get a specific user (admin/coordinator only)"""
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.org_id == current_user.org_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Update a user's role (admin only)"""
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.org_id == current_user.org_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    user.role = role
    db.commit()

    return {"message": f"User role updated to {role.value}"}


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Activate or deactivate a user (admin only)"""
    user = db.query(models.User).filter(
        models.User.id == user_id,
        models.User.org_id == current_user.org_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = is_active
    db.commit()

    return {"message": f"User {'activated' if is_active else 'deactivated'} successfully"}


# SYSTEM CONFIGURATION
@router.get("/config", response_model=List[schemas.SystemConfig])
def list_config_settings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """List all system configuration settings (admin only)"""
    configs = db.query(models.SystemConfig).filter(
        models.SystemConfig.org_id == current_user.org_id
    ).all()
    return configs


@router.get("/config/{key}", response_model=schemas.SystemConfig)
def get_config_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Get a specific configuration setting (admin only)"""
    config = db.query(models.SystemConfig).filter(
        models.SystemConfig.key == key,
        models.SystemConfig.org_id == current_user.org_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuration setting not found")

    return config


@router.post("/config", response_model=schemas.SystemConfig)
def create_config_setting(
    config: schemas.SystemConfigCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Create a new configuration setting (admin only)"""
    # Check if key already exists
    existing = db.query(models.SystemConfig).filter(
        models.SystemConfig.key == config.key
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Configuration key already exists")

    db_config = models.SystemConfig(
        **config.model_dump(),
        org_id=current_user.org_id
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config


@router.patch("/config/{key}", response_model=schemas.SystemConfig)
def update_config_setting(
    key: str,
    config_update: schemas.SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Update a configuration setting (admin only)"""
    config = db.query(models.SystemConfig).filter(
        models.SystemConfig.key == key,
        models.SystemConfig.org_id == current_user.org_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuration setting not found")

    update_data = config_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)
    return config


@router.delete("/config/{key}")
def delete_config_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Delete a configuration setting (admin only)"""
    config = db.query(models.SystemConfig).filter(
        models.SystemConfig.key == key,
        models.SystemConfig.org_id == current_user.org_id
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Configuration setting not found")

    db.delete(config)
    db.commit()

    return {"message": "Configuration setting deleted successfully"}


# ORGANIZATION MANAGEMENT
@router.get("/organization")
def get_organization_info(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get current organization information"""
    org = db.query(models.Organization).filter(
        models.Organization.id == current_user.org_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get stats
    total_users = db.query(models.User).filter(models.User.org_id == org.id).count()
    total_animals = db.query(models.Animal).filter(models.Animal.org_id == org.id).count()
    total_fosters = db.query(models.FosterProfile).filter(models.FosterProfile.org_id == org.id).count()

    return {
        "id": org.id,
        "name": org.name,
        "created_at": org.created_at,
        "stats": {
            "total_users": total_users,
            "total_animals": total_animals,
            "total_fosters": total_fosters
        }
    }


@router.patch("/organization/name")
def update_organization_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role([UserRole.admin]))
):
    """Update organization name (admin only)"""
    org = db.query(models.Organization).filter(
        models.Organization.id == current_user.org_id
    ).first()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.name = name
    db.commit()

    return {"message": "Organization name updated successfully", "name": name}
