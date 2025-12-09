from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_db

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
