"""
Seed database with comprehensive test data
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, init_db
from app.models import (
    Organization, User, Animal, FosterProfile, FosterPlacement,
    CareUpdate, SystemConfig, PetStatus, UserRole, FosterExperienceLevel,
    PlacementOutcome
)
from app.security import get_password_hash


def seed_database():
    """Seed the database with test data"""
    print("Initializing database...")
    init_db()

    db = SessionLocal()

    try:
        print("Creating organization...")
        org = Organization(name="Happy Paws Rescue")
        db.add(org)
        db.commit()
        db.refresh(org)

        print("Creating users...")
        # Admin user
        admin = User(
            org_id=org.id,
            email="admin@rescueworks.test",
            full_name="Admin User",
            phone="555-0100",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.admin
        )
        db.add(admin)

        # Coordinator user
        coordinator = User(
            org_id=org.id,
            email="coordinator@rescueworks.test",
            full_name="Sarah Coordinator",
            phone="555-0101",
            hashed_password=get_password_hash("coord123"),
            role=UserRole.coordinator
        )
        db.add(coordinator)

        # Foster users
        foster_users = [
            User(
                org_id=org.id,
                email=f"foster{i}@rescueworks.test",
                full_name=f"Foster User {i}",
                phone=f"555-{1000+i}",
                hashed_password=get_password_hash(f"foster{i}123"),
                role=UserRole.foster
            )
            for i in range(1, 6)
        ]
        for user in foster_users:
            db.add(user)

        db.commit()

        print("Creating animals...")

        animals = []
        for data in animals_data:
            animal = Animal(
                org_id=org.id,
                intake_date=datetime.now().date() - timedelta(days=30),
                description=f"A lovely {data['species'].lower()} looking for a forever home.",
                internal_notes="Standard intake process completed",
                **data
            )
            db.add(animal)
            animals.append(animal)

        db.commit()

        print("Creating foster profiles...")
        foster_profiles_data = [
            {
                "user": foster_users[0],
                "experience_level": FosterExperienceLevel.advanced,
                "preferred_species": "Dog",
                "max_capacity": 2,
                "current_capacity": 0,
                "can_handle_medical": True,
                "can_handle_behavioral": True,
                "has_yard": True,
                "rating": 4.8
            },
            {
                "user": foster_users[1],
                "experience_level": FosterExperienceLevel.intermediate,
                "preferred_species": "Cat",
                "max_capacity": 3,
                "current_capacity": 1,
                "can_handle_medical": False,
                "can_handle_behavioral": False,
                "has_yard": False,
                "rating": 4.5
            },
            {
                "user": foster_users[2],
                "experience_level": FosterExperienceLevel.beginner,
                "preferred_species": "Dog,Cat",
                "max_capacity": 1,
                "current_capacity": 1,
                "can_handle_medical": False,
                "can_handle_behavioral": False,
                "has_yard": True,
                "rating": 4.3
            },
            {
                "user": foster_users[3],
                "experience_level": FosterExperienceLevel.advanced,
                "preferred_species": "Dog",
                "max_capacity": 3,
                "current_capacity": 0,
                "can_handle_medical": True,
                "can_handle_behavioral": False,
                "has_yard": True,
                "rating": 4.9,
                "total_fosters": 15,
                "successful_adoptions": 13
            },
            {
                "user": foster_users[4],
                "experience_level": FosterExperienceLevel.intermediate,
                "preferred_species": "Cat",
                "max_capacity": 2,
                "current_capacity": 0,
                "can_handle_medical": False,
                "can_handle_behavioral": True,
                "has_yard": False,
                "rating": 4.6,
                "total_fosters": 8,
                "successful_adoptions": 7
            },
        ]

        foster_profiles = []
        for data in foster_profiles_data:
            user = data.pop("user")
            profile = FosterProfile(
                user_id=user.id,
                org_id=org.id,
                home_type="house",
                has_other_pets=False,
                has_children=False,
                is_available=True,
                **data
            )
            db.add(profile)
            foster_profiles.append(profile)

        db.commit()

        print("Creating foster placements...")
        # Active placements
        placement1 = FosterPlacement(
            org_id=org.id,
            animal_id=animals[3].id,  # Charlie (in_foster)
            foster_profile_id=foster_profiles[2].id,
            start_date=datetime.now() - timedelta(days=15),
            expected_end_date=datetime.now() + timedelta(days=45),
            outcome=PlacementOutcome.active,
            placement_notes="Doing great with the family!"
        )
        db.add(placement1)
        animals[3].foster_user_id = foster_profiles[2].user_id

        placement2 = FosterPlacement(
            org_id=org.id,
            animal_id=animals[6].id,  # Mittens (in_foster)
            foster_profile_id=foster_profiles[1].id,
            start_date=datetime.now() - timedelta(days=20),
            expected_end_date=datetime.now() + timedelta(days=40),
            outcome=PlacementOutcome.active,
            placement_notes="Very playful and friendly"
        )
        db.add(placement2)
        animals[6].foster_user_id = foster_profiles[1].user_id

        # Completed placement (adopted)
        placement3 = FosterPlacement(
            org_id=org.id,
            animal_id=animals[7].id,  # Buddy (adopted)
            foster_profile_id=foster_profiles[3].id,
            start_date=datetime.now() - timedelta(days=60),
            expected_end_date=datetime.now() - timedelta(days=10),
            actual_end_date=datetime.now() - timedelta(days=5),
            outcome=PlacementOutcome.adopted,
            placement_notes="Successfully adopted!"
        )
        db.add(placement3)

        db.commit()

        print("Creating care updates...")
        care_updates = [
            CareUpdate(
                org_id=org.id,
                animal_id=animals[3].id,
                created_by_user_id=foster_users[2].id,
                update_type="general",
                update_text="Charlie is settling in well. He loves playing fetch!",
                is_important=False
            ),
            CareUpdate(
                org_id=org.id,
                animal_id=animals[3].id,
                created_by_user_id=foster_users[2].id,
                update_type="behavioral",
                update_text="Working on basic commands. Responds well to training.",
                is_important=True
            ),
            CareUpdate(
                org_id=org.id,
                animal_id=animals[6].id,
                created_by_user_id=foster_users[1].id,
                update_type="health",
                update_text="Mittens went for her checkup. All clear!",
                is_important=True
            ),
            CareUpdate(
                org_id=org.id,
                animal_id=animals[0].id,
                created_by_user_id=coordinator.id,
                update_type="general",
                update_text="Max completed intake examination. Ready for foster placement.",
                is_important=False
            ),
        ]

        for update in care_updates:
            db.add(update)

        db.commit()

        print("Creating system configuration...")
        configs = [
            SystemConfig(
                org_id=org.id,
                key="organization_email",
                value="contact@happypaws.org",
                description="Main contact email for the organization"
            ),
            SystemConfig(
                org_id=org.id,
                key="adoption_fee_dog",
                value="250",
                description="Standard adoption fee for dogs (USD)"
            ),
            SystemConfig(
                org_id=org.id,
                key="adoption_fee_cat",
                value="150",
                description="Standard adoption fee for cats (USD)"
            ),
            SystemConfig(
                org_id=org.id,
                key="max_foster_duration",
                value="90",
                description="Maximum foster duration in days"
            ),
        ]

        for config in configs:
            db.add(config)

        db.commit()

        print("\n" + "="*60)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("="*60)
        print("\nTest Users Created:")
        print("-" * 60)
        print(f"Admin:       admin@rescueworks.test / admin123")
        print(f"Coordinator: coordinator@rescueworks.test / coord123")
        print(f"Foster 1:    foster1@rescueworks.test / foster1123")
        print(f"Foster 2:    foster2@rescueworks.test / foster2123")
        print(f"Foster 3:    foster3@rescueworks.test / foster3123")
        print(f"Foster 4:    foster4@rescueworks.test / foster4123")
        print(f"Foster 5:    foster5@rescueworks.test / foster5123")
        print("\nData Summary:")
        print("-" * 60)
        print(f"Animals:          10 (various statuses)")
        print(f"Foster Profiles:  5 (with different experience levels)")
        print(f"Placements:       3 (2 active, 1 completed)")
        print(f"Care Updates:     4")
        print(f"System Configs:   4")
        print("="*60)

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
