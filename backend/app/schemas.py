from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator


class ApplicationType(str, Enum):
    adoption = "adoption"
    foster = "foster"
    volunteer = "volunteer"
    board = "board"


class ApplicationStatus(str, Enum):
    submitted = "submitted"
    under_review = "under_review"
    interview_scheduled = "interview_scheduled"
    approved = "approved"
    denied = "denied"


class PetStatus(str, Enum):
    intake = "intake"
    needs_foster = "needs_foster"
    in_foster = "in_foster"
    available = "available"
    pending = "pending"
    adopted = "adopted"
    medical_hold = "medical_hold"


class AlteredStatus(str, Enum):
    yes = "yes"
    no = "no"
    unsure = "unsure"



class TaskStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"


class TaskPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class FosterExperienceLevel(str, Enum):
    none = "none"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class HomeType(str, Enum):
    house = "house"
    apartment = "apartment"
    condo = "condo"
    townhouse = "townhouse"
    other = "other"


class PlacementOutcome(str, Enum):
    active = "active"
    adopted = "adopted"
    returned = "returned"
    transferred = "transferred"


class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"
    canceled = "canceled"


class PaymentPurpose(str, Enum):
    adoption_fee = "adoption_fee"
    donation = "donation"
    event_ticket = "event_ticket"
    reimbursement = "reimbursement"
    other = "other"


class OrganizationBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    primary_contact_email: Optional[EmailStr] = None


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    org_id: int


class User(UserBase):
    id: int
    org_id: int
    is_active: bool

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    class Config:
        orm_mode = True


class UserRoleAssignment(BaseModel):
    role_id: int


class UserWithRoles(User):
    roles: List[Role] = []

    class Config:
        orm_mode = True


class PetBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Pet name (required)"
    )
    species: str = Field(
        ..., min_length=1, max_length=50, description="Species (e.g., Dog, Cat, Bird)"
    )
    breed: Optional[str] = Field(None, max_length=100, description="Breed or mix")
    sex: Optional[str] = Field(None, description="Sex of the animal")

    # NEW FIELDS
    intake_date: Optional[date] = Field(
        None, description="Date the animal was taken into rescue"
    )
    microchip_number: Optional[str] = Field(
        None, max_length=100, description="Microchip number if available"
    )
    weight: Optional[float] = Field(
        None, gt=0, description="Weight in pounds"
    )
    altered_status: Optional[AlteredStatus] = Field(
        None, description="Spay or neuter status"
    )
    date_of_birth: Optional[date] = Field(
        None, description="Date of birth (exact or estimated)"
    )

    status: PetStatus = PetStatus.intake
    description_public: Optional[str] = Field(
        None, max_length=2000, description="Public description for adopters"
    )
    description_internal: Optional[str] = Field(
        None, max_length=2000, description="Internal notes for staff"
    )
    photo_url: Optional[str] = Field(None, max_length=500)
    foster_user_id: Optional[int] = None
    adopter_user_id: Optional[int] = None

    @validator("sex")
    def validate_sex(cls, v):
        if v is not None:
            valid_sexes = ["Male", "Female", "Unknown", "M", "F", "U"]
            if v not in valid_sexes:
                raise ValueError(f'Sex must be one of: {", ".join(valid_sexes)}')
        return v

    @validator("name", "species")
    def validate_required_strings(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("Field cannot be empty or whitespace only")
        return v.strip() if v else v


class PetCreate(PetBase):
    org_id: Optional[int] = None  # Will be auto-populated from authenticated user if not provided


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    sex: Optional[str] = None

    intake_date: Optional[date] = None
    microchip_number: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, gt=0)
    altered_status: Optional[AlteredStatus] = None
    date_of_birth: Optional[date] = None

    status: Optional[PetStatus] = None
    description_public: Optional[str] = Field(None, max_length=2000)
    description_internal: Optional[str] = Field(None, max_length=2000)
    photo_url: Optional[str] = Field(None, max_length=500)
    foster_user_id: Optional[int] = None
    adopter_user_id: Optional[int] = None
    ...


    @validator("sex")
    def validate_sex(cls, v):
        if v is not None:
            valid_sexes = ["Male", "Female", "Unknown", "M", "F", "U"]
            if v not in valid_sexes:
                raise ValueError(f'Sex must be one of: {", ".join(valid_sexes)}')
        return v


