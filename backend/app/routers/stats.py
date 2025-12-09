from typing import Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, or_, extract
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


@router.get("/comprehensive_metrics")
def comprehensive_metrics(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> Dict:
    """Get comprehensive metrics for the organization dashboard"""

    # Pet metrics
    total_pets = db.query(func.count(models.Pet.id)).filter(
        models.Pet.org_id == user.org_id
    ).scalar() or 0

    pets_available = db.query(func.count(models.Pet.id)).filter(
        models.Pet.org_id == user.org_id,
        models.Pet.status == models.PetStatus.available
    ).scalar() or 0

    pets_in_foster = db.query(func.count(models.Pet.id)).filter(
        models.Pet.org_id == user.org_id,
        models.Pet.status == models.PetStatus.in_foster
    ).scalar() or 0

    # TODO: Add updated_at field to Pet model to track when status changed
    # For now, counting all adopted pets instead of just this month
    pets_adopted_this_month = db.query(func.count(models.Pet.id)).filter(
        models.Pet.org_id == user.org_id,
        models.Pet.status == models.PetStatus.adopted
    ).scalar() or 0

    # Foster metrics
    total_foster_profiles = db.query(func.count(models.FosterProfile.id)).filter(
        models.FosterProfile.org_id == user.org_id
    ).scalar() or 0

    active_foster_profiles = db.query(func.count(models.FosterProfile.id)).filter(
        models.FosterProfile.org_id == user.org_id,
        models.FosterProfile.is_available == True
    ).scalar() or 0

    active_placements = db.query(func.count(models.FosterPlacement.id)).filter(
        models.FosterPlacement.org_id == user.org_id,
        models.FosterPlacement.outcome == models.PlacementOutcome.active
    ).scalar() or 0

    # Calculate foster capacity
    total_capacity = db.query(
        func.coalesce(func.sum(models.FosterProfile.max_capacity), 0)
    ).filter(
        models.FosterProfile.org_id == user.org_id,
        models.FosterProfile.is_available == True
    ).scalar() or 0

    available_capacity = int(total_capacity) - active_placements

    # Application metrics
    pending_applications = db.query(func.count(models.Application.id)).filter(
        models.Application.org_id == user.org_id,
        models.Application.status.in_([
            models.ApplicationStatus.submitted,
            models.ApplicationStatus.under_review,
            models.ApplicationStatus.interview_scheduled
        ])
    ).scalar() or 0

    approved_applications_this_month = db.query(func.count(models.Application.id)).filter(
        models.Application.org_id == user.org_id,
        models.Application.status == models.ApplicationStatus.approved,
        func.strftime("%Y-%m", models.Application.updated_at) == datetime.now().strftime("%Y-%m")
    ).scalar() or 0

    # Task metrics
    open_tasks = db.query(func.count(models.Task.id)).filter(
        models.Task.org_id == user.org_id,
        models.Task.status.in_([models.TaskStatus.open, models.TaskStatus.in_progress])
    ).scalar() or 0

    urgent_tasks = db.query(func.count(models.Task.id)).filter(
        models.Task.org_id == user.org_id,
        models.Task.status.in_([models.TaskStatus.open, models.TaskStatus.in_progress]),
        models.Task.priority == models.TaskPriority.urgent
    ).scalar() or 0

    # Financial metrics
    total_donations = db.query(
        func.coalesce(func.sum(models.Payment.amount), 0.0)
    ).filter(
        models.Payment.org_id == user.org_id,
        models.Payment.status == models.PaymentStatus.completed
    ).scalar() or 0.0

    total_expenses = db.query(
        func.coalesce(func.sum(models.Expense.amount), 0.0)
    ).filter(
        models.Expense.org_id == user.org_id
    ).scalar() or 0.0

    donations_this_month = db.query(
        func.coalesce(func.sum(models.Payment.amount), 0.0)
    ).filter(
        models.Payment.org_id == user.org_id,
        models.Payment.status == models.PaymentStatus.completed,
        func.strftime("%Y-%m", models.Payment.created_at) == datetime.now().strftime("%Y-%m")
    ).scalar() or 0.0

    # Volunteer/people metrics
    total_volunteers = db.query(func.count(models.Person.id)).filter(
        models.Person.org_id == user.org_id,
        models.Person.tag_volunteer == True
    ).scalar() or 0

    total_donors = db.query(func.count(models.Person.id)).filter(
        models.Person.org_id == user.org_id,
        models.Person.tag_donor == True
    ).scalar() or 0

    return {
        "pet_metrics": {
            "total_pets": total_pets,
            "pets_available": pets_available,
            "pets_in_foster": pets_in_foster,
            "pets_adopted_this_month": pets_adopted_this_month
        },
        "foster_metrics": {
            "total_foster_profiles": total_foster_profiles,
            "active_foster_profiles": active_foster_profiles,
            "active_placements": active_placements,
            "total_capacity": int(total_capacity),
            "available_capacity": available_capacity
        },
        "application_metrics": {
            "pending_applications": pending_applications,
            "approved_applications_this_month": approved_applications_this_month
        },
        "task_metrics": {
            "open_tasks": open_tasks,
            "urgent_tasks": urgent_tasks
        },
        "financial_metrics": {
            "total_donations": float(total_donations),
            "total_expenses": float(total_expenses),
            "donations_this_month": float(donations_this_month),
            "net_balance": float(total_donations - total_expenses)
        },
        "people_metrics": {
            "total_volunteers": total_volunteers,
            "total_donors": total_donors
        }
    }


@router.get("/intake_trends")
def intake_trends(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> List[Dict]:
    """Get pet intake trends over time"""

    cutoff_date = datetime.now() - timedelta(days=days)

    rows = (
        db.query(
            func.date(models.Pet.intake_date).label("date"),
            func.count(models.Pet.id).label("count")
        )
        .filter(
            models.Pet.org_id == user.org_id,
            models.Pet.intake_date >= cutoff_date
        )
        .group_by(func.date(models.Pet.intake_date))
        .order_by(func.date(models.Pet.intake_date))
        .all()
    )

    return [{"date": str(date), "count": count} for date, count in rows]


@router.get("/adoption_trends")
def adoption_trends(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> List[Dict]:
    """Get adoption trends over time"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # TODO: Add updated_at field to Pet model to track when status changed
    # For now, using created_at as approximation (not accurate for adoption trends)
    # This will show when pets were added to system, not when they were adopted
    rows = (
        db.query(
            func.date(models.Pet.created_at).label("date"),
            func.count(models.Pet.id).label("count")
        )
        .filter(
            models.Pet.org_id == user.org_id,
            models.Pet.status == models.PetStatus.adopted,
            models.Pet.created_at >= cutoff_date
        )
        .group_by(func.date(models.Pet.created_at))
        .order_by(func.date(models.Pet.created_at))
        .all()
    )

    return [{"date": str(date), "count": count} for date, count in rows]


@router.get("/foster_performance")
def foster_performance(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> Dict:
    """Get foster program performance metrics"""

    # Average placement duration
    avg_duration = db.query(
        func.avg(models.FosterProfile.avg_foster_duration_days)
    ).filter(
        models.FosterProfile.org_id == user.org_id,
        models.FosterProfile.avg_foster_duration_days.isnot(None)
    ).scalar() or 0.0

    # Total successful adoptions from foster
    total_success = db.query(
        func.coalesce(func.sum(models.FosterProfile.successful_adoptions), 0)
    ).filter(
        models.FosterProfile.org_id == user.org_id
    ).scalar() or 0

    # Placement outcomes breakdown
    outcome_counts = db.query(
        models.FosterPlacement.outcome,
        func.count(models.FosterPlacement.id)
    ).filter(
        models.FosterPlacement.org_id == user.org_id
    ).group_by(
        models.FosterPlacement.outcome
    ).all()

    outcomes = {}
    for outcome, count in outcome_counts:
        outcome_value = outcome.value if hasattr(outcome, "value") else str(outcome)
        outcomes[outcome_value] = count

    # Average foster rating
    avg_rating = db.query(
        func.avg(models.FosterProfile.rating)
    ).filter(
        models.FosterProfile.org_id == user.org_id,
        models.FosterProfile.rating.isnot(None)
    ).scalar() or 0.0

    # Top performing fosters
    top_fosters = db.query(
        models.FosterProfile.id,
        models.FosterProfile.user_id,
        models.FosterProfile.successful_adoptions,
        models.FosterProfile.rating
    ).filter(
        models.FosterProfile.org_id == user.org_id,
        models.FosterProfile.is_available == True
    ).order_by(
        models.FosterProfile.successful_adoptions.desc(),
        models.FosterProfile.rating.desc()
    ).limit(10).all()

    top_fosters_data = []
    for profile in top_fosters:
        user_obj = db.query(models.User).filter(models.User.id == profile.user_id).first()
        top_fosters_data.append({
            "profile_id": profile.id,
            "user_id": profile.user_id,
            "user_name": user_obj.full_name if user_obj else "Unknown",
            "successful_adoptions": profile.successful_adoptions or 0,
            "rating": float(profile.rating) if profile.rating else 0.0
        })

    return {
        "avg_placement_duration_days": float(avg_duration),
        "total_successful_adoptions": total_success,
        "placement_outcomes": outcomes,
        "avg_foster_rating": float(avg_rating),
        "top_performers": top_fosters_data
    }


@router.get("/species_breakdown")
def species_breakdown(
    db: Session = Depends(get_db), user=Depends(get_current_user)
) -> List[Dict]:
    """Get breakdown of pets by species"""

    rows = (
        db.query(
            models.Pet.species,
            func.count(models.Pet.id)
        )
        .filter(models.Pet.org_id == user.org_id)
        .group_by(models.Pet.species)
        .all()
    )

    return [{"species": species, "count": count} for species, count in rows]


@router.get("/application_trends")
def application_trends(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get application submission and approval trends"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Applications by type
    by_type = db.query(
        models.Application.type,
        func.count(models.Application.id)
    ).filter(
        models.Application.org_id == user.org_id,
        models.Application.created_at >= cutoff_date
    ).group_by(
        models.Application.type
    ).all()

    type_data = {}
    for app_type, count in by_type:
        type_value = app_type.value if hasattr(app_type, "value") else str(app_type)
        type_data[type_value] = count

    # Applications by status
    by_status = db.query(
        models.Application.status,
        func.count(models.Application.id)
    ).filter(
        models.Application.org_id == user.org_id,
        models.Application.created_at >= cutoff_date
    ).group_by(
        models.Application.status
    ).all()

    status_data = {}
    for app_status, count in by_status:
        status_value = app_status.value if hasattr(app_status, "value") else str(app_status)
        status_data[status_value] = count

    # Daily submissions
    daily_submissions = db.query(
        func.date(models.Application.created_at).label("date"),
        func.count(models.Application.id).label("count")
    ).filter(
        models.Application.org_id == user.org_id,
        models.Application.created_at >= cutoff_date
    ).group_by(
        func.date(models.Application.created_at)
    ).order_by(
        func.date(models.Application.created_at)
    ).all()

    return {
        "by_type": type_data,
        "by_status": status_data,
        "daily_submissions": [
            {"date": str(date), "count": count}
            for date, count in daily_submissions
        ]
    }
