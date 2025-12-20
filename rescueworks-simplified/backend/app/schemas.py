from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from .models import PetStatus, FosterExperienceLevel, PlacementOutcome, UserRole


# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.staff


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    org_id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


# Animal schemas
class AnimalBase(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age_years: Optional[int] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    color: Optional[str] = None
    microchip_number: Optional[str] = None
    medical_notes: Optional[str] = None
    behavioral_notes: Optional[str] = None
    description: Optional[str] = None
    internal_notes: Optional[str] = None


class AnimalCreate(AnimalBase):
    intake_date: Optional[date] = None
    photo_url: Optional[str] = None


class AnimalUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    breed: Optional[str] = None
    age_years: Optional[int] = None
    sex: Optional[str] = None
    weight: Optional[float] = None
    color: Optional[str] = None
    status: Optional[PetStatus] = None
    medical_notes: Optional[str] = None
    behavioral_notes: Optional[str] = None
    description: Optional[str] = None
    internal_notes: Optional[str] = None
    photo_url: Optional[str] = None


class Animal(AnimalBase):
    id: int
    org_id: int
    status: PetStatus
    intake_date: Optional[date]
    photo_url: Optional[str]
    foster_user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Foster Profile schemas
class FosterProfileBase(BaseModel):
    experience_level: FosterExperienceLevel = FosterExperienceLevel.none
    preferred_species: Optional[str] = None
    max_capacity: int = 1
    home_type: Optional[str] = None
    has_yard: bool = False
    has_other_pets: bool = False
    has_children: bool = False
    can_handle_medical: bool = False
    can_handle_behavioral: bool = False
    is_available: bool = True


class FosterProfileCreate(FosterProfileBase):
    pass


class FosterProfileUpdate(BaseModel):
    experience_level: Optional[FosterExperienceLevel] = None
    preferred_species: Optional[str] = None
    max_capacity: Optional[int] = None
    home_type: Optional[str] = None
    has_yard: Optional[bool] = None
    has_other_pets: Optional[bool] = None
    has_children: Optional[bool] = None
    can_handle_medical: Optional[bool] = None
    can_handle_behavioral: Optional[bool] = None
    is_available: Optional[bool] = None


class FosterProfile(FosterProfileBase):
    id: int
    user_id: int
    org_id: int
    current_capacity: int
    total_fosters: int
    successful_adoptions: int
    rating: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Foster Placement schemas
class FosterPlacementBase(BaseModel):
    animal_id: int
    foster_profile_id: int
    expected_end_date: Optional[datetime] = None
    placement_notes: Optional[str] = None


class FosterPlacementCreate(FosterPlacementBase):
    pass


class FosterPlacementUpdate(BaseModel):
    expected_end_date: Optional[datetime] = None
    placement_notes: Optional[str] = None
    outcome: Optional[PlacementOutcome] = None
    return_reason: Optional[str] = None


class FosterPlacement(FosterPlacementBase):
    id: int
    org_id: int
    start_date: datetime
    actual_end_date: Optional[datetime]
    outcome: PlacementOutcome
    return_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Care Update schemas
class CareUpdateBase(BaseModel):
    animal_id: int
    update_type: str = "general"
    update_text: str
    is_important: bool = False
    photo_url: Optional[str] = None


class CareUpdateCreate(CareUpdateBase):
    pass


class CareUpdate(CareUpdateBase):
    id: int
    org_id: int
    created_by_user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardStats(BaseModel):
    total_animals: int
    animals_in_intake: int
    animals_needs_foster: int
    animals_in_foster: int
    animals_available: int
    animals_adopted: int
    active_fosters: int
    available_foster_capacity: int
    recent_intakes: List[Animal]
    recent_placements: List[FosterPlacement]


# Matching schemas
class FosterMatch(BaseModel):
    animal_id: int
    animal_name: str
    foster_profile_id: int
    foster_name: str
    foster_email: str
    score: int
    reasons: List[str]

    class Config:
        from_attributes = True


# Report schemas
class ReportFilters(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[PetStatus] = None
    species: Optional[str] = None


class AnimalReport(BaseModel):
    total_count: int
    by_status: dict
    by_species: dict
    average_time_to_foster: Optional[float]
    average_time_to_adoption: Optional[float]


# System Config schemas
class SystemConfigBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None


class SystemConfigCreate(SystemConfigBase):
    pass


class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


class SystemConfig(SystemConfigBase):
    id: int
    org_id: int
    updated_at: datetime

    class Config:
        from_attributes = True
