from sqlalchemy.orm import Session

from .. import models


def publish_pet_to_petfinder(
    db: Session, pet: models.Pet, settings: models.OrganizationSettings
):
    # Placeholder for real Petfinder API call
    # You would use settings.petfinder_api_key and settings.petfinder_secret here.
    print(f"[petfinder] publish pet {pet.id} - {pet.name} for org {pet.org_id}")


def remove_pet_from_petfinder(
    db: Session, pet: models.Pet, settings: models.OrganizationSettings
):
    print(f"[petfinder] remove pet {pet.id} - {pet.name} for org {pet.org_id}")