class Pet(PetBase):
    id: int
    org_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FosterAssignment(BaseModel):
    foster_user_id: int

    class Config:
        orm_mode = True


class ApplicationBase(BaseModel):
    org_id: int
    pet_id: Optional[int] = None
    type: ApplicationType
    answers_json: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    answers_json: Optional[str] = None
    pet_id: Optional[int] = None


class Application(ApplicationBase):
    id: int
    applicant_user_id: int
    status: ApplicationStatus
    created_at: datetime

    class Config:
        orm_mode = True


class MedicalRecordBase(BaseModel):
    pet_id: int
    record_type: str
    notes: Optional[str] = None
    visibility: str = "staff_only"


class MedicalRecordCreate(MedicalRecordBase):
    org_id: int


class MedicalRecord(MedicalRecordBase):
    id: int
    org_id: int
    created_by_user_id: int
    date: datetime
    created_at: datetime

    class Config:
        orm_mode = True


class AppointmentBase(BaseModel):
    pet_id: Optional[int] = None
    type: str
    date_time: datetime
    location: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    org_id: int


class Appointment(AppointmentBase):
    id: int
    org_id: int

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    capacity: Optional[int] = None


class EventCreate(EventBase):
    org_id: int


class Event(EventBase):
    id: int
    org_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class EventSignupBase(BaseModel):
    event_id: int
    role: Optional[str] = None
    shift_start: Optional[datetime] = None
    shift_end: Optional[datetime] = None


class EventSignupCreate(EventSignupBase):
    pass


class EventSignup(EventSignupBase):
    id: int
    user_id: int
    status: str

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.open
    priority: TaskPriority = TaskPriority.normal
    due_date: Optional[datetime] = None
    related_pet_id: Optional[int] = None
    related_application_id: Optional[int] = None
    related_event_id: Optional[int] = None


class TaskCreate(TaskBase):
    assigned_to_user_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to_user_id: Optional[int] = None


class Task(TaskBase):
    id: int
    org_id: int
    created_by_user_id: int
    assigned_to_user_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class ExpenseCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class ExpenseCategoryCreate(ExpenseCategoryBase):
    org_id: int


class ExpenseCategory(ExpenseCategoryBase):
    id: int
    org_id: int

    class Config:
        orm_mode = True


class ExpenseBase(BaseModel):
    category_id: int
    amount: float
    currency: str = "USD"
    date_incurred: datetime
    description: Optional[str] = None
    vendor_name: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    org_id: int


class Expense(ExpenseBase):
    id: int
    org_id: int
    recorded_by_user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MessageThreadBase(BaseModel):
    subject: str
    related_pet_id: Optional[int] = None
    related_application_id: Optional[int] = None
    is_external: bool = False


class MessageThreadCreate(MessageThreadBase):
    org_id: int


class MessageThread(MessageThreadBase):
    id: int
    org_id: int
    created_by_user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class MessageBase(BaseModel):
    thread_id: int
    body_text: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    sender_user_id: int
    sent_at: datetime

    class Config:
        orm_mode = True


class PaymentBase(BaseModel):
    user_id: int
    pet_id: Optional[int] = None
    purpose: PaymentPurpose
    amount: float
    currency: str = "USD"
    provider: str = "manual"
    gateway_payment_id: Optional[str] = None
    status_detail: Optional[str] = None


class PaymentCreate(PaymentBase):
    org_id: int


class Payment(PaymentBase):
    id: int
    org_id: int
    status: PaymentStatus
    created_at: datetime

    class Config:
        orm_mode = True


class CouponBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    max_uses: Optional[int] = None
    applicable_purpose: Optional[str] = None
    is_active: bool = True


class CouponCreate(CouponBase):
    org_id: int


class Coupon(CouponBase):
    id: int
    org_id: int
    current_uses: int

    class Config:
        orm_mode = True


class OrganizationSettingsBase(BaseModel):
    email_provider: Optional[str] = None
    email_from_address: Optional[str] = None
    sms_provider: Optional[str] = None
    sms_from_number: Optional[str] = None
    stripe_public_key: Optional[str] = None
    stripe_secret_key: Optional[str] = None
    paypal_client_id: Optional[str] = None
    paypal_client_secret: Optional[str] = None
    petfinder_api_key: Optional[str] = None
    petfinder_secret: Optional[str] = None


class OrganizationSettingsUpdate(OrganizationSettingsBase):
    pass


class OrganizationSettings(OrganizationSettingsBase):
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class DocumentBase(BaseModel):
    pet_id: Optional[int] = None
    medical_record_id: Optional[int] = None
    event_id: Optional[int] = None
    task_id: Optional[int] = None
    file_path: str
    file_type: Optional[str] = None
    visibility: Optional[str] = "internal"


class Document(DocumentBase):
    id: int
    org_id: int
    uploader_user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class FosterProfileBase(BaseModel):
    # Experience and preferences
    experience_level: FosterExperienceLevel = FosterExperienceLevel.none
    preferred_species: Optional[str] = None
    preferred_ages: Optional[str] = None
    max_capacity: int = 1
    current_capacity: int = 0

    # Home information
    home_type: Optional[HomeType] = None
    has_yard: bool = False
    has_other_pets: bool = False
    other_pets_description: Optional[str] = None
    has_children: bool = False
    children_ages: Optional[str] = None

    # Qualifications
    can_handle_medical: bool = False
    can_handle_behavioral: bool = False
    training_completed: Optional[str] = None
    certifications: Optional[str] = None

    # Availability
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    is_available: bool = True


class FosterProfileCreate(FosterProfileBase):
    org_id: int


class FosterProfileUpdate(BaseModel):
    experience_level: Optional[FosterExperienceLevel] = None
    preferred_species: Optional[str] = None
    preferred_ages: Optional[str] = None
    max_capacity: Optional[int] = None
    home_type: Optional[HomeType] = None
    has_yard: Optional[bool] = None
    has_other_pets: Optional[bool] = None
    other_pets_description: Optional[str] = None
    has_children: Optional[bool] = None
    children_ages: Optional[str] = None
    can_handle_medical: Optional[bool] = None
    can_handle_behavioral: Optional[bool] = None
    training_completed: Optional[str] = None
    certifications: Optional[str] = None
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None
    is_available: Optional[bool] = None


class FosterProfile(FosterProfileBase):
    id: int
    user_id: int
    org_id: int
    total_fosters: int
    successful_adoptions: int
    avg_foster_duration_days: Optional[float]
    rating: Optional[float]
    background_check_status: Optional[str]
    background_check_date: Optional[datetime]
    insurance_verified: bool
    references_checked: bool
    notes_internal: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class FosterProfileAdmin(FosterProfile):
    """Admin view with all fields including sensitive data"""
    pass


class FosterPlacementBase(BaseModel):
    pet_id: int
    foster_profile_id: int
    expected_end_date: Optional[datetime] = None
    placement_notes: Optional[str] = None


class FosterPlacementCreate(FosterPlacementBase):
    org_id: int


class FosterPlacementUpdate(BaseModel):
    expected_end_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    outcome: Optional[PlacementOutcome] = None
    placement_notes: Optional[str] = None
    return_reason: Optional[str] = None
    success_notes: Optional[str] = None
    agreement_signed: Optional[bool] = None
    agreement_signed_date: Optional[datetime] = None


