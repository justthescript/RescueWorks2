import pytest
from app import models


def test_create_pet(client, auth_headers, test_org):
    """Test creating a new pet."""
    pet_data = {
        "name": "Max",
        "species": "Dog",
        "breed": "Labrador",
        "sex": "Male",
        "org_id": test_org.id,
        "status": "intake",
        "description_public": "A lovable lab",
        "description_internal": "Found on 1st street",
    }

    response = client.post("/pets/", json=pet_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Max"
    assert data["species"] == "Dog"
    assert data["breed"] == "Labrador"
    assert data["sex"] == "Male"
    assert data["status"] == "intake"


def test_create_pet_with_validation(client, auth_headers, test_org):
    """Test pet creation validation."""
    # Test with invalid sex
    pet_data = {
        "name": "Fluffy",
        "species": "Cat",
        "sex": "InvalidSex",
        "org_id": test_org.id,
    }

    response = client.post("/pets/", json=pet_data, headers=auth_headers)
    assert response.status_code == 422


def test_create_pet_name_too_long(client, auth_headers, test_org):
    """Test pet name validation - max length."""
    pet_data = {
        "name": "A" * 101,  # Exceeds max length of 100
        "species": "Dog",
        "org_id": test_org.id,
    }

    response = client.post("/pets/", json=pet_data, headers=auth_headers)
    assert response.status_code == 422


def test_create_pet_missing_required_fields(client, auth_headers, test_org):
    """Test pet creation with missing required fields."""
    pet_data = {
        "org_id": test_org.id
        # Missing name and species
    }

    response = client.post("/pets/", json=pet_data, headers=auth_headers)
    assert response.status_code == 422


def test_list_pets(client, auth_headers, test_pet):
    """Test listing pets."""
    response = client.get("/pets/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(pet["id"] == test_pet.id for pet in data)


def test_get_pet(client, auth_headers, test_pet):
    """Test getting a specific pet."""
    response = client.get(f"/pets/{test_pet.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_pet.id
    assert data["name"] == test_pet.name


def test_get_nonexistent_pet(client, auth_headers):
    """Test getting a pet that doesn't exist."""
    response = client.get("/pets/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_pet(client, auth_headers, test_pet):
    """Test updating a pet."""
    update_data = {"name": "Buddy Updated", "status": "available"}

    response = client.patch(
        f"/pets/{test_pet.id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Buddy Updated"
    assert data["status"] == "available"


def test_assign_foster(client, auth_headers, test_pet, test_user):
    """Test assigning a foster to a pet."""
    assignment_data = {"foster_user_id": test_user.id}

    response = client.post(
        f"/pets/{test_pet.id}/assign-foster", json=assignment_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["foster_user_id"] == test_user.id
    assert data["status"] == "in_foster"


def test_assign_foster_invalid_user(client, auth_headers, test_pet):
    """Test assigning an invalid foster user."""
    assignment_data = {"foster_user_id": 99999}  # Non-existent user

    response = client.post(
        f"/pets/{test_pet.id}/assign-foster", json=assignment_data, headers=auth_headers
    )

    assert response.status_code == 400


def test_assign_foster_inactive_user(client, auth_headers, test_pet, test_user, db):
    """Test assigning an inactive foster user."""
    # Make user inactive
    test_user.is_active = False
    db.commit()

    assignment_data = {"foster_user_id": test_user.id}

    response = client.post(
        f"/pets/{test_pet.id}/assign-foster", json=assignment_data, headers=auth_headers
    )

    assert response.status_code == 400
    assert "inactive" in response.json()["detail"].lower()


def test_unassign_foster(client, auth_headers, test_pet, test_user, db):
    """Test unassigning a foster from a pet."""
    # First assign the foster
    test_pet.foster_user_id = test_user.id
    test_pet.status = "in_foster"
    db.commit()

    # Now unassign
    response = client.delete(f"/pets/{test_pet.id}/assign-foster", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["foster_user_id"] is None
    assert data["status"] == "needs_foster"


def test_unauthorized_access(client, test_pet):
    """Test accessing pets without authentication."""
    response = client.get("/pets/")
    assert response.status_code == 401
