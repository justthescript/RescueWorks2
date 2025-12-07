from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..deps import get_current_user, get_db
from ..permissions import (
    ROLE_ADMIN,
    ROLE_BILLING_MANAGER,
    ROLE_SUPER_ADMIN,
    require_any_role,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("/categories", response_model=schemas.ExpenseCategory)
def create_category(
    cat_in: schemas.ExpenseCategoryCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role([ROLE_BILLING_MANAGER, ROLE_ADMIN, ROLE_SUPER_ADMIN])
    ),
):
    if user.org_id != cat_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    cat = models.ExpenseCategory(
        org_id=cat_in.org_id,
        name=cat_in.name,
        description=cat_in.description,
        is_active=cat_in.is_active,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.get("/categories", response_model=List[schemas.ExpenseCategory])
def list_categories(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return (
        db.query(models.ExpenseCategory)
        .filter(models.ExpenseCategory.org_id == user.org_id)
        .all()
    )


@router.post("/", response_model=schemas.Expense)
def create_expense(
    exp_in: schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role([ROLE_BILLING_MANAGER, ROLE_ADMIN, ROLE_SUPER_ADMIN])
    ),
):
    if user.org_id != exp_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    cat = (
        db.query(models.ExpenseCategory)
        .filter(
            models.ExpenseCategory.id == exp_in.category_id,
            models.ExpenseCategory.org_id == user.org_id,
        )
        .first()
    )
    if not cat:
        raise HTTPException(status_code=400, detail="Category not found")
    exp = models.Expense(
        org_id=exp_in.org_id,
        category_id=exp_in.category_id,
        amount=exp_in.amount,
        currency=exp_in.currency,
        date_incurred=exp_in.date_incurred,
        description=exp_in.description,
        vendor_name=exp_in.vendor_name,
        recorded_by_user_id=user.id,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.get("/", response_model=List[schemas.Expense])
def list_expenses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Expense).filter(models.Expense.org_id == user.org_id).all()
