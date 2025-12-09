from typing import Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/adoptions_by_month")
def adoptions_by_month(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> List[Dict]:
    rows = (
        db.query(
            func.strftime("%Y-%m", models.Application.created_at).label("month"),
            func.count(models.Application.id),
        )
        .filter(
            models.Application.org_id == user.org_id,
            models.Application.type == models.ApplicationType.adoption,
            models.Application.status == models.ApplicationStatus.approved,
        )
        .group_by("month")
        .order_by("month")
        .all()
    )
    return [{"month": m, "count": c} for m, c in rows]


@router.get("/donations_summary")
def donations_summary(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> Dict:
    total = (
        db.query(func.coalesce(func.sum(models.Payment.amount), 0.0))
        .filter(
            models.Payment.org_id == user.org_id,
            models.Payment.status == models.PaymentStatus.completed,
        )
        .scalar()
    )
    return {"total_donations": float(total or 0.0)}


@router.get("/pets_by_status")
def pets_by_status(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> List[Dict]:
    rows = (
        db.query(models.Pet.status, func.count(models.Pet.id))
        .filter(models.Pet.org_id == user.org_id)
        .group_by(models.Pet.status)
        .all()
    )
    out: List[Dict] = []
    for status, count in rows:
        status_value = status.value if hasattr(status, "value") else str(status)
        out.append({"status": status_value, "count": count})
    return out


@router.get("/expenses_by_category")
def expenses_by_category(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> List[Dict]:
    rows = (
        db.query(
            models.Expense.category_id,
            func.count(models.Expense.id),
            func.sum(models.Expense.amount),
        )
        .filter(models.Expense.org_id == user.org_id)
        .group_by(models.Expense.category_id)
        .all()
    )

    out: List[Dict] = []
    for cat_id, count, total in rows:
        cat = (
            db.query(models.ExpenseCategory)
            .filter(
                models.ExpenseCategory.id == cat_id,
                models.ExpenseCategory.org_id == user.org_id,
            )
            .first()
        )
        out.append(
            {
                "category_id": cat_id,
                "category_name": cat.name if cat else "Unknown",
                "count": count,
                "total": float(total or 0.0),
            }
        )
    return out
