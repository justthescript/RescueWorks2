from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db, get_current_user

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.post("/", response_model=schemas.Organization)
def create_org(org_in: schemas.OrganizationCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(models.Organization)
        .filter(models.Organization.name == org_in.name)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Organization name already exists")
    org = models.Organization(
        name=org_in.name,
        logo_url=org_in.logo_url,
        primary_contact_email=org_in.primary_contact_email,
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/", response_model=list[schemas.Organization])
def list_orgs(db: Session = Depends(get_db)):
    return db.query(models.Organization).all()


@router.get("/me", response_model=schemas.Organization)
def get_my_org(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's organization"""
    org = db.query(models.Organization).filter(models.Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/me", response_model=schemas.Organization)
def update_my_org(
    org_in: schemas.OrganizationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's organization"""
    org = db.query(models.Organization).filter(models.Organization.id == current_user.org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if name is being changed to one that already exists
    if org_in.name != org.name:
        existing = (
            db.query(models.Organization)
            .filter(models.Organization.name == org_in.name)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Organization name already exists")

    org.name = org_in.name
    org.logo_url = org_in.logo_url
    org.primary_contact_email = org_in.primary_contact_email
    db.commit()
    db.refresh(org)
    return org
