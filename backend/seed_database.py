#!/usr/bin/env python3
"""Seed the database with comprehensive test data for development and testing."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database():
    """Add comprehensive test data to the database."""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("SEEDING DATABASE WITH TEST DATA")
        print("=" * 60)

        # ============================================================
        # 1. CREATE ORGANIZATION
        # ============================================================
        print("\n[1/8] Creating organization...")
        org = db.query(models.Organization).first()
        if not org:
            org = models.Organization(
                name="Pawsitive Rescue",
                logo_url="https://example.com/logo.png",
                primary_contact_email="admin@pawsitiverescue.org"
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"  ✓ Created organization: {org.name}")
        else:
            print(f"  ✓ Organization already exists: {org.name}")

        # ============================================================
        # 2. CREATE USERS (Admin, Staff, Fosters)
        # ============================================================
        print("\n[2/8] Creating users...")

        users_data = [
            {
                "email": "admin@pawsitiverescue.org",
                "full_name": "Admin User",
                "phone": "555-0100",
                "role": "admin"
            },
            {
                "email": "staff@pawsitiverescue.org",
                "full_name": "Staff Member",
                "phone": "555-0101",
                "role": "staff"
            },
            {
                "email": "sarah.foster@example.com",
                "full_name": "Sarah Johnson",
                "phone": "555-0201",
                "role": "foster",
                "profile": {
                    "experience_level": models.FosterExperienceLevel.advanced,
                    "preferred_species": "dog,cat",
                    "preferred_ages": "puppy,kitten,adult",
                    "max_capacity": 3,
                    "current_capacity": 0,
                    "home_type": models.HomeType.house,
                    "has_yard": True,
                    "has_other_pets": True,
                    "other_pets_description": "2 friendly dogs, 1 cat",
                    "has_children": True,
                    "children_ages": "8,12",
                    "can_handle_medical": True,
                    "can_handle_behavioral": True,
                    "is_available": True,
                    "background_check_status": "approved",
                    "background_check_date": datetime.utcnow() - timedelta(days=90),
                    "insurance_verified": True,
                    "references_checked": True,
                    "rating": 4.8,
                    "total_fosters": 15,
                    "successful_adoptions": 13,
                    "avg_foster_duration_days": 45.0,
                }
            },
            {
                "email": "mike.foster@example.com",
                "full_name": "Mike Anderson",
                "phone": "555-0202",
                "role": "foster",
                "profile": {
                    "experience_level": models.FosterExperienceLevel.intermediate,
                    "preferred_species": "dog",
                    "preferred_ages": "adult,senior",
                    "max_capacity": 2,
                    "current_capacity": 0,
                    "home_type": models.HomeType.apartment,
                    "has_yard": False,
                    "has_other_pets": False,
                    "has_children": False,
                    "can_handle_medical": False,
                    "can_handle_behavioral": True,
                    "is_available": True,
                    "background_check_status": "approved",
                    "background_check_date": datetime.utcnow() - timedelta(days=60),
                    "insurance_verified": True,
                    "references_checked": True,
                    "rating": 4.5,
                    "total_fosters": 8,
                    "successful_adoptions": 7,
                    "avg_foster_duration_days": 60.0,
                }
            },
            {
                "email": "emma.foster@example.com",
                "full_name": "Emma Davis",
                "phone": "555-0203",
                "role": "foster",
                "profile": {
                    "experience_level": models.FosterExperienceLevel.advanced,
                    "preferred_species": "cat",
                    "preferred_ages": "kitten,adult",
                    "max_capacity": 4,
                    "current_capacity": 0,
                    "home_type": models.HomeType.house,
                    "has_yard": True,
                    "has_other_pets": True,
                    "other_pets_description": "3 cats",
                    "has_children": False,
                    "can_handle_medical": True,
                    "can_handle_behavioral": True,
                    "is_available": True,
                    "background_check_status": "approved",
                    "background_check_date": datetime.utcnow() - timedelta(days=120),
                    "insurance_verified": True,
                    "references_checked": True,
                    "rating": 5.0,
                    "total_fosters": 22,
                    "successful_adoptions": 20,
                    "avg_foster_duration_days": 35.0,
                }
            },
        ]

        created_users = {}
        for user_data in users_data:
            existing_user = db.query(models.User).filter_by(email=user_data["email"]).first()
            if existing_user:
                print(f"  ⊙ User already exists: {user_data['email']}")
                created_users[user_data["email"]] = existing_user
                continue

            user = models.User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                hashed_password=pwd_context.hash("password123"),
                org_id=org.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users[user_data["email"]] = user
            print(f"  ✓ Created user: {user.full_name} ({user.email})")

            # Create foster profile if applicable
            if "profile" in user_data:
                profile_data = user_data["profile"]
                foster_profile = models.FosterProfile(
                    user_id=user.id,
                    org_id=org.id,
                    **profile_data
                )
                db.add(foster_profile)
                db.commit()
                print(f"    ✓ Created foster profile")

        # ============================================================
        # 3. CREATE PETS
        # ============================================================
        print("\n[3/8] Creating pets...")

        pets_data = [
            {
                "name": "Buddy",
                "species": "Dog",
                "breed": "Labrador Retriever",
                "sex": "Male",
                "date_of_birth": datetime.utcnow() - timedelta(days=365*3),
                "weight": 65.0,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.available,
                "description_public": "Buddy is a friendly, energetic lab who loves to play fetch and go for walks. Great with kids!",
                "description_internal": "Fully vaccinated, heartworm negative. Very trainable.",
                "microchip_number": "123456789012345",
                "adoption_fee": 250.0,
                "intake_date": datetime.utcnow() - timedelta(days=45),
            },
            {
                "name": "Whiskers",
                "species": "Cat",
                "breed": "Domestic Shorthair",
                "sex": "Female",
                "date_of_birth": datetime.utcnow() - timedelta(days=365*2),
                "weight": 9.5,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.available,
                "description_public": "Whiskers is a sweet, affectionate cat who loves to cuddle. She's litter trained and gets along well with other cats.",
                "description_internal": "FeLV/FIV negative, all vaccines up to date.",
                "microchip_number": "987654321098765",
                "adoption_fee": 150.0,
                "intake_date": datetime.utcnow() - timedelta(days=30),
            },
            {
                "name": "Luna",
                "species": "Dog",
                "breed": "German Shepherd Mix",
                "sex": "Female",
                "date_of_birth": datetime.utcnow() - timedelta(days=180),
                "weight": 35.0,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.in_foster,
                "description_public": "Luna is a playful puppy who is learning basic commands. She would do well in an active home.",
                "description_internal": "In foster with Sarah Johnson. Doing well with house training.",
                "microchip_number": "567890123456789",
                "adoption_fee": 300.0,
                "intake_date": datetime.utcnow() - timedelta(days=20),
                "foster_user_id": created_users.get("sarah.foster@example.com").id if "sarah.foster@example.com" in created_users else None,
            },
            {
                "name": "Max",
                "species": "Dog",
                "breed": "Beagle",
                "sex": "Male",
                "date_of_birth": datetime.utcnow() - timedelta(days=365*5),
                "weight": 28.0,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.needs_foster,
                "description_public": "Max is a calm senior dog who enjoys leisurely walks and napping. He would be perfect for a quiet home.",
                "description_internal": "Senior dog, some arthritis but managing well with medication.",
                "microchip_number": "234567890123456",
                "adoption_fee": 100.0,
                "intake_date": datetime.utcnow() - timedelta(days=60),
            },
            {
                "name": "Mittens",
                "species": "Cat",
                "breed": "Siamese",
                "sex": "Female",
                "date_of_birth": datetime.utcnow() - timedelta(days=365),
                "weight": 8.0,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.pending,
                "description_public": "Mittens is a vocal, social cat who loves attention. She's very playful and curious.",
                "description_internal": "Application pending with adopter. Should be ready to go home next week.",
                "microchip_number": "345678901234567",
                "adoption_fee": 150.0,
                "intake_date": datetime.utcnow() - timedelta(days=40),
            },
            {
                "name": "Rocky",
                "species": "Dog",
                "breed": "Pit Bull Terrier",
                "sex": "Male",
                "date_of_birth": datetime.utcnow() - timedelta(days=365*4),
                "weight": 55.0,
                "altered_status": models.AlteredStatus.yes,
                "status": models.PetStatus.intake,
                "description_public": "Rocky is a strong, loyal dog who needs an experienced owner.",
                "description_internal": "New intake, needs behavioral assessment before foster placement.",
                "microchip_number": "456789012345678",
                "adoption_fee": 200.0,
                "intake_date": datetime.utcnow() - timedelta(days=5),
            },
        ]

        created_pets = []
        for pet_data in pets_data:
            existing_pet = db.query(models.Pet).filter_by(
                name=pet_data["name"],
                org_id=org.id
            ).first()
            if existing_pet:
                print(f"  ⊙ Pet already exists: {pet_data['name']}")
                created_pets.append(existing_pet)
                continue

            pet = models.Pet(org_id=org.id, **pet_data)
            db.add(pet)
            db.commit()
            db.refresh(pet)
            created_pets.append(pet)
            print(f"  ✓ Created pet: {pet.name} ({pet.species})")

        # ============================================================
        # 4. CREATE FOSTER PLACEMENTS
        # ============================================================
        print("\n[4/8] Creating foster placements...")

        # Create placement for Luna with Sarah
        if "sarah.foster@example.com" in created_users:
            sarah_user = created_users["sarah.foster@example.com"]
            sarah_profile = db.query(models.FosterProfile).filter_by(user_id=sarah_user.id).first()
            luna_pet = db.query(models.Pet).filter_by(name="Luna", org_id=org.id).first()

            if sarah_profile and luna_pet:
                existing_placement = db.query(models.FosterPlacement).filter_by(
                    pet_id=luna_pet.id,
                    foster_profile_id=sarah_profile.id,
                    outcome=models.PlacementOutcome.active
                ).first()

                if not existing_placement:
                    placement = models.FosterPlacement(
                        org_id=org.id,
                        pet_id=luna_pet.id,
                        foster_profile_id=sarah_profile.id,
                        start_date=datetime.utcnow() - timedelta(days=20),
                        expected_end_date=datetime.utcnow() + timedelta(days=40),
                        outcome=models.PlacementOutcome.active,
                        agreement_signed=True,
                        agreement_signed_date=datetime.utcnow() - timedelta(days=20),
                        placement_notes="Puppy needs house training and socialization"
                    )
                    db.add(placement)
                    db.commit()
                    print(f"  ✓ Created foster placement: Luna with Sarah Johnson")
                else:
                    print(f"  ⊙ Foster placement already exists: Luna with Sarah Johnson")

        # ============================================================
        # 5. CREATE EXPENSE CATEGORIES
        # ============================================================
        print("\n[5/8] Creating expense categories...")

        categories_data = [
            {"name": "Medical Care", "description": "Veterinary bills, medications, surgeries"},
            {"name": "Food & Supplies", "description": "Pet food, litter, toys, bedding"},
            {"name": "Facility Costs", "description": "Rent, utilities, maintenance"},
            {"name": "Marketing", "description": "Adoption events, advertising, website"},
            {"name": "Administrative", "description": "Office supplies, software, legal fees"},
        ]

        for cat_data in categories_data:
            existing_cat = db.query(models.ExpenseCategory).filter_by(
                name=cat_data["name"],
                org_id=org.id
            ).first()
            if existing_cat:
                print(f"  ⊙ Category already exists: {cat_data['name']}")
                continue

            category = models.ExpenseCategory(org_id=org.id, **cat_data)
            db.add(category)
            db.commit()
            print(f"  ✓ Created expense category: {category.name}")

        # ============================================================
        # 6. CREATE SAMPLE EXPENSES
        # ============================================================
        print("\n[6/8] Creating sample expenses...")

        admin_user = created_users.get("admin@pawsitiverescue.org")
        medical_cat = db.query(models.ExpenseCategory).filter_by(
            name="Medical Care",
            org_id=org.id
        ).first()
        food_cat = db.query(models.ExpenseCategory).filter_by(
            name="Food & Supplies",
            org_id=org.id
        ).first()

        expenses_data = []
        if admin_user and medical_cat:
            expenses_data.append({
                "category_id": medical_cat.id,
                "amount": 350.50,
                "description": "Spay surgery for Whiskers",
                "vendor_name": "Happy Paws Veterinary Clinic",
                "recorded_by_user_id": admin_user.id,
                "date_incurred": datetime.utcnow() - timedelta(days=25),
            })

        if admin_user and food_cat:
            expenses_data.append({
                "category_id": food_cat.id,
                "amount": 125.00,
                "description": "Monthly pet food order",
                "vendor_name": "PetMart",
                "recorded_by_user_id": admin_user.id,
                "date_incurred": datetime.utcnow() - timedelta(days=10),
            })

        for expense_data in expenses_data:
            expense = models.Expense(org_id=org.id, **expense_data)
            db.add(expense)
            db.commit()
            print(f"  ✓ Created expense: {expense.description}")

        # ============================================================
        # 7. CREATE SAMPLE PEOPLE (Adopters, etc.)
        # ============================================================
        print("\n[7/8] Creating sample people...")

        people_data = [
            {
                "first_name": "John",
                "last_name": "Smith",
                "email": "john.smith@example.com",
                "phone": "555-0301",
                "street_1": "123 Oak Street",
                "city": "Springfield",
                "state": "IL",
                "zip_code": "62701",
                "tag_potential_adopter": True,
            },
            {
                "first_name": "Maria",
                "last_name": "Garcia",
                "email": "maria.garcia@example.com",
                "phone": "555-0302",
                "street_1": "456 Elm Avenue",
                "city": "Springfield",
                "state": "IL",
                "zip_code": "62702",
                "tag_adopter": True,
            },
        ]

        for person_data in people_data:
            existing_person = db.query(models.Person).filter_by(
                email=person_data["email"],
                org_id=org.id
            ).first()
            if existing_person:
                print(f"  ⊙ Person already exists: {person_data['first_name']} {person_data['last_name']}")
                continue

            person = models.Person(org_id=org.id, **person_data)
            db.add(person)
            db.commit()
            print(f"  ✓ Created person: {person.first_name} {person.last_name}")

        # ============================================================
        # 8. CREATE SAMPLE TASKS
        # ============================================================
        print("\n[8/8] Creating sample tasks...")

        if admin_user:
            tasks_data = [
                {
                    "title": "Schedule vet appointment for Max",
                    "description": "Annual checkup and arthritis medication refill",
                    "status": models.TaskStatus.open,
                    "priority": models.TaskPriority.high,
                    "created_by_user_id": admin_user.id,
                    "assigned_to_user_id": created_users.get("staff@pawsitiverescue.org").id if "staff@pawsitiverescue.org" in created_users else admin_user.id,
                    "due_date": datetime.utcnow() + timedelta(days=7),
                },
                {
                    "title": "Update Buddy's adoption listing photos",
                    "description": "Take new photos showing Buddy's playful personality",
                    "status": models.TaskStatus.in_progress,
                    "priority": models.TaskPriority.normal,
                    "created_by_user_id": admin_user.id,
                    "assigned_to_user_id": created_users.get("staff@pawsitiverescue.org").id if "staff@pawsitiverescue.org" in created_users else admin_user.id,
                    "due_date": datetime.utcnow() + timedelta(days=3),
                },
            ]

            for task_data in tasks_data:
                existing_task = db.query(models.Task).filter_by(
                    title=task_data["title"],
                    org_id=org.id
                ).first()
                if existing_task:
                    print(f"  ⊙ Task already exists: {task_data['title']}")
                    continue

                task = models.Task(org_id=org.id, **task_data)
                db.add(task)
                db.commit()
                print(f"  ✓ Created task: {task.title}")

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 60)
        print("DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\nTest Accounts (all passwords: password123):")
        print("  • admin@pawsitiverescue.org - Admin User")
        print("  • staff@pawsitiverescue.org - Staff Member")
        print("  • sarah.foster@example.com - Foster (Advanced)")
        print("  • mike.foster@example.com - Foster (Intermediate)")
        print("  • emma.foster@example.com - Foster (Advanced)")
        print("\nDatabase Contents:")
        print(f"  • Organizations: {db.query(models.Organization).count()}")
        print(f"  • Users: {db.query(models.User).count()}")
        print(f"  • Foster Profiles: {db.query(models.FosterProfile).count()}")
        print(f"  • Pets: {db.query(models.Pet).count()}")
        print(f"  • Foster Placements: {db.query(models.FosterPlacement).count()}")
        print(f"  • Expense Categories: {db.query(models.ExpenseCategory).count()}")
        print(f"  • Expenses: {db.query(models.Expense).count()}")
        print(f"  • People: {db.query(models.Person).count()}")
        print(f"  • Tasks: {db.query(models.Task).count()}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
