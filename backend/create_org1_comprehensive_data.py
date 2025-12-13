"""
Comprehensive test data generation script for RescueWorks
Focused on Organization 1 with extensive data for analytics

Creates:
- 50+ pets with various statuses
- 30+ people (adopters, fosters, volunteers, donors)
- Foster profiles with default values for all fosters
- 20+ active and completed foster placements
- 15+ adoptions
- 30+ tasks
- 20+ expenses across categories
- 10+ events
- 30+ medical records
- 25+ appointments
- Payment records
- Application records

Run with: python create_org1_comprehensive_data.py
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app import models
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Sample data
DOG_NAMES = ["Max", "Buddy", "Charlie", "Cooper", "Rocky", "Duke", "Bear", "Zeus", "Jack", "Toby",
             "Oliver", "Tucker", "Buster", "Riley", "Murphy", "Bentley", "Milo", "Finn", "Leo", "Teddy",
             "Bailey", "Daisy", "Sadie", "Molly", "Maggie", "Sophie", "Abby", "Chloe", "Roxy", "Penny"]

CAT_NAMES = ["Luna", "Bella", "Simba", "Milo", "Lucy", "Oliver", "Chloe", "Shadow", "Smokey", "Tiger",
             "Whiskers", "Mittens", "Oreo", "Ginger", "Felix", "Nala", "Jasper", "Cleo", "Socks", "Patches",
             "Snowball", "Pumpkin", "Boots", "Misty", "Fluffy", "Sylvester", "Garfield", "Tom", "Duchess", "Marie"]

DOG_BREEDS = ["Labrador Retriever", "German Shepherd", "Golden Retriever", "French Bulldog", "Bulldog",
              "Beagle", "Poodle", "Rottweiler", "Boxer", "Australian Shepherd", "Siberian Husky", "Great Dane",
              "Doberman Pinscher", "Chihuahua", "Corgi", "Border Collie", "Pitbull", "Dachshund", "Cocker Spaniel"]

CAT_BREEDS = ["Domestic Shorthair", "Domestic Longhair", "Siamese", "Persian", "Maine Coon",
              "Ragdoll", "Bengal", "Abyssinian", "American Shorthair", "Russian Blue", "British Shorthair"]

COLORS = ["Black", "White", "Brown", "Golden", "Gray", "Orange", "Tan", "Black and White",
          "Brown and White", "Tricolor", "Brindle", "Cream", "Silver", "Chocolate"]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen", "Daniel", "Nancy", "Matthew", "Lisa", "Anthony", "Betty"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
              "Taylor", "Moore", "Jackson", "Martin", "Lee", "White", "Harris", "Clark", "Lewis"]

CITIES = ["Portland", "Eugene", "Salem", "Bend", "Corvallis", "Medford", "Springfield", "Hillsboro"]
STATES = ["OR"] * 8

EXPENSE_CATEGORIES = ["Medical", "Food & Supplies", "Facility", "Marketing", "Administrative", "Transport", "Events"]

TASK_TITLES = [
    "Schedule vet appointment for {pet}",
    "Update website with new adoptable pets",
    "Follow up with foster applicant",
    "Prepare adoption paperwork",
    "Post social media updates",
    "Order pet food supplies",
    "Clean and organize kennels",
    "Call veterinary references",
    "Process adoption application",
    "Schedule home visit",
]


def create_comprehensive_org1_data():
    """Create comprehensive test data for Organization 1"""

    db = SessionLocal()

    try:
        print("=" * 60)
        print("Creating comprehensive test data for Organization 1")
        print("=" * 60)

        # Get Organization 1
        org1 = db.query(models.Organization).filter(models.Organization.id == 1).first()
        if not org1:
            print("ERROR: Organization 1 not found. Creating it now...")
            org1 = models.Organization(
                id=1,
                name="Happy Paws Rescue",
                logo_url="https://example.com/logos/org1.png",
                primary_contact_email="contact@happypawsrescue.org"
            )
            db.add(org1)
            db.commit()
            db.refresh(org1)

        # Clear existing data for org 1
        print("\n0. Clearing existing org 1 data...")
        db.query(models.FosterPlacementNote).filter(
            models.FosterPlacementNote.placement_id.in_(
                db.query(models.FosterPlacement.id).join(models.Pet).filter(models.Pet.org_id == 1)
            )
        ).delete(synchronize_session=False)

        db.query(models.FosterPlacement).filter(
            models.FosterPlacement.pet_id.in_(
                db.query(models.Pet.id).filter(models.Pet.org_id == 1)
            )
        ).delete(synchronize_session=False)

        db.query(models.FosterProfile).filter(
            models.FosterProfile.person_id.in_(
                db.query(models.Person.id).filter(models.Person.org_id == 1)
            )
        ).delete(synchronize_session=False)

        db.query(models.MedicalRecord).filter(
            models.MedicalRecord.pet_id.in_(
                db.query(models.Pet.id).filter(models.Pet.org_id == 1)
            )
        ).delete(synchronize_session=False)

        db.query(models.Appointment).filter(models.Appointment.org_id == 1).delete(synchronize_session=False)
        db.query(models.Task).filter(models.Task.org_id == 1).delete(synchronize_session=False)
        db.query(models.Expense).filter(models.Expense.org_id == 1).delete(synchronize_session=False)
        db.query(models.Payment).filter(models.Payment.org_id == 1).delete(synchronize_session=False)
        db.query(models.Application).filter(models.Application.org_id == 1).delete(synchronize_session=False)
        db.query(models.Event).filter(models.Event.org_id == 1).delete(synchronize_session=False)
        db.query(models.PersonNote).filter(
            models.PersonNote.person_id.in_(
                db.query(models.Person.id).filter(models.Person.org_id == 1)
            )
        ).delete(synchronize_session=False)
        db.query(models.Person).filter(models.Person.org_id == 1).delete(synchronize_session=False)
        db.query(models.Pet).filter(models.Pet.org_id == 1).delete(synchronize_session=False)

        db.commit()
        print("   ✓ Cleared existing org 1 data")

        # 1. Create 30 People (adopters, fosters, volunteers, donors)
        print("\n1. Creating 30 people with various tags...")
        people = []

        for i in range(30):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)

            # Distribute tags
            is_foster = i < 15  # First 15 are fosters
            is_adopter = 10 <= i < 25  # 15 adopters
            is_volunteer = i % 3 == 0  # Every 3rd person
            is_donor = i % 5 == 0  # Every 5th person

            person = models.Person(
                org_id=1,
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}{i}@example.com",
                phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                street_1=f"{random.randint(100,9999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine', 'Cedar'])} St",
                city=random.choice(CITIES),
                state=random.choice(STATES),
                zip_code=f"{random.randint(97000,97999)}",
                country="USA",
                tag_foster=is_foster,
                tag_current_foster=is_foster and i < 8,  # 8 current fosters
                tag_available_foster=is_foster and 8 <= i < 15,  # 7 available fosters
                tag_adopter=is_adopter,
                tag_potential_adopter=not is_adopter and i >= 25,
                tag_volunteer=is_volunteer,
                tag_donor=is_donor,
            )
            db.add(person)
            db.commit()
            db.refresh(person)
            people.append(person)

            tags = []
            if is_foster:
                tags.append("Foster")
            if is_adopter:
                tags.append("Adopter")
            if is_volunteer:
                tags.append("Volunteer")
            if is_donor:
                tags.append("Donor")

            print(f"   ✓ Created person: {first_name} {last_name} ({', '.join(tags)})")

        # 2. Create Foster Profiles for all fosters with default values
        print("\n2. Creating foster profiles with default values...")
        foster_profiles = []

        for person in people[:15]:  # First 15 are fosters
            profile = models.FosterProfile(
                org_id=1,
                person_id=person.id,
                experience_level=models.FosterExperienceLevel.beginner,
                max_capacity=1,
                current_capacity=0,
                home_type=models.HomeType.house,
                has_yard=True,
                can_handle_medical=True,
                can_handle_behavioral=True,
                is_active=True,
                preferred_species="",
                preferred_age_ranges="",
                notes="Default foster profile created automatically"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            foster_profiles.append(profile)
            print(f"   ✓ Created foster profile for {person.first_name} {person.last_name}")

        # 3. Create 60 Pets with various statuses
        print("\n3. Creating 60 pets with various statuses...")
        pets = []
        statuses = [
            models.PetStatus.intake,
            models.PetStatus.needs_foster,
            models.PetStatus.in_foster,
            models.PetStatus.available,
            models.PetStatus.pending,
            models.PetStatus.adopted,
            models.PetStatus.medical_hold
        ]

        for i in range(60):
            is_dog = i % 2 == 0
            species = "Dog" if is_dog else "Cat"
            name = random.choice(DOG_NAMES if is_dog else CAT_NAMES)
            breed = random.choice(DOG_BREEDS if is_dog else CAT_BREEDS)
            sex = random.choice(["Male", "Female"])
            status = statuses[i % len(statuses)]

            # Intake date within last 6 months
            intake_date = datetime.now() - timedelta(days=random.randint(1, 180))

            pet = models.Pet(
                org_id=1,
                name=name,
                species=species,
                breed=breed,
                sex=sex,
                status=status,
                intake_date=intake_date.date(),
                weight=random.uniform(5, 80) if is_dog else random.uniform(5, 20),
                altered_status=random.choice([models.AlteredStatus.yes, models.AlteredStatus.no, models.AlteredStatus.unsure]),
                color=random.choice(COLORS),
                adoption_fee=random.choice([50, 75, 100, 125, 150, 200]),
                description_public=f"{name} is a wonderful {sex.lower()} {species.lower()} looking for a loving home!",
                description_internal=f"Good temperament, house trained, good with {random.choice(['kids', 'other pets', 'everyone'])}",
                photo_url=f"https://placekitten.com/400/400" if not is_dog else f"https://placedog.net/400/400"
            )

            # Assign foster if in_foster status
            if status == models.PetStatus.in_foster and len(foster_profiles) > 0:
                foster = random.choice(foster_profiles[:8])  # Current fosters
                pet.foster_user_id = foster.person_id

            # Assign adopter if adopted or pending
            if status in [models.PetStatus.adopted, models.PetStatus.pending] and len([p for p in people if p.tag_adopter]) > 0:
                adopter = random.choice([p for p in people if p.tag_adopter])
                pet.adopter_user_id = adopter.id

            db.add(pet)
            db.commit()
            db.refresh(pet)
            pets.append(pet)
            print(f"   ✓ Created pet: {name} ({species}, {status.value})")

        # 4. Create Foster Placements
        print("\n4. Creating 25 foster placements (active and completed)...")
        placements = []

        for i in range(25):
            pet = random.choice([p for p in pets if p.species in ["Dog", "Cat"]])
            foster_profile = random.choice(foster_profiles)

            # Mix of active and completed placements
            is_active = i < 10

            start_date = datetime.now() - timedelta(days=random.randint(30, 180))

            placement = models.FosterPlacement(
                org_id=1,
                pet_id=pet.id,
                foster_profile_id=foster_profile.id,
                start_date=start_date.date(),
                expected_end_date=(start_date + timedelta(days=60)).date() if is_active else None,
                actual_end_date=None if is_active else (start_date + timedelta(days=random.randint(30, 90))).date(),
                outcome=models.PlacementOutcome.active if is_active else random.choice([
                    models.PlacementOutcome.adopted,
                    models.PlacementOutcome.returned,
                ]),
                notes=f"Foster placement for {pet.name}"
            )
            db.add(placement)
            db.commit()
            db.refresh(placement)
            placements.append(placement)

            # Add some placement notes
            for j in range(random.randint(1, 3)):
                note = models.FosterPlacementNote(
                    placement_id=placement.id,
                    note_type=random.choice([models.NoteType.progress, models.NoteType.health, models.NoteType.behavior]),
                    note_text=f"Update #{j+1}: Doing well, eating normally, playing with toys",
                    created_at=start_date + timedelta(days=random.randint(1, 30))
                )
                db.add(note)

            db.commit()
            print(f"   ✓ Created placement: {pet.name} with {foster_profile.person.first_name} {foster_profile.person.last_name} ({placement.outcome.value})")

        # 5. Create Tasks
        print("\n5. Creating 40 tasks...")
        priorities = [models.Priority.low, models.Priority.medium, models.Priority.high, models.Priority.urgent]
        task_statuses = [models.TaskStatus.pending, models.TaskStatus.in_progress, models.TaskStatus.completed]

        for i in range(40):
            pet = random.choice(pets) if i % 2 == 0 else None

            task = models.Task(
                org_id=1,
                title=random.choice(TASK_TITLES).format(pet=pet.name if pet else "pets"),
                description=f"Task description for task {i+1}",
                priority=random.choice(priorities),
                status=random.choice(task_statuses),
                due_date=(datetime.now() + timedelta(days=random.randint(-10, 30))).date(),
                pet_id=pet.id if pet else None,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.add(task)

        db.commit()
        print("   ✓ Created 40 tasks")

        # 6. Create Expenses
        print("\n6. Creating 30 expenses across categories...")

        for i in range(30):
            expense = models.Expense(
                org_id=1,
                category=random.choice(EXPENSE_CATEGORIES),
                amount=random.uniform(25, 500),
                description=f"Expense for {random.choice(EXPENSE_CATEGORIES).lower()}",
                expense_date=(datetime.now() - timedelta(days=random.randint(1, 180))).date(),
                pet_id=random.choice(pets).id if i % 3 == 0 else None
            )
            db.add(expense)

        db.commit()
        print("   ✓ Created 30 expenses")

        # 7. Create Medical Records
        print("\n7. Creating 40 medical records...")

        for i in range(40):
            pet = random.choice(pets)
            medical = models.MedicalRecord(
                pet_id=pet.id,
                record_type=random.choice(["Vaccination", "Checkup", "Surgery", "Treatment", "Lab Work"]),
                description=f"Medical record for {pet.name}",
                vet_name=f"Dr. {random.choice(LAST_NAMES)}",
                cost=random.uniform(50, 500),
                record_date=(datetime.now() - timedelta(days=random.randint(1, 180))).date()
            )
            db.add(medical)

        db.commit()
        print("   ✓ Created 40 medical records")

        # 8. Create Appointments
        print("\n8. Creating 30 appointments...")

        for i in range(30):
            pet = random.choice(pets)
            appointment = models.Appointment(
                org_id=1,
                title=f"Vet appointment for {pet.name}",
                description=f"Annual checkup and vaccinations",
                appointment_type=random.choice(["vet", "adoption_meetup", "home_visit", "event"]),
                start_time=datetime.now() + timedelta(days=random.randint(-30, 60), hours=random.randint(8, 17)),
                end_time=datetime.now() + timedelta(days=random.randint(-30, 60), hours=random.randint(9, 18)),
                pet_id=pet.id if i % 2 == 0 else None
            )
            db.add(appointment)

        db.commit()
        print("   ✓ Created 30 appointments")

        # 9. Create Events
        print("\n9. Creating 10 events...")

        for i in range(10):
            event = models.Event(
                org_id=1,
                title=f"Adoption Event #{i+1}",
                description="Come meet our adoptable pets!",
                event_type=random.choice(["adoption_event", "fundraiser", "volunteer_training"]),
                start_time=datetime.now() + timedelta(days=random.randint(1, 60)),
                end_time=datetime.now() + timedelta(days=random.randint(1, 60), hours=4),
                location=f"{random.choice(CITIES)}, OR",
                max_attendees=random.choice([20, 30, 50, 100])
            )
            db.add(event)

        db.commit()
        print("   ✓ Created 10 events")

        # 10. Create Applications
        print("\n10. Creating 25 applications...")

        for i in range(25):
            person = random.choice(people)
            pet = random.choice(pets) if i % 2 == 0 else None

            application = models.Application(
                org_id=1,
                person_id=person.id,
                pet_id=pet.id if pet else None,
                type=random.choice([models.ApplicationType.adoption, models.ApplicationType.foster, models.ApplicationType.volunteer]),
                status=random.choice(["pending", "approved", "rejected", "in_review"]),
                submitted_at=datetime.now() - timedelta(days=random.randint(1, 60))
            )
            db.add(application)

        db.commit()
        print("   ✓ Created 25 applications")

        # 11. Create Payments (donations and adoption fees)
        print("\n11. Creating 20 payments...")

        for i in range(20):
            person = random.choice(people)

            payment = models.Payment(
                org_id=1,
                person_id=person.id,
                amount=random.uniform(25, 500),
                payment_type=random.choice(["adoption_fee", "donation", "event_fee"]),
                status="completed",
                payment_date=datetime.now() - timedelta(days=random.randint(1, 180))
            )
            db.add(payment)

        db.commit()
        print("   ✓ Created 20 payments")

        print("\n" + "=" * 60)
        print("✅ Successfully created comprehensive test data for Organization 1!")
        print("=" * 60)
        print("\nSummary:")
        print(f"  • 30 People (15 fosters, 15 adopters, volunteers, donors)")
        print(f"  • 15 Foster Profiles (all with default values)")
        print(f"  • 60 Pets (various statuses)")
        print(f"  • 25 Foster Placements (10 active, 15 completed)")
        print(f"  • 40 Tasks")
        print(f"  • 30 Expenses")
        print(f"  • 40 Medical Records")
        print(f"  • 30 Appointments")
        print(f"  • 10 Events")
        print(f"  • 25 Applications")
        print(f"  • 20 Payments")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_comprehensive_org1_data()
