"""
Reports Router
Endpoints for generating and exporting various reports
"""
import csv
import io
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_current_user, get_db

router = APIRouter(prefix="/reports", tags=["reports"])


def generate_csv(headers: list, rows: list) -> StreamingResponse:
    """Generate a CSV file from headers and rows"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerows(rows)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=report.csv"}
    )


@router.get("/pets/export")
def export_pets_report(
    status_filter: Optional[str] = None,
    species: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export pets report as CSV"""
    query = db.query(models.Pet).filter(models.Pet.org_id == current_user.org_id)

    if status_filter:
        query = query.filter(models.Pet.status == status_filter)

    if species:
        query = query.filter(models.Pet.species.ilike(f"%{species}%"))

    pets = query.all()

    headers = [
        "ID", "Name", "Species", "Breed", "Sex", "Status",
        "Intake Date", "Date of Birth", "Microchip", "Altered",
        "Description"
    ]

    rows = []
    for pet in pets:
        rows.append([
            pet.id,
            pet.name or "",
            pet.species or "",
            pet.breed or "",
            pet.sex or "",
            pet.status.value if hasattr(pet.status, "value") else str(pet.status),
            pet.intake_date.strftime("%Y-%m-%d") if pet.intake_date else "",
            pet.date_of_birth.strftime("%Y-%m-%d") if pet.date_of_birth else "",
            pet.microchip_number or "",
            pet.altered_status or "",
            pet.description_public or ""
        ])

    return generate_csv(headers, rows)