class FosterPlacement(FosterPlacementBase):
    id: int
    org_id: int
    start_date: datetime
    actual_end_date: Optional[datetime]
    outcome: PlacementOutcome
    return_reason: Optional[str]
    success_notes: Optional[str]
    agreement_signed: bool
    agreement_signed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    pet_name: Optional[str] = None
    pet_species: Optional[str] = None

    class Config:
        orm_mode = True


class FosterMatch(BaseModel):
    """Represents a suggested foster match from the matching algorithm"""
    pet_id: int
    pet_name: str
    pet_species: str
    pet_status: str
    foster_user_id: int
    foster_name: str
    foster_email: str
    match_score: float
    match_reasons: List[str]
    current_foster_load: int
    max_capacity: int


class FosterCoordinatorStats(BaseModel):
    """Statistics for the foster coordinator dashboard"""
    total_active_fosters: int
    total_available_fosters: int
    pets_needing_foster: int
    pets_in_foster: int
    avg_placement_duration_days: Optional[float]
    recent_placements: List[FosterPlacement]
    available_foster_capacity: int


class FosterPlacementNoteBase(BaseModel):
    note_type: str = "progress"
    note_text: str
    is_important: bool = False


class FosterPlacementNoteCreate(FosterPlacementNoteBase):
    placement_id: int


class FosterPlacementNote(FosterPlacementNoteBase):
    id: int
    placement_id: int
    org_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PortalSummary(BaseModel):
    my_applications: List[Application] = []
    my_foster_pets: List[Pet] = []
    my_tasks: List[Task] = []


class PersonBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

    # Address
    street_1: Optional[str] = Field(None, max_length=200)
    street_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)

    # Adopter Tags
    tag_adopter: bool = False
    tag_potential_adopter: bool = False
    tag_adopt_waitlist: bool = False
    tag_do_not_adopt: bool = False

    # Foster Tags
    tag_foster: bool = False
    tag_available_foster: bool = False
    tag_current_foster: bool = False
    tag_dormant_foster: bool = False
    tag_foster_waitlist: bool = False
    tag_do_not_foster: bool = False

    # Volunteer Tags
    tag_volunteer: bool = False
    tag_do_not_volunteer: bool = False

    # Misc Tags
    tag_donor: bool = False
    tag_board_member: bool = False
    tag_has_dogs: bool = False
    tag_has_cats: bool = False
    tag_has_kids: bool = False
    tag_processing_application: bool = False
    tag_owner_surrender: bool = False

    user_id: Optional[int] = None


class PersonCreate(PersonBase):
    org_id: int


class PersonUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None

    # Address
    street_1: Optional[str] = Field(None, max_length=200)
    street_2: Optional[str] = Field(None, max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)

    # Adopter Tags
    tag_adopter: Optional[bool] = None
    tag_potential_adopter: Optional[bool] = None
    tag_adopt_waitlist: Optional[bool] = None
    tag_do_not_adopt: Optional[bool] = None

    # Foster Tags
    tag_foster: Optional[bool] = None
    tag_available_foster: Optional[bool] = None
    tag_current_foster: Optional[bool] = None
    tag_dormant_foster: Optional[bool] = None
    tag_foster_waitlist: Optional[bool] = None
    tag_do_not_foster: Optional[bool] = None

    # Volunteer Tags
    tag_volunteer: Optional[bool] = None
    tag_do_not_volunteer: Optional[bool] = None

    # Misc Tags
    tag_donor: Optional[bool] = None
    tag_board_member: Optional[bool] = None
    tag_has_dogs: Optional[bool] = None
    tag_has_cats: Optional[bool] = None
    tag_has_kids: Optional[bool] = None
    tag_processing_application: Optional[bool] = None
    tag_owner_surrender: Optional[bool] = None

    user_id: Optional[int] = None


class Person(PersonBase):
    id: int
    org_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PersonNoteBase(BaseModel):
    note_text: str = Field(..., min_length=1)


class PersonNoteCreate(PersonNoteBase):
    person_id: int
    org_id: int


class PersonNote(PersonNoteBase):
    id: int
    org_id: int
    person_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
