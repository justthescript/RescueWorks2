from datetime import datetime
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


class PetBase(BaseModel):
    name: str = Field(
        ..., min_length=1, max_length=100, description="Pet name (required)"
    )
    species: str = Field(
        ..., min_length=1, max_length=50, description="Species (e.g., Dog, Cat, Bird)"
    )
    breed: Optional[str] = Field(None, max_length=100, description="Breed or mix")
    sex: Optional[str] = Field(None, description="Sex of the animal")
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
    org_id: int


class PetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    species: Optional[str] = Field(None, min_length=1, max_length=50)
    breed: Optional[str] = Field(None, max_length=100)
    sex: Optional[str] = None
    status: Optional[PetStatus] = None
    description_public: Optional[str] = Field(None, max_length=2000)
    description_internal: Optional[str] = Field(None, max_length=2000)
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
    org_id: int
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


class PortalSummary(BaseModel):
    my_applications: List[Application] = []
    my_foster_pets: List[Pet] = []
    my_tasks: List[Task] = []
