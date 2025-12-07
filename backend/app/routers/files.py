import os
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db

UPLOAD_ROOT = os.environ.get("RESCUEWORKS_UPLOAD_ROOT", "./uploads")

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    pet_id: Optional[int] = Form(None),
    medical_record_id: Optional[int] = Form(None),
    event_id: Optional[int] = Form(None),
    task_id: Optional[int] = Form(None),
    visibility: str = Form("internal"),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """
    Upload a file and create a Document row.

    Files are written under UPLOAD_ROOT/<org_id>/ with a generated
    unique prefix to avoid collisions.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename",
        )

    # Map visibility string to enum, with validation
    try:
        visibility_enum = models.DocumentVisibility(visibility)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid visibility '{visibility}'",
        )

    org_id = user.org_id

    org_root = os.path.join(UPLOAD_ROOT, str(org_id))
    os.makedirs(org_root, exist_ok=True)

    # Generate a unique file name while preserving the original extension
    _, ext = os.path.splitext(file.filename)
    unique_name = f"{uuid4().hex}{ext or ''}"
    rel_path = os.path.join(str(org_id), unique_name)
    abs_path = os.path.join(UPLOAD_ROOT, rel_path)

    # Persist file contents
    contents = await file.read()
    try:
        with open(abs_path, "wb") as f:
            f.write(contents)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to save file: {exc}",
        )

    doc = models.Document(
        org_id=org_id,
        uploader_user_id=user.id,
        pet_id=pet_id,
        medical_record_id=medical_record_id,
        event_id=event_id,
        task_id=task_id,
        file_path=rel_path,
        file_type=file.content_type,
        visibility=visibility_enum,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
