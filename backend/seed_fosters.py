#!/usr/bin/env python3
"""Seed the database with sample foster profiles for testing."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_fosters():
    """Add sample foster users and profiles for testing."""
    db = SessionLocal()

    try:
        # Get the first organization (or create one if it doesn't exist)
        org = db.query(models.Organization).first()
        if not org:
            org = models.Organization(
                name="Test Rescue Organization",
                email="admin@testrescue.org",
                phone="555-0100",
                address="123 Main St, Test City, TC 12345"
            )
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"Created organization: {org.name}")

        # Sample foster users data
        foster_users_data = [
            {
                "email": "sarah.foster@example.com",
                "full_name": "Sarah Johnson",
                "phone": "555-0101",
                "role": models.UserRole.foster,
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
                "phone": "555-0102",
                "role": models.UserRole.foster,
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
                "phone": "555-0103",
                "role": models.UserRole.foster,
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
            {
                "email": "james.foster@example.com",
                "full_name": "James Wilson",
                "phone": "555-0104",
                "role": models.UserRole.foster,
                "profile": {
                    "experience_level": models.FosterExperienceLevel.beginner,
                    "preferred_species": "dog,cat",
                    "preferred_ages": "adult",
                    "max_capacity": 1,
                    "current_capacity": 0,
                    "home_type": models.HomeType.condo,
                    "has_yard": False,
                    "has_other_pets": False,
                    "has_children": False,
                    "can_handle_medical": False,
                    "can_handle_behavioral": False,
                    "is_available": True,
                    "background_check_status": "approved",
                    "background_check_date": datetime.utcnow() - timedelta(days=30),
                    "insurance_verified": True,
                    "references_checked": True,
                    "rating": 4.2,
                    "total_fosters": 3,
                    "successful_adoptions": 2,
                    "avg_foster_duration_days": 50.0,
                }
            },
            {
                "email": "lisa.foster@example.com",
                "full_name": "Lisa Martinez",
                "phone": "555-0105",
                "role": models.UserRole.foster,
                "profile": {
                    "experience_level": models.FosterExperienceLevel.intermediate,
                    "preferred_species": "dog,cat,rabbit",
                    "preferred_ages": "puppy,kitten,young",
                    "max_capacity": 2,
                    "current_capacity": 0,
                    "home_type": models.HomeType.house,
                    "has_yard": True,
                    "has_other_pets": True,
                    "other_pets_description": "1 dog, 2 rabbits",
                    "has_children": True,
                    "children_ages": "5,7,10",
                    "can_handle_medical": True,
                    "can_handle_behavioral": False,
                    "is_available": True,
                    "background_check_status": "approved",
                    "background_check_date": datetime.utcnow() - timedelta(days=75),
                    "insurance_verified": True,
                    "references_checked": True,
                    "rating": 4.6,
                    "total_fosters": 11,
                    "successful_adoptions": 10,
                    "avg_foster_duration_days": 40.0,
                }
            },
        ]

        for user_data in foster_users_data:
            # Check if user already exists
            existing_user = db.query(models.User).filter_by(email=user_data["email"]).first()
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                continue

            # Create user
            user = models.User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                phone=user_data["phone"],
                hashed_password=pwd_context.hash("password123"),  # Default password
                role=user_data["role"],
                org_id=org.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {user.full_name} ({user.email})")

            # Create foster profile
            profile_data = user_data["profile"]
            foster_profile = models.FosterProfile(
                user_id=user.id,
                org_id=org.id,
                **profile_data
            )
            db.add(foster_profile)
            db.commit()
            db.refresh(foster_profile)
            print(f"  Created foster profile for {user.full_name}")

        print("\n✅ Foster profiles seeded successfully!")
        print("\nYou can now log in with any of these accounts:")
        print("  sarah.foster@example.com / password123")
        print("  mike.foster@example.com / password123")
        print("  emma.foster@example.com / password123")
        print("  james.foster@example.com / password123")
        print("  lisa.foster@example.com / password123")

    except Exception as e:
        print(f"Error seeding foster profiles: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_fosters()
