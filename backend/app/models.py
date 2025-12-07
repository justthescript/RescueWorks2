import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class ApplicationType(str, enum.Enum):
    adoption = "adoption"
    foster = "foster"
    volunteer = "volunteer"
    board = "board"


class ApplicationStatus(str, enum.Enum):
    submitted = "submitted"
    under_review = "under_review"
    interview_scheduled = "interview_scheduled"
    approved = "approved"
    denied = "denied"


class PetStatus(str, enum.Enum):
    intake = "intake"
    needs_foster = "needs_foster"
    in_foster = "in_foster"
    available = "available"
    pending = "pending"
    adopted = "adopted"
    medical_hold = "medical_hold"


class TaskStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"


class TaskPriority(str, enum.Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class FosterExperienceLevel(str, enum.Enum):
    none = "none"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class HomeType(str, enum.Enum):
    house = "house"
    apartment = "apartment"
    condo = "condo"
    townhouse = "townhouse"
    other = "other"


class PlacementOutcome(str, enum.Enum):
    active = "active"
    adopted = "adopted"
    returned = "returned"
    transferred = "transferred"


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"
    canceled = "canceled"


class PaymentPurpose(str, enum.Enum):
    adoption_fee = "adoption_fee"
    donation = "donation"
    event_ticket = "event_ticket"
    reimbursement = "reimbursement"
    other = "other"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    logo_url = Column(String, nullable=True)
    primary_contact_email = Column(String, nullable=True)

    users = relationship("User", back_populates="organization")
    pets = relationship("Pet", back_populates="organization")
    applications = relationship("Application", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="users")
    roles = relationship("UserRole", back_populates="user")
    tasks_assigned = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assigned_to_user_id"
    )
    foster_profile = relationship("FosterProfile", back_populates="user", uselist=False)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    users = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


class Pet(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    breed = Column(String, nullable=True)
    sex = Column(String, nullable=True)
    status = Column(Enum(PetStatus), default=PetStatus.intake)
    description_public = Column(Text, nullable=True)
    description_internal = Column(Text, nullable=True)
    photo_url = Column(String, nullable=True)
    foster_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    adopter_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="pets")
    medical_records = relationship("MedicalRecord", back_populates="pet")
    appointments = relationship("Appointment", back_populates="pet")
    foster = relationship("User", foreign_keys=[foster_user_id])
    adopter = relationship("User", foreign_keys=[adopter_user_id])


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    applicant_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    type = Column(Enum(ApplicationType), nullable=False)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.submitted)
    answers_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="applications")
    applicant = relationship("User")
    pet = relationship("Pet")


class FosterProfile(Base):
    __tablename__ = "foster_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Experience and preferences
    experience_level = Column(Enum(FosterExperienceLevel), default=FosterExperienceLevel.none)
    preferred_species = Column(String, nullable=True)  # Comma-separated list
    preferred_ages = Column(String, nullable=True)  # e.g., "puppy,adult"
    max_capacity = Column(Integer, default=1)
    current_capacity = Column(Integer, default=0)

    # Home information
    home_type = Column(Enum(HomeType), nullable=True)
    has_yard = Column(Boolean, default=False)
    has_other_pets = Column(Boolean, default=False)
    other_pets_description = Column(Text, nullable=True)
    has_children = Column(Boolean, default=False)
    children_ages = Column(String, nullable=True)

    # Qualifications
    can_handle_medical = Column(Boolean, default=False)
    can_handle_behavioral = Column(Boolean, default=False)
    training_completed = Column(Text, nullable=True)  # Comma-separated list of completed trainings
    certifications = Column(Text, nullable=True)

    # Availability
    available_from = Column(DateTime, nullable=True)
    available_until = Column(DateTime, nullable=True)
    is_available = Column(Boolean, default=True)

    # Performance metrics
    total_fosters = Column(Integer, default=0)
    successful_adoptions = Column(Integer, default=0)
    avg_foster_duration_days = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)  # 0-5 stars

    # Admin fields
    background_check_status = Column(String, nullable=True)  # pending, approved, denied
    background_check_date = Column(DateTime, nullable=True)
    insurance_verified = Column(Boolean, default=False)
    references_checked = Column(Boolean, default=False)
    notes_internal = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="foster_profile")
    placements = relationship("FosterPlacement", back_populates="foster_profile")


class FosterPlacement(Base):
    __tablename__ = "foster_placements"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    foster_profile_id = Column(Integer, ForeignKey("foster_profiles.id"), nullable=False)

    # Placement details
    start_date = Column(DateTime, default=datetime.utcnow)
    expected_end_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)
    outcome = Column(Enum(PlacementOutcome), default=PlacementOutcome.active)

    # Placement metadata
    placement_notes = Column(Text, nullable=True)  # Special instructions for foster
    return_reason = Column(Text, nullable=True)
    success_notes = Column(Text, nullable=True)

    # Agreement and documentation
    agreement_signed = Column(Boolean, default=False)
    agreement_signed_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    foster_profile = relationship("FosterProfile", back_populates="placements")
    pet = relationship("Pet")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    visibility = Column(String, default="staff_only")
    created_at = Column(DateTime, default=datetime.utcnow)

    pet = relationship("Pet", back_populates="medical_records")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    type = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    pet = relationship("Pet", back_populates="appointments")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=True)
    location_name = Column(String, nullable=True)
    location_address = Column(String, nullable=True)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EventSignup(Base):
    __tablename__ = "event_signups"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=True)
    shift_start = Column(DateTime, nullable=True)
    shift_end = Column(DateTime, nullable=True)
    status = Column(String, default="confirmed")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.open)
    priority = Column(Enum(TaskPriority), default=TaskPriority.normal)
    due_date = Column(DateTime, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    related_pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    related_application_id = Column(
        Integer, ForeignKey("applications.id"), nullable=True
    )
    related_event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assignee = relationship("User", foreign_keys=[assigned_to_user_id])


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    date_incurred = Column(DateTime, default=datetime.utcnow)
    description = Column(Text, nullable=True)
    vendor_name = Column(String, nullable=True)
    recorded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class MessageThread(Base):
    __tablename__ = "message_threads"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    subject = Column(String, nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    related_pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    related_application_id = Column(
        Integer, ForeignKey("applications.id"), nullable=True
    )
    is_external = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("message_threads.id"), nullable=False)
    sender_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    body_text = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    purpose = Column(Enum(PaymentPurpose), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    provider = Column(String, default="manual")
    gateway_payment_id = Column(String, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    status_detail = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentVisibility(enum.Enum):
    internal = "internal"
    foster = "foster"
    adopter = "adopter"
    vet_only = "vet_only"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    uploader_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=True)
    medical_record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    visibility = Column(Enum(DocumentVisibility), default=DocumentVisibility.internal)
    created_at = Column(DateTime, default=datetime.utcnow)


class OrganizationSettings(Base):
    __tablename__ = "organization_settings"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email_provider = Column(String, nullable=True)
    email_from_address = Column(String, nullable=True)
    sms_provider = Column(String, nullable=True)
    sms_from_number = Column(String, nullable=True)
    stripe_public_key = Column(String, nullable=True)
    stripe_secret_key = Column(String, nullable=True)
    paypal_client_id = Column(String, nullable=True)
    paypal_client_secret = Column(String, nullable=True)
    petfinder_api_key = Column(String, nullable=True)
    petfinder_secret = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    discount_type = Column(String, nullable=False)
    discount_value = Column(Float, nullable=False)
    valid_from = Column(DateTime, nullable=True)
    valid_to = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)
    current_uses = Column(Integer, default=0)
    applicable_purpose = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
