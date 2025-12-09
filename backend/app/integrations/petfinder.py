"""
Petfinder API client stubs.

Use official Petfinder API docs to implement real calls and map
from internal Pet model to Petfinder listing format.
"""


def publish_pet(pet_id: int) -> None:
    # TODO: fetch pet from database and push to Petfinder
    print(f"[PETFINDER] publish pet {pet_id}")


def remove_pet(pet_id: int) -> None:
    # TODO: tell Petfinder to archive or remove the pet listing
    print(f"[PETFINDER] remove pet {pet_id}")
