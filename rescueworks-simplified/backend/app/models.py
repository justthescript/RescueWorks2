import enum
from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base


# Enums
class PetStatus(str, enum.Enum):
    intake = "intake"
    needs_foster = "needs_foster"
    in_foster = "in_foster"
    available = "available"
    adopted = "adopted"
    medical_hold = "medical_hold"


class FosterExperienceLevel(str, enum.Enum):
    none = "none"
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class PlacementOutcome(str, enum.Enum):
    active = "active"
    adopted = "adopted"
    returned = "returned"


class UserRole(str, enum.Enum):
    admin = "admin"
    coordinator = "coordinator"
    foster = "foster"
    staff = "staff"


# Models
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    animals = relationship("Animal", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.staff)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")
    foster_profile = relationship("FosterProfile", back_populates="user", uselist=False)
    care_updates = relationship("CareUpdate", back_populates="created_by")


class Animal(Base):
    __tablename__ = "animals"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    breed = Column(String)
    age_years = Column(Integer)
    sex = Column(String)
    weight = Column(Float)
    color = Column(String)

    # Intake information
    intake_date = Column(Date)
    microchip_number = Column(String)
    medical_notes = Column(Text)
    behavioral_notes = Column(Text)

    # Status and placement
    status = Column(Enum(PetStatus), default=PetStatus.intake)
    photo_url = Column(String)
    foster_user_id = Column(Integer, ForeignKey("users.id"))

    # Public and internal descriptions
    description = Column(Text)
    internal_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="animals")
    foster = relationship("User", foreign_keys=[foster_user_id])
    placements = relationship("FosterPlacement", back_populates="animal")
    care_updates = relationship("CareUpdate", back_populates="animal")


class FosterProfile(Base):
    __tablename__ = "foster_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)

    # Experience and preferences
    experience_level = Column(Enum(FosterExperienceLevel), default=FosterExperienceLevel.none)
    preferred_species = Column(String)  # Comma-separated
    max_capacity = Column(Integer, default=1)
    current_capacity = Column(Integer, default=0)

    # Home information
    home_type = Column(String)
    has_yard = Column(Boolean, default=False)
    has_other_pets = Column(Boolean, default=False)
    has_children = Column(Boolean, default=False)

    # Capabilities
    can_handle_medical = Column(Boolean, default=False)
    can_handle_behavioral = Column(Boolean, default=False)

    # Availability
    is_available = Column(Boolean, default=True)

    # Performance metrics
    total_fosters = Column(Integer, default=0)
    successful_adoptions = Column(Integer, default=0)
    rating = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="foster_profile")
    placements = relationship("FosterPlacement", back_populates="foster_profile")


class FosterPlacement(Base):
    __tablename__ = "foster_placements"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    foster_profile_id = Column(Integer, ForeignKey("foster_profiles.id"), nullable=False)

    start_date = Column(DateTime, default=datetime.utcnow)
    expected_end_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    outcome = Column(Enum(PlacementOutcome), default=PlacementOutcome.active)

    placement_notes = Column(Text)
    return_reason = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    foster_profile = relationship("FosterProfile", back_populates="placements")
    animal = relationship("Animal", back_populates="placements")


class CareUpdate(Base):
    __tablename__ = "care_updates"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    animal_id = Column(Integer, ForeignKey("animals.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    update_type = Column(String, default="general")  # general, medical, behavioral, photo
    update_text = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False)
    photo_url = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    animal = relationship("Animal", back_populates="care_updates")
    created_by = relationship("User", back_populates="care_updates")


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    key = Column(String, nullable=False, unique=True)
    value = Column(Text)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