@router.get("/adoptions/export")
def export_adoptions_report(
    days: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export adoptions report as CSV"""
    cutoff_date = datetime.now() - timedelta(days=days)

    # Get adopted pets
    pets = db.query(models.Pet).filter(
        models.Pet.org_id == current_user.org_id,
        models.Pet.status == models.PetStatus.adopted,
        models.Pet.updated_at >= cutoff_date
    ).all()

    headers = [
        "Pet ID", "Pet Name", "Species", "Breed",
        "Adopter ID", "Adoption Date", "Days in System"
    ]

    rows = []
    for pet in pets:
        days_in_system = (pet.updated_at - pet.intake_date).days if pet.intake_date else 0
        rows.append([
            pet.id,
            pet.name or "",
            pet.species or "",
            pet.breed or "",
            pet.adopter_user_id or "",
            pet.updated_at.strftime("%Y-%m-%d") if pet.updated_at else "",
            days_in_system
        ])

    return generate_csv(headers, rows)


@router.get("/foster/placements/export")
def export_foster_placements_report(
    active_only: bool = False,
    days: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export foster placements report as CSV"""
    query = db.query(models.FosterPlacement).filter(
        models.FosterPlacement.org_id == current_user.org_id
    )

    if active_only:
        query = query.filter(models.FosterPlacement.outcome == models.PlacementOutcome.active)
    else:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(models.FosterPlacement.created_at >= cutoff_date)

    placements = query.all()

    headers = [
        "Placement ID", "Pet ID", "Pet Name", "Foster Profile ID",
        "Start Date", "Expected End", "Actual End", "Outcome",
        "Duration (days)", "Notes"
    ]

    rows = []
    for placement in placements:
        pet = placement.pet
        duration = ""
        if placement.actual_end_date:
            duration = (placement.actual_end_date - placement.start_date).days
        elif placement.outcome == models.PlacementOutcome.active:
            duration = (datetime.now() - placement.start_date).days

        rows.append([
            placement.id,
            placement.pet_id,
            pet.name if pet else "",
            placement.foster_profile_id,
            placement.start_date.strftime("%Y-%m-%d") if placement.start_date else "",
            placement.expected_end_date.strftime("%Y-%m-%d") if placement.expected_end_date else "",
            placement.actual_end_date.strftime("%Y-%m-%d") if placement.actual_end_date else "",
            placement.outcome.value if hasattr(placement.outcome, "value") else str(placement.outcome),
            duration,
            placement.placement_notes or ""
        ])

    return generate_csv(headers, rows)


@router.get("/foster/performance/export")
def export_foster_performance_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export foster performance report as CSV"""
    profiles = db.query(models.FosterProfile).filter(
        models.FosterProfile.org_id == current_user.org_id
    ).all()

    headers = [
        "Profile ID", "User ID", "Experience Level", "Max Capacity",
        "Current Capacity", "Total Fosters", "Successful Adoptions",
        "Avg Duration (days)", "Rating", "Status"
    ]

    rows = []
    for profile in profiles:
        rows.append([
            profile.id,
            profile.user_id,
            profile.experience_level.value if hasattr(profile.experience_level, "value") else str(profile.experience_level),
            profile.max_capacity or 0,
            profile.current_capacity or 0,
            profile.total_fosters or 0,
            profile.successful_adoptions or 0,
            f"{profile.avg_foster_duration_days:.1f}" if profile.avg_foster_duration_days else "0",
            f"{profile.rating:.1f}" if profile.rating else "0",
            profile.status or "unknown"
        ])

    return generate_csv(headers, rows)


@router.get("/applications/export")
def export_applications_report(
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    days: int = Query(default=90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export applications report as CSV"""
    cutoff_date = datetime.now() - timedelta(days=days)

    query = db.query(models.Application).filter(
        models.Application.org_id == current_user.org_id,
        models.Application.created_at >= cutoff_date
    )

    if type_filter:
        try:
            app_type = models.ApplicationType(type_filter)
            query = query.filter(models.Application.type == app_type)
        except ValueError:
            pass

    if status_filter:
        try:
            app_status = models.ApplicationStatus(status_filter)
            query = query.filter(models.Application.status == app_status)
        except ValueError:
            pass

    applications = query.all()

    headers = [
        "Application ID", "Type", "Status", "Applicant User ID",
        "Pet ID", "Submitted Date", "Updated Date", "Days Pending"
    ]

    rows = []
    for app in applications:
        days_pending = (datetime.now() - app.created_at).days if app.status in [
            models.ApplicationStatus.submitted,
            models.ApplicationStatus.under_review,
            models.ApplicationStatus.interview_scheduled
        ] else 0

        rows.append([
            app.id,
            app.type.value if hasattr(app.type, "value") else str(app.type),
            app.status.value if hasattr(app.status, "value") else str(app.status),
            app.applicant_user_id,
            app.pet_id or "",
            app.created_at.strftime("%Y-%m-%d") if app.created_at else "",
            app.updated_at.strftime("%Y-%m-%d") if app.updated_at else "",
            days_pending
        ])

    return generate_csv(headers, rows)


@router.get("/financial/donations/export")
def export_donations_report(
    days: int = Query(default=365, ge=1, le=730),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export donations report as CSV"""
    cutoff_date = datetime.now() - timedelta(days=days)

    payments = db.query(models.Payment).filter(
        models.Payment.org_id == current_user.org_id,
        models.Payment.status == models.PaymentStatus.completed,
        models.Payment.created_at >= cutoff_date
    ).all()

    headers = [
        "Payment ID", "Amount", "Date", "User ID", "Purpose", "Status"
    ]

    rows = []
    for payment in payments:
        rows.append([
            payment.id,
            f"${payment.amount:.2f}" if payment.amount else "$0.00",
            payment.created_at.strftime("%Y-%m-%d") if payment.created_at else "",
            payment.user_id or "",
            payment.purpose.value if hasattr(payment.purpose, "value") else str(payment.purpose),
            payment.status.value if hasattr(payment.status, "value") else str(payment.status)
        ])

    return generate_csv(headers, rows)


@router.get("/financial/expenses/export")
def export_expenses_report(
    days: int = Query(default=365, ge=1, le=730),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export expenses report as CSV"""
    cutoff_date = datetime.now() - timedelta(days=days)

    expenses = db.query(models.Expense).filter(
        models.Expense.org_id == current_user.org_id,
        models.Expense.date_incurred >= cutoff_date
    ).all()

    headers = [
        "Expense ID", "Category", "Amount", "Date", "Description"
    ]

    rows = []
    for expense in expenses:
        category = ""
        if expense.category_id:
            cat = db.query(models.ExpenseCategory).filter(
                models.ExpenseCategory.id == expense.category_id
            ).first()
            category = cat.name if cat else ""

        rows.append([
            expense.id,
            category,
            f"${expense.amount:.2f}" if expense.amount else "$0.00",
            expense.date_incurred.strftime("%Y-%m-%d") if expense.date_incurred else "",
            expense.description or ""
        ])

    return generate_csv(headers, rows)


@router.get("/people/export")
def export_people_report(
    tag_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Export people/contacts report as CSV"""
    query = db.query(models.Person).filter(models.Person.org_id == current_user.org_id)

    # Apply tag filter if provided
    if tag_filter:
        tag_map = {
            "adopter": models.Person.tag_adopter,
            "foster": models.Person.tag_foster,
            "volunteer": models.Person.tag_volunteer,
            "donor": models.Person.tag_donor
        }
        if tag_filter in tag_map:
            query = query.filter(tag_map[tag_filter] == True)

    people = query.all()

    headers = [
        "ID", "First Name", "Last Name", "Email", "Phone",
        "Address", "City", "State", "Zip",
        "Tags"
    ]

    rows = []
    for person in people:
        tags = []
        if person.tag_adopter:
            tags.append("adopter")
        if person.tag_foster:
            tags.append("foster")
        if person.tag_volunteer:
            tags.append("volunteer")
        if person.tag_donor:
            tags.append("donor")

        rows.append([
            person.id,
            person.first_name or "",
            person.last_name or "",
            person.email or "",
            person.phone or "",
            person.street_1 or "",
            person.city or "",
            person.state or "",
            person.zip_code or "",
            ", ".join(tags)
        ])

    return generate_csv(headers, rows)
