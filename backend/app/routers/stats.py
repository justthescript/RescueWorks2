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


@router.get("/medical_operations")
def medical_operations(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get medical and veterinary operations metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Total medical records
    total_records = db.query(func.count(models.MedicalRecord.id)).filter(
        models.MedicalRecord.org_id == user.org_id,
        models.MedicalRecord.date >= cutoff_date
    ).scalar() or 0

    # Medical records by type
    by_type = db.query(
        models.MedicalRecord.record_type,
        func.count(models.MedicalRecord.id)
    ).filter(
        models.MedicalRecord.org_id == user.org_id,
        models.MedicalRecord.date >= cutoff_date
    ).group_by(
        models.MedicalRecord.record_type
    ).all()

    records_by_type = {record_type: count for record_type, count in by_type}

    # Upcoming appointments
    upcoming_appointments = db.query(func.count(models.Appointment.id)).filter(
        models.Appointment.org_id == user.org_id,
        models.Appointment.date_time >= datetime.now()
    ).scalar() or 0

    # Appointments by type
    appointments_by_type = db.query(
        models.Appointment.type,
        func.count(models.Appointment.id)
    ).filter(
        models.Appointment.org_id == user.org_id,
        models.Appointment.date_time >= cutoff_date
    ).group_by(
        models.Appointment.type
    ).all()

    appt_type_data = {appt_type: count for appt_type, count in appointments_by_type}

    # Pets on medical hold
    medical_hold_count = db.query(func.count(models.Pet.id)).filter(
        models.Pet.org_id == user.org_id,
        models.Pet.status == models.PetStatus.medical_hold
    ).scalar() or 0

    return {
        "total_medical_records": total_records,
        "records_by_type": records_by_type,
        "upcoming_appointments": upcoming_appointments,
        "appointments_by_type": appt_type_data,
        "pets_on_medical_hold": medical_hold_count
    }


@router.get("/event_participation")
def event_participation(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get event participation and volunteer engagement metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Total events
    total_events = db.query(func.count(models.Event.id)).filter(
        models.Event.org_id == user.org_id,
        models.Event.date_time >= cutoff_date
    ).scalar() or 0

    # Upcoming events
    upcoming_events = db.query(func.count(models.Event.id)).filter(
        models.Event.org_id == user.org_id,
        models.Event.date_time >= datetime.now()
    ).scalar() or 0

    # Total signups
    total_signups = db.query(func.count(models.EventSignup.id)).join(
        models.Event
    ).filter(
        models.Event.org_id == user.org_id,
        models.Event.date_time >= cutoff_date
    ).scalar() or 0

    # Average signups per event
    avg_signups = total_signups / total_events if total_events > 0 else 0

    # Events with capacity info
    events_with_capacity = db.query(
        models.Event.id,
        models.Event.capacity,
        func.count(models.EventSignup.id).label("signup_count")
    ).outerjoin(
        models.EventSignup
    ).filter(
        models.Event.org_id == user.org_id,
        models.Event.date_time >= cutoff_date,
        models.Event.capacity.isnot(None)
    ).group_by(
        models.Event.id
    ).all()

    total_capacity = sum(e.capacity for e in events_with_capacity if e.capacity)
    total_filled = sum(e.signup_count for e in events_with_capacity)
    capacity_utilization = (total_filled / total_capacity * 100) if total_capacity > 0 else 0

    return {
        "total_events": total_events,
        "upcoming_events": upcoming_events,
        "total_signups": total_signups,
        "avg_signups_per_event": round(avg_signups, 2),
        "capacity_utilization_percent": round(capacity_utilization, 2)
    }


@router.get("/communication_metrics")
def communication_metrics(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get messaging and communication metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Total message threads
    total_threads = db.query(func.count(models.MessageThread.id)).filter(
        models.MessageThread.org_id == user.org_id,
        models.MessageThread.created_at >= cutoff_date
    ).scalar() or 0

    # Total messages
    total_messages = db.query(func.count(models.Message.id)).join(
        models.MessageThread
    ).filter(
        models.MessageThread.org_id == user.org_id,
        models.Message.created_at >= cutoff_date
    ).scalar() or 0

    # Average messages per thread
    avg_messages = total_messages / total_threads if total_threads > 0 else 0

    # External vs internal threads
    external_threads = db.query(func.count(models.MessageThread.id)).filter(
        models.MessageThread.org_id == user.org_id,
        models.MessageThread.is_external == True,
        models.MessageThread.created_at >= cutoff_date
    ).scalar() or 0

    internal_threads = total_threads - external_threads

    return {
        "total_threads": total_threads,
        "total_messages": total_messages,
        "avg_messages_per_thread": round(avg_messages, 2),
        "external_threads": external_threads,
        "internal_threads": internal_threads
    }


@router.get("/document_metrics")
def document_metrics(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get document management metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Total documents
    total_docs = db.query(func.count(models.Document.id)).filter(
        models.Document.org_id == user.org_id,
        models.Document.uploaded_at >= cutoff_date
    ).scalar() or 0

    # Documents by visibility
    by_visibility = db.query(
        models.Document.visibility,
        func.count(models.Document.id)
    ).filter(
        models.Document.org_id == user.org_id,
        models.Document.uploaded_at >= cutoff_date
    ).group_by(
        models.Document.visibility
    ).all()

    visibility_data = {}
    for visibility, count in by_visibility:
        vis_value = visibility.value if hasattr(visibility, "value") else str(visibility)
        visibility_data[vis_value] = count

    # Documents by entity type (pet, application, person)
    pet_docs = db.query(func.count(models.Document.id)).filter(
        models.Document.org_id == user.org_id,
        models.Document.pet_id.isnot(None),
        models.Document.uploaded_at >= cutoff_date
    ).scalar() or 0

    application_docs = db.query(func.count(models.Document.id)).filter(
        models.Document.org_id == user.org_id,
        models.Document.application_id.isnot(None),
        models.Document.uploaded_at >= cutoff_date
    ).scalar() or 0

    person_docs = db.query(func.count(models.Document.id)).filter(
        models.Document.org_id == user.org_id,
        models.Document.person_id.isnot(None),
        models.Document.uploaded_at >= cutoff_date
    ).scalar() or 0

    return {
        "total_documents": total_docs,
        "by_visibility": visibility_data,
        "by_entity": {
            "pet_documents": pet_docs,
            "application_documents": application_docs,
            "person_documents": person_docs
        }
    }


@router.get("/financial_operations")
def financial_operations(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get detailed financial operations metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Payments by purpose
    by_purpose = db.query(
        models.Payment.purpose,
        func.count(models.Payment.id),
        func.coalesce(func.sum(models.Payment.amount), 0.0)
    ).filter(
        models.Payment.org_id == user.org_id,
        models.Payment.created_at >= cutoff_date,
        models.Payment.status == models.PaymentStatus.completed
    ).group_by(
        models.Payment.purpose
    ).all()

    purpose_data = {}
    for purpose, count, total in by_purpose:
        purpose_value = purpose.value if hasattr(purpose, "value") else str(purpose)
        purpose_data[purpose_value] = {
            "count": count,
            "total_amount": float(total)
        }

    # Payments by provider
    by_provider = db.query(
        models.Payment.provider,
        func.count(models.Payment.id),
        func.coalesce(func.sum(models.Payment.amount), 0.0)
    ).filter(
        models.Payment.org_id == user.org_id,
        models.Payment.created_at >= cutoff_date,
        models.Payment.status == models.PaymentStatus.completed
    ).group_by(
        models.Payment.provider
    ).all()

    provider_data = {}
    for provider, count, total in by_provider:
        provider_data[provider] = {
            "count": count,
            "total_amount": float(total)
        }

    # Daily payment trends
    daily_payments = db.query(
        func.date(models.Payment.created_at).label("date"),
        func.count(models.Payment.id).label("count"),
        func.coalesce(func.sum(models.Payment.amount), 0.0).label("total")
    ).filter(
        models.Payment.org_id == user.org_id,
        models.Payment.created_at >= cutoff_date,
        models.Payment.status == models.PaymentStatus.completed
    ).group_by(
        func.date(models.Payment.created_at)
    ).order_by(
        func.date(models.Payment.created_at)
    ).all()

    # Expense trends
    daily_expenses = db.query(
        func.date(models.Expense.date).label("date"),
        func.count(models.Expense.id).label("count"),
        func.coalesce(func.sum(models.Expense.amount), 0.0).label("total")
    ).filter(
        models.Expense.org_id == user.org_id,
        models.Expense.date >= cutoff_date
    ).group_by(
        func.date(models.Expense.date)
    ).order_by(
        func.date(models.Expense.date)
    ).all()

    return {
        "by_purpose": purpose_data,
        "by_provider": provider_data,
        "daily_payments": [
            {"date": str(date), "count": count, "total": float(total)}
            for date, count, total in daily_payments
        ],
        "daily_expenses": [
            {"date": str(date), "count": count, "total": float(total)}
            for date, count, total in daily_expenses
        ]
    }


@router.get("/operational_efficiency")
def operational_efficiency(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get operational efficiency metrics"""

    # Average time to adoption (from intake to adopted status)
    # Note: This is an approximation since we don't track status change timestamps
    adopted_pets = db.query(
        models.Pet.intake_date,
        models.Pet.created_at
    ).filter(
        models.Pet.org_id == user.org_id,
        models.Pet.status == models.PetStatus.adopted,
        models.Pet.intake_date.isnot(None)
    ).all()

    if adopted_pets:
        # Calculate average days from intake to now (approximation)
        total_days = sum(
            (datetime.now().date() - pet.intake_date).days
            for pet in adopted_pets
            if pet.intake_date
        )
        avg_days_to_adoption = total_days / len(adopted_pets)
    else:
        avg_days_to_adoption = 0

    # Task completion rate
    total_tasks = db.query(func.count(models.Task.id)).filter(
        models.Task.org_id == user.org_id
    ).scalar() or 0

    completed_tasks = db.query(func.count(models.Task.id)).filter(
        models.Task.org_id == user.org_id,
        models.Task.status == models.TaskStatus.completed
    ).scalar() or 0

    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # Average task completion time (using created_at and updated_at)
    completed_task_times = db.query(
        models.Task.created_at,
        models.Task.updated_at
    ).filter(
        models.Task.org_id == user.org_id,
        models.Task.status == models.TaskStatus.completed,
        models.Task.updated_at.isnot(None)
    ).all()

    if completed_task_times:
        total_hours = sum(
            (task.updated_at - task.created_at).total_seconds() / 3600
            for task in completed_task_times
        )
        avg_task_completion_hours = total_hours / len(completed_task_times)
    else:
        avg_task_completion_hours = 0

    # Application processing efficiency
    approved_apps = db.query(
        models.Application.created_at,
        models.Application.updated_at
    ).filter(
        models.Application.org_id == user.org_id,
        models.Application.status == models.ApplicationStatus.approved,
        models.Application.updated_at.isnot(None)
    ).all()

    if approved_apps:
        total_days = sum(
            (app.updated_at - app.created_at).total_seconds() / 86400
            for app in approved_apps
        )
        avg_app_processing_days = total_days / len(approved_apps)
    else:
        avg_app_processing_days = 0

    return {
        "avg_days_to_adoption": round(avg_days_to_adoption, 2),
        "task_completion_rate_percent": round(completion_rate, 2),
        "avg_task_completion_hours": round(avg_task_completion_hours, 2),
        "avg_application_processing_days": round(avg_app_processing_days, 2)
    }


@router.get("/user_activity")
def user_activity(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
) -> Dict:
    """Get user and staff activity metrics"""

    cutoff_date = datetime.now() - timedelta(days=days)

    # Total users
    total_users = db.query(func.count(models.User.id)).filter(
        models.User.org_id == user.org_id
    ).scalar() or 0

    # Active users (users who created/updated something recently)
    # Using audit logs if available
    active_user_ids = db.query(models.AuditLog.user_id.distinct()).filter(
        models.AuditLog.org_id == user.org_id,
        models.AuditLog.created_at >= cutoff_date
    ).all()

    active_users = len(active_user_ids) if active_user_ids else 0

    # Users by role
    role_counts = db.query(
        models.Role.name,
        func.count(models.UserRole.user_id.distinct())
    ).join(
        models.UserRole
    ).join(
        models.User
    ).filter(
        models.User.org_id == user.org_id
    ).group_by(
        models.Role.name
    ).all()

    users_by_role = {role: count for role, count in role_counts}

    # New users registered in period
    new_users = db.query(func.count(models.User.id)).filter(
        models.User.org_id == user.org_id,
        models.User.created_at >= cutoff_date
    ).scalar() or 0

    return {
        "total_users": total_users,
        "active_users": active_users,
        "new_users": new_users,
        "users_by_role": users_by_role
    }
