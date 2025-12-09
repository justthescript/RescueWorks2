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

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=schemas.Payment)
def create_payment(
    pay_in: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role([ROLE_BILLING_MANAGER, ROLE_ADMIN, ROLE_SUPER_ADMIN])
    ),
):
    if user.org_id != pay_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    payment = models.Payment(
        org_id=pay_in.org_id,
        user_id=pay_in.user_id,
        pet_id=pay_in.pet_id,
        purpose=pay_in.purpose,
        amount=pay_in.amount,
        currency=pay_in.currency,
        provider=pay_in.provider,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=List[schemas.Payment])
def list_payments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Payment).filter(models.Payment.org_id == user.org_id).all()


@router.post("/coupons", response_model=schemas.Coupon)
def create_coupon(
    coupon_in: schemas.CouponCreate,
    db: Session = Depends(get_db),
    user=Depends(
        require_any_role([ROLE_BILLING_MANAGER, ROLE_ADMIN, ROLE_SUPER_ADMIN])
    ),
):
    if user.org_id != coupon_in.org_id:
        raise HTTPException(status_code=400, detail="User org mismatch")
    existing = (
        db.query(models.Coupon).filter(models.Coupon.code == coupon_in.code).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Code already exists")
    c = models.Coupon(
        org_id=coupon_in.org_id,
        code=coupon_in.code,
        description=coupon_in.description,
        discount_type=coupon_in.discount_type,
        discount_value=coupon_in.discount_value,
        valid_from=coupon_in.valid_from,
        valid_to=coupon_in.valid_to,
        max_uses=coupon_in.max_uses,
        applicable_purpose=coupon_in.applicable_purpose,
        is_active=coupon_in.is_active,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/coupons", response_model=List[schemas.Coupon])
def list_coupons(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(models.Coupon).filter(models.Coupon.org_id == user.org_id).all()
