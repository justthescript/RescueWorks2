"""
Comprehensive test data generation script for RescueWorks
Creates:
- 10-20 organizations
- 10-20 users with roles for org 1
- 10-20 pets
- 10-20 foster profiles
- 10-20 people
- 5 test tasks

Run with: python create_comprehensive_test_data.py
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
             "Oliver", "Tucker", "Buster", "Riley", "Murphy", "Bentley", "Milo", "Finn", "Leo", "Teddy"]

CAT_NAMES = ["Luna", "Bella", "Simba", "Milo", "Lucy", "Oliver", "Chloe", "Shadow", "Smokey", "Tiger",
             "Whiskers", "Mittens", "Oreo", "Ginger", "Felix", "Nala", "Jasper", "Cleo", "Socks", "Patches"]

DOG_BREEDS = ["Labrador Retriever", "German Shepherd", "Golden Retriever", "French Bulldog", "Bulldog",
              "Beagle", "Poodle", "Rottweiler", "German Shorthaired Pointer", "Dachshund",
              "Boxer", "Australian Shepherd", "Siberian Husky", "Great Dane", "Doberman Pinscher"]

CAT_BREEDS = ["Domestic Shorthair", "Domestic Longhair", "Siamese", "Persian", "Maine Coon",
              "Ragdoll", "Bengal", "Abyssinian", "American Shorthair", "Russian Blue"]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
               "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
               "Thomas", "Sarah", "Charles", "Karen"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
              "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas",
              "Taylor", "Moore", "Jackson", "Martin", "Lee"]

CITIES = ["Portland", "Seattle", "San Francisco", "Los Angeles", "Phoenix", "Denver", "Austin",
          "Chicago", "New York", "Boston", "Miami", "Atlanta", "Dallas", "Houston", "Minneapolis"]

STATES = ["OR", "WA", "CA", "CA", "AZ", "CO", "TX", "IL", "NY", "MA", "FL", "GA", "TX", "TX", "MN"]

ORG_NAMES = [
    "Happy Paws Rescue",
    "Second Chance Animal Sanctuary",
    "Furry Friends Foster Network",
    "Rescue Rovers Foundation",
    "Pet Haven Alliance",
    "Compassionate Critters Rescue",
    "Animal Angels Adoption Center",
    "Four Legs and a Tail",
    "Whiskers and Wags",
    "New Beginnings Pet Rescue",
    "Forever Home Finders",
    "Pawsitive Impact Rescue",
    "Safe Harbor Animal Shelter",
    "Heartland Pet Rescue",
    "Coastal Companions Rescue",
    "Mountain View Animal Haven",
    "Urban Pet Rescue League",
    "Country Creatures Sanctuary",
    "City Paws Foster Care",
    "Prairie Dogs and Cats Rescue"
]

ROLE_NAMES = ["admin", "staff", "foster_coordinator", "volunteer", "vet"]


def create_comprehensive_test_data():
    """Create comprehensive test data for all entities"""

    db = SessionLocal()

    try:
        print("=" * 60)
        print("Creating comprehensive test data for RescueWorks")
        print("=" * 60)

        # 1. Create Roles (if they don't exist)
        print("\n1. Creating roles...")
        roles = {}
        for role_name in ROLE_NAMES:
            existing_role = db.query(models.Role).filter(models.Role.name == role_name).first()
            if not existing_role:
                role = models.Role(
                    name=role_name,
                    description=f"{role_name.replace('_', ' ').title()} role"
                )
                db.add(role)
                db.commit()
                db.refresh(role)
                roles[role_name] = role
                print(f"   ✓ Created role: {role_name}")
            else:
                roles[role_name] = existing_role
                print(f"   ✓ Role already exists: {role_name}")

        db.commit()

        # 2. Create Organizations
        print("\n2. Creating 15 organizations...")
        organizations = []
        for i in range(15):
            org_name = ORG_NAMES[i]

            # Check if org already exists
            existing_org = db.query(models.Organization).filter(
                models.Organization.name == org_name
            ).first()

            if not existing_org:
                org = models.Organization(
                    name=org_name,
                    logo_url=f"https://example.com/logos/org{i+1}.png",
                    primary_contact_email=f"contact@{org_name.lower().replace(' ', '')}.org"
                )
                db.add(org)
                db.commit()
                db.refresh(org)
                organizations.append(org)
                print(f"   ✓ Created organization: {org_name}")
            else:
                organizations.append(existing_org)
                print(f"   ✓ Organization already exists: {org_name}")

        # 3. Create 20 Users with roles for Organization 1
        print("\n3. Creating 20 users with roles for Organization 1...")
        org1 = organizations[0]
        users_org1 = []

        for i in range(20):
            email = f"user{i+1}@{org1.name.lower().replace(' ', '')}.org"

            # Check if user already exists
            existing_user = db.query(models.User).filter(models.User.email == email).first()

            if not existing_user:
                user = models.User(
                    org_id=org1.id,
                    email=email,
                    full_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                    phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                    hashed_password=hash_password("password123"),
                    is_active=True
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                # Assign random roles (1-3 roles per user)
                num_roles = random.randint(1, 3)
                assigned_roles = random.sample(list(roles.values()), num_roles)

                for role in assigned_roles:
                    user_role = models.UserRole(user_id=user.id, role_id=role.id)
                    db.add(user_role)

                db.commit()
                users_org1.append(user)
                role_names = [r.name for r in assigned_roles]
                print(f"   ✓ Created user: {user.full_name} ({email}) with roles: {', '.join(role_names)}")
            else:
                users_org1.append(existing_user)
                print(f"   ✓ User already exists: {email}")

        # 4. Create 20 Pets for Organization 1
        print("\n4. Creating 20 pets for Organization 1...")
        pets_org1 = []

        for i in range(20):
            is_dog = i % 2 == 0
            species = "dog" if is_dog else "cat"
            name = random.choice(DOG_NAMES if is_dog else CAT_NAMES)
            breed = random.choice(DOG_BREEDS if is_dog else CAT_BREEDS)
            sex = random.choice(["male", "female"])
            status = random.choice([
                models.PetStatus.intake,
                models.PetStatus.needs_foster,
                models.PetStatus.available,
                models.PetStatus.in_foster,
                models.PetStatus.pending
            ])

            pet = models.Pet(
                org_id=org1.id,
                name=name,
                species=species,
                breed=breed,
                sex=sex,
                intake_date=datetime.now() - timedelta(days=random.randint(1, 180)),
                microchip_number=f"MC{random.randint(100000000, 999999999)}",
                weight=random.uniform(5.0, 80.0) if is_dog else random.uniform(3.0, 20.0),
                altered_status=random.choice([models.AlteredStatus.yes, models.AlteredStatus.no, models.AlteredStatus.unsure]),
                date_of_birth=datetime.now() - timedelta(days=random.randint(180, 3650)),
                status=status,
                description_public=f"Meet {name}, a wonderful {breed}!",
                description_internal=f"Internal notes for {name}",
                photo_url=f"https://example.com/pets/{name.lower()}.jpg"
            )
            db.add(pet)
            db.commit()
            db.refresh(pet)
            pets_org1.append(pet)
            print(f"   ✓ Created pet: {name} ({species}, {breed}) - Status: {status.value}")

        # 5. Create 20 Foster Profiles for Organization 1
        print("\n5. Creating 20 foster profiles for Organization 1...")
        foster_profiles = []

        for i in range(20):
            # Create a new user for this foster if we need more
            if i < len(users_org1):
                foster_user = users_org1[i]
            else:
                email = f"foster{i+1}@{org1.name.lower().replace(' ', '')}.org"
                existing_user = db.query(models.User).filter(models.User.email == email).first()

                if not existing_user:
                    foster_user = models.User(
                        org_id=org1.id,
                        email=email,
                        full_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                        phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                        hashed_password=hash_password("password123"),
                        is_active=True
                    )
                    db.add(foster_user)
                    db.commit()
                    db.refresh(foster_user)
                else:
                    foster_user = existing_user

            # Check if foster profile already exists for this user
            existing_profile = db.query(models.FosterProfile).filter(
                models.FosterProfile.user_id == foster_user.id
            ).first()

            if not existing_profile:
                experience_level = random.choice([
                    models.FosterExperienceLevel.beginner,
                    models.FosterExperienceLevel.intermediate,
                    models.FosterExperienceLevel.advanced
                ])

                profile = models.FosterProfile(
                    user_id=foster_user.id,
                    org_id=org1.id,
                    experience_level=experience_level,
                    preferred_species="dog,cat",
                    preferred_ages="puppy,adult" if random.random() > 0.5 else "adult,senior",
                    max_capacity=random.randint(1, 5),
                    current_capacity=random.randint(0, 2),
                    home_type=random.choice([
                        models.HomeType.house,
                        models.HomeType.apartment,
                        models.HomeType.condo
                    ]),
                    has_yard=random.choice([True, False]),
                    has_other_pets=random.choice([True, False]),
                    other_pets_description="Friendly dog" if random.random() > 0.5 else None,
                    has_children=random.choice([True, False]),
                    children_ages="5,8" if random.random() > 0.5 else None,
                    can_handle_medical=random.choice([True, False]),
                    can_handle_behavioral=random.choice([True, False]),
                    training_completed="Basic Foster Training,Medical Care" if random.random() > 0.5 else "Basic Foster Training",
                    is_available=random.choice([True, True, True, False]),  # 75% available
                    total_fosters=random.randint(0, 25),
                    successful_adoptions=random.randint(0, 20),
                    avg_foster_duration_days=random.uniform(14.0, 120.0),
                    rating=random.uniform(3.5, 5.0),
                    background_check_status=random.choice(["approved", "approved", "pending"]),
                    background_check_date=datetime.now() - timedelta(days=random.randint(30, 365)) if random.random() > 0.3 else None,
                    insurance_verified=random.choice([True, False]),
                    references_checked=random.choice([True, False])
                )
                db.add(profile)
                db.commit()
                db.refresh(profile)
                foster_profiles.append(profile)
                print(f"   ✓ Created foster profile for: {foster_user.full_name} (Experience: {experience_level.value})")
            else:
                foster_profiles.append(existing_profile)
                print(f"   ✓ Foster profile already exists for: {foster_user.full_name}")

        # 6. Create 20 People for Organization 1
        print("\n6. Creating 20 people for Organization 1...")
        people_org1 = []

        for i in range(20):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            city_idx = random.randint(0, len(CITIES)-1)

            person = models.Person(
                org_id=org1.id,
                first_name=first_name,
                last_name=last_name,
                phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                street_1=f"{random.randint(100,9999)} {random.choice(['Main', 'Oak', 'Maple', 'Pine', 'Elm'])} St",
                city=CITIES[city_idx],
                state=STATES[city_idx],
                country="USA",
                zip_code=f"{random.randint(10000,99999)}",
                # Randomly assign tags
                tag_adopter=random.random() > 0.7,
                tag_potential_adopter=random.random() > 0.5,
                tag_foster=random.random() > 0.8,
                tag_volunteer=random.random() > 0.6,
                tag_donor=random.random() > 0.7,
                tag_board_member=random.random() > 0.95
            )
            db.add(person)
            db.commit()
            db.refresh(person)
            people_org1.append(person)

            tags = []
            if person.tag_adopter:
                tags.append("adopter")
            if person.tag_potential_adopter:
                tags.append("potential_adopter")
            if person.tag_foster:
                tags.append("foster")
            if person.tag_volunteer:
                tags.append("volunteer")
            if person.tag_donor:
                tags.append("donor")
            if person.tag_board_member:
                tags.append("board_member")

            tag_str = ", ".join(tags) if tags else "no tags"
            print(f"   ✓ Created person: {first_name} {last_name} ({tag_str})")

        # 7. Create 5 Test Tasks for Organization 1
        print("\n7. Creating 5 test tasks for Organization 1...")
        task_titles = [
            "Schedule vet appointment for {}",
            "Follow up with {} about adoption application",
            "Update website with new pet photos",
            "Coordinate foster placement for {}",
            "Review and approve adoption applications",
            "Organize fundraising event",
            "Update social media posts",
            "Process donation receipts",
            "Call {} to schedule home visit",
            "Order supplies for foster care"
        ]

        tasks = []
        for i in range(5):
            task_template = random.choice(task_titles)

            # Format title with pet or person name if needed
            if '{}' in task_template:
                if random.random() > 0.5 and pets_org1:
                    title = task_template.format(random.choice(pets_org1).name)
                    related_pet_id = random.choice(pets_org1).id if random.random() > 0.5 else None
                elif people_org1:
                    person = random.choice(people_org1)
                    title = task_template.format(f"{person.first_name} {person.last_name}")
                    related_pet_id = None
                else:
                    title = task_template.replace(" {}", "")
                    related_pet_id = None
            else:
                title = task_template
                related_pet_id = None

            task = models.Task(
                org_id=org1.id,
                title=title,
                description=f"Task description for: {title}",
                status=random.choice([
                    models.TaskStatus.open,
                    models.TaskStatus.in_progress,
                    models.TaskStatus.open,  # More open tasks
                    models.TaskStatus.completed
                ]),
                priority=random.choice([
                    models.TaskPriority.normal,
                    models.TaskPriority.high,
                    models.TaskPriority.urgent,
                    models.TaskPriority.low
                ]),
                due_date=datetime.now() + timedelta(days=random.randint(-7, 30)),
                created_by_user_id=users_org1[0].id,  # First user creates tasks
                assigned_to_user_id=random.choice(users_org1).id if random.random() > 0.3 else None,
                related_pet_id=related_pet_id
            )
            db.add(task)
            db.commit()
            db.refresh(task)
            tasks.append(task)

            assigned_to = "Unassigned"
            if task.assigned_to_user_id:
                assigned_user = next((u for u in users_org1 if u.id == task.assigned_to_user_id), None)
                if assigned_user:
                    assigned_to = assigned_user.full_name

            print(f"   ✓ Created task: {title}")
            print(f"      Status: {task.status.value}, Priority: {task.priority.value}, Assigned: {assigned_to}")

        print("\n" + "=" * 60)
        print("Summary:")
        print("=" * 60)
        print(f"✓ Roles: {len(roles)}")
        print(f"✓ Organizations: {len(organizations)}")
        print(f"✓ Users for Org 1: {len(users_org1)}")
        print(f"✓ Pets for Org 1: {len(pets_org1)}")
        print(f"✓ Foster Profiles for Org 1: {len(foster_profiles)}")
        print(f"✓ People for Org 1: {len(people_org1)}")
        print(f"✓ Tasks for Org 1: {len(tasks)}")
        print("=" * 60)
        print("\nTest data created successfully!")
        print("\nYou can login with any user email and password: password123")
        print(f"Example: {users_org1[0].email} / password123")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)
    create_comprehensive_test_data()
