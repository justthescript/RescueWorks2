#!/usr/bin/env python3
"""
Script to populate the database with test data
Creates 20 test entries each for pets, people, appointments, and tasks
Also creates an admin user: nateweaver94@gmail.com
"""
import sys
import os
from datetime import datetime, timedelta
from random import choice, randint, uniform, sample

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.database import SessionLocal, engine
from app.models import (
    Base,
    Organization,
    User,
    Role,
    UserRole,
    Pet,
    Person,
    Appointment,
    Task,
    PetStatus,
    AlteredStatus,
    TaskStatus,
    TaskPriority,
)
from app.security import get_password_hash


# Test data generators
DOG_NAMES = [
    "Max", "Bella", "Charlie", "Luna", "Cooper", "Daisy", "Rocky", "Sadie",
    "Duke", "Molly", "Bear", "Maggie", "Jack", "Lucy", "Oliver", "Sophie",
    "Tucker", "Penny", "Buddy", "Stella", "Zeus", "Chloe", "Milo", "Zoe"
]

CAT_NAMES = [
    "Whiskers", "Mittens", "Shadow", "Simba", "Felix", "Tigger", "Smokey", "Oliver",
    "Leo", "Cleo", "Luna", "Bella", "Milo", "Nala", "Ginger", "Oscar",
    "Boots", "Patches", "Oreo", "Princess", "Tiger", "Snowball", "Jasper", "Coco"
]

DOG_BREEDS = [
    "Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog",
    "Beagle", "Poodle", "Rottweiler", "Yorkshire Terrier", "Boxer", "Dachshund",
    "Siberian Husky", "Great Dane", "Doberman", "Shih Tzu", "Boston Terrier",
    "Chihuahua", "Pomeranian", "Maltese", "Border Collie", "Mixed Breed"
]

CAT_BREEDS = [
    "Domestic Shorthair", "Domestic Longhair", "Siamese", "Persian", "Maine Coon",
    "Ragdoll", "Bengal", "Abyssinian", "Birman", "Oriental Shorthair",
    "Sphynx", "Devon Rex", "British Shorthair", "Scottish Fold", "American Shorthair",
    "Exotic Shorthair", "Himalayan", "Burmese", "Russian Blue", "Mixed Breed"
]

FIRST_NAMES = [
    "Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason",
    "Isabella", "William", "Mia", "James", "Charlotte", "Benjamin", "Amelia",
    "Lucas", "Harper", "Henry", "Evelyn", "Alexander", "Emily", "Michael",
    "Abigail", "Daniel", "Elizabeth", "Matthew", "Sofia", "Jackson", "Avery"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White"
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
    "Denver", "Washington"
]

STATES = [
    "NY", "CA", "IL", "TX", "AZ", "PA", "FL", "OH", "NC", "WA", "CO", "DC"
]

APPOINTMENT_TYPES = [
    "Veterinary Checkup", "Vaccination", "Spay/Neuter", "Dental Cleaning",
    "Follow-up Visit", "Emergency Visit", "Grooming", "Behavior Consultation",
    "Surgery", "X-Ray", "Blood Work", "Adoption Meet & Greet"
]

TASK_TITLES = [
    "Schedule vet appointment for {pet}",
    "Follow up with {person} about adoption",
    "Update medical records for {pet}",
    "Process adoption application",
    "Schedule home visit for {person}",
    "Order supplies for shelter",
    "Update website with new pets",
    "Call references for {person}",
    "Post {pet} on social media",
    "Prepare adoption paperwork for {pet}",
    "Schedule spay/neuter for {pet}",
    "Send thank you note to {person}",
    "Update foster care information",
    "Review applications for {pet}",
    "Coordinate transport for {pet}",
    "Schedule training session",
    "Update donor database",
    "Prepare newsletter content",
    "Review volunteer applications",
    "Schedule fundraising event"
]


