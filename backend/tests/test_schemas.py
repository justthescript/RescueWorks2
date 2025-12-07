import pytest
from app import schemas
from pydantic import ValidationError


def test_pet_base_valid():
    """Test PetBase schema with valid data."""
    pet = schemas.PetBase(
        name="Buddy",
        species="Dog",
        breed="Golden Retriever",
        sex="Male",
        description_public="A friendly dog",
        description_internal="Healthy",
    )
    assert pet.name == "Buddy"
    assert pet.species == "Dog"
    assert pet.sex == "Male"


def test_pet_base_name_required():
    """Test that pet name is required."""
    with pytest.raises(ValidationError) as exc_info:
        schemas.PetBase(species="Dog")
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("name",) for error in errors)


def test_pet_base_species_required():
    """Test that pet species is required."""
    with pytest.raises(ValidationError) as exc_info:
        schemas.PetBase(name="Buddy")
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("species",) for error in errors)


def test_pet_base_name_max_length():
    """Test pet name max length validation."""
    with pytest.raises(ValidationError):
        schemas.PetBase(name="A" * 101, species="Dog")  # Exceeds max length of 100


def test_pet_base_species_max_length():
    """Test pet species max length validation."""
    with pytest.raises(ValidationError):
        schemas.PetBase(name="Buddy", species="A" * 51)  # Exceeds max length of 50


def test_pet_base_invalid_sex():
    """Test pet sex validation with invalid value."""
    with pytest.raises(ValidationError) as exc_info:
        schemas.PetBase(name="Buddy", species="Dog", sex="InvalidSex")
    errors = exc_info.value.errors()
    assert any("Sex must be one of" in str(error["msg"]) for error in errors)


def test_pet_base_valid_sex_values():
    """Test that all valid sex values are accepted."""
    valid_sexes = ["Male", "Female", "Unknown", "M", "F", "U"]

    for sex in valid_sexes:
        pet = schemas.PetBase(name="Buddy", species="Dog", sex=sex)
        assert pet.sex == sex


def test_pet_base_description_max_length():
    """Test description max length validation."""
    with pytest.raises(ValidationError):
        schemas.PetBase(
            name="Buddy",
            species="Dog",
            description_public="A" * 2001,  # Exceeds max length of 2000
        )


def test_pet_base_whitespace_stripping():
    """Test that whitespace is stripped from name and species."""
    pet = schemas.PetBase(name="  Buddy  ", species="  Dog  ")
    assert pet.name == "Buddy"
    assert pet.species == "Dog"


def test_pet_base_empty_string_validation():
    """Test that empty strings are rejected for required fields."""
    with pytest.raises(ValidationError):
        schemas.PetBase(name="   ", species="Dog")  # Only whitespace


def test_pet_create_schema():
    """Test PetCreate schema."""
    pet = schemas.PetCreate(name="Max", species="Cat", org_id=1)
    assert pet.org_id == 1
    assert pet.name == "Max"


def test_pet_update_schema():
    """Test PetUpdate schema allows partial updates."""
    update = schemas.PetUpdate(name="New Name")
    assert update.name == "New Name"
    assert update.species is None


def test_foster_assignment_schema():
    """Test FosterAssignment schema."""
    assignment = schemas.FosterAssignment(foster_user_id=123)
    assert assignment.foster_user_id == 123


def test_foster_assignment_missing_user_id():
    """Test FosterAssignment requires foster_user_id."""
    with pytest.raises(ValidationError):
        schemas.FosterAssignment()


def test_pet_status_enum():
    """Test PetStatus enum values."""
    assert schemas.PetStatus.intake == "intake"
    assert schemas.PetStatus.needs_foster == "needs_foster"
    assert schemas.PetStatus.in_foster == "in_foster"
    assert schemas.PetStatus.available == "available"
    assert schemas.PetStatus.pending == "pending"
    assert schemas.PetStatus.adopted == "adopted"
    assert schemas.PetStatus.medical_hold == "medical_hold"


def test_pet_base_with_all_fields():
    """Test PetBase with all optional fields populated."""
    pet = schemas.PetBase(
        name="Fluffy",
        species="Cat",
        breed="Persian",
        sex="Female",
        status=schemas.PetStatus.available,
        description_public="A beautiful cat",
        description_internal="Needs special diet",
        photo_url="https://example.com/fluffy.jpg",
        foster_user_id=1,
        adopter_user_id=2,
    )
    assert pet.name == "Fluffy"
    assert pet.breed == "Persian"
    assert pet.status == schemas.PetStatus.available
    assert pet.foster_user_id == 1
    assert pet.adopter_user_id == 2