def create_admin_user(db, org_id):
    """Create admin user with full access"""
    print("Creating admin user...")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "nateweaver94@gmail.com").first()
    if existing_user:
        print("  Admin user already exists!")
        return existing_user

    # Create admin user
    admin = User(
        org_id=org_id,
        email="nateweaver94@gmail.com",
        full_name="Nate Weaver",
        phone="555-0100",
        hashed_password=get_password_hash("admin123"),  # Default password
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    # Create or get admin role
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(
            name="admin",
            description="Full system access"
        )
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    # Assign admin role to user
    user_role = UserRole(
        user_id=admin.id,
        role_id=admin_role.id
    )
    db.add(user_role)
    db.commit()

    print(f"  Created admin user: {admin.email} (password: admin123)")
    return admin


def create_test_pets(db, org_id, count=20):
    """Create test pets"""
    print(f"Creating {count} test pets...")
    pets = []

    for i in range(count):
        species = choice(["Dog", "Cat"])
        if species == "Dog":
            name = choice(DOG_NAMES)
            breed = choice(DOG_BREEDS)
        else:
            name = choice(CAT_NAMES)
            breed = choice(CAT_BREEDS)

        # Ensure unique names by appending number if needed
        name = f"{name} {i+1}"

        pet = Pet(
            org_id=org_id,
            name=name,
            species=species,
            breed=breed,
            sex=choice(["Male", "Female"]),
            intake_date=datetime.now() - timedelta(days=randint(1, 365)),
            microchip_number=f"MC{randint(100000000, 999999999)}",
            weight=uniform(5.0, 100.0),
            altered_status=choice([AlteredStatus.yes, AlteredStatus.no, AlteredStatus.unsure]),
            date_of_birth=datetime.now() - timedelta(days=randint(365, 3650)),
            status=choice([PetStatus.intake, PetStatus.available, PetStatus.in_foster, PetStatus.pending]),
            description_public=f"Meet {name}! A lovely {species.lower()} looking for a forever home.",
            description_internal=f"Intake notes: Good temperament, friendly with people.",
        )
        db.add(pet)
        pets.append(pet)

    db.commit()
    print(f"  Created {count} pets")
    return pets


def create_test_people(db, org_id, count=20):
    """Create test people"""
    print(f"Creating {count} test people...")
    people = []

    for i in range(count):
        first_name = choice(FIRST_NAMES)
        last_name = choice(LAST_NAMES)

        person = Person(
            org_id=org_id,
            first_name=first_name,
            last_name=last_name,
            phone=f"555-{randint(1000, 9999)}",
            email=f"{first_name.lower()}.{last_name.lower()}{i}@example.com",
            street_1=f"{randint(100, 9999)} Main St",
            city=choice(CITIES),
            state=choice(STATES),
            zip_code=f"{randint(10000, 99999)}",
            country="USA",
            # Randomly assign tags
            tag_adopter=choice([True, False]),
            tag_potential_adopter=choice([True, False]),
            tag_foster=choice([True, False]),
            tag_volunteer=choice([True, False]),
            tag_donor=choice([True, False]),
            tag_has_dogs=choice([True, False]),
            tag_has_cats=choice([True, False]),
            tag_has_kids=choice([True, False]),
        )
        db.add(person)
        people.append(person)

    db.commit()
    print(f"  Created {count} people")
    return people


def create_test_appointments(db, org_id, pets, count=20):
    """Create test appointments"""
    print(f"Creating {count} test appointments...")
    appointments = []

    for i in range(count):
        # Some appointments have pets, some don't
        pet = choice(pets) if choice([True, False, True]) else None

        appointment = Appointment(
            org_id=org_id,
            pet_id=pet.id if pet else None,
            type=choice(APPOINTMENT_TYPES),
            date_time=datetime.now() + timedelta(days=randint(-30, 60)),
            location=choice(["Main Vet Clinic", "Mobile Clinic", "Emergency Vet", "Grooming Salon"]),
            notes=f"Appointment scheduled for routine care.",
        )
        db.add(appointment)
        appointments.append(appointment)

    db.commit()
    print(f"  Created {count} appointments")
    return appointments


def create_test_tasks(db, org_id, admin_user, pets, people, count=20):
    """Create test tasks"""
    print(f"Creating {count} test tasks...")
    tasks = []

    for i in range(count):
        # Pick a random task title template
        title_template = choice(TASK_TITLES)

        # Replace placeholders
        title = title_template
        if "{pet}" in title:
            pet = choice(pets)
            title = title.replace("{pet}", pet.name)
        if "{person}" in title:
            person = choice(people)
            title = title.replace("{person}", f"{person.first_name} {person.last_name}")

        # Pick a related pet for some tasks
        related_pet = choice(pets) if choice([True, False]) else None

        task = Task(
            org_id=org_id,
            title=title,
            description=f"Task details for: {title}",
            status=choice([TaskStatus.open, TaskStatus.in_progress, TaskStatus.completed]),
            priority=choice([TaskPriority.low, TaskPriority.normal, TaskPriority.high, TaskPriority.urgent]),
            due_date=datetime.now() + timedelta(days=randint(-10, 30)),
            created_by_user_id=admin_user.id,
            assigned_to_user_id=admin_user.id if choice([True, False]) else None,
            related_pet_id=related_pet.id if related_pet else None,
        )
        db.add(task)
        tasks.append(task)

    db.commit()
    print(f"  Created {count} tasks")
    return tasks


def main():
    print("Starting database population...")
    print("=" * 60)

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Create database session
    db = SessionLocal()

    try:
        # Get or create organization
        org = db.query(Organization).first()
        if not org:
            org = Organization(
                name="Test Rescue Organization",
                primary_contact_email="info@testrescue.org"
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created organization: {org.name}")
        else:
            print(f"Using existing organization: {org.name}")

        print("=" * 60)

        # Create admin user
        admin_user = create_admin_user(db, org.id)

        # Create test data
        pets = create_test_pets(db, org.id, 20)
        people = create_test_people(db, org.id, 20)
        appointments = create_test_appointments(db, org.id, pets, 20)
        tasks = create_test_tasks(db, org.id, admin_user, pets, people, 20)

        print("=" * 60)
        print("Database population completed successfully!")
        print("=" * 60)
        print(f"Created:")
        print(f"  - 1 admin user (nateweaver94@gmail.com)")
        print(f"  - {len(pets)} pets")
        print(f"  - {len(people)} people")
        print(f"  - {len(appointments)} appointments")
        print(f"  - {len(tasks)} tasks")
        print()
        print("Admin credentials:")
        print("  Email: nateweaver94@gmail.com")
        print("  Password: admin123")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
