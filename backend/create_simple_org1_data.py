"""
Simple comprehensive test data generation for Organization 1
Run with: python create_simple_org1_data.py
"""

import os
import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app import models
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Sample data
DOG_NAMES = ["Max", "Buddy", "Charlie", "Cooper", "Rocky", "Duke", "Bear", "Zeus", "Jack", "Toby",
             "Bailey", "Daisy", "Sadie", "Molly", "Maggie", "Sophie", "Abby", "Chloe", "Roxy", "Penny"]
CAT_NAMES = ["Luna", "Bella", "Simba", "Milo", "Lucy", "Oliver", "Shadow", "Smokey", "Tiger", "Whiskers",
             "Mittens", "Oreo", "Ginger", "Felix", "Nala", "Jasper", "Cleo", "Socks", "Patches", "Snowball"]
DOG_BREEDS = ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Beagle", "Poodle", "Boxer",
              "Australian Shepherd", "Siberian Husky", "Doberman Pinscher", "Chihuahua", "Corgi"]
CAT_BREEDS = ["Domestic Shorthair", "Domestic Longhair", "Siamese", "Persian", "Maine Coon", "Ragdoll"]
COLORS = ["Black", "White", "Brown", "Golden", "Gray", "Orange", "Tan", "Black and White", "Tricolor"]
FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]

def create_simple_org1_data():
    db = SessionLocal()

    try:
        print("=" * 60)
        print("Creating simple comprehensive test data for Org 1")
        print("=" * 60)

        # Get or create Org 1
        org1 = db.query(models.Organization).filter(models.Organization.id == 1).first()
        if not org1:
            org1 = models.Organization(
                id=1,
                name="Happy Paws Rescue",
                primary_contact_email="contact@happypawsrescue.org"
            )
            db.add(org1)
            db.commit()
            db.refresh(org1)

        print("\n1. Creating 60 pets...")
        statuses = ["intake", "needs_foster", "in_foster", "available", "pending", "adopted"]

        for i in range(60):
            is_dog = i % 2 == 0
            species = "Dog" if is_dog else "Cat"
            name = random.choice(DOG_NAMES if is_dog else CAT_NAMES) + str(i)

            intake_date = datetime.now() - timedelta(days=random.randint(1, 180))

            pet = models.Pet(
                org_id=1,
                name=name,
                species=species,
                breed=random.choice(DOG_BREEDS if is_dog else CAT_BREEDS),
                sex=random.choice(["Male", "Female"]),
                status=statuses[i % len(statuses)],
                intake_date=intake_date.date(),
                weight=random.uniform(10, 70),
                altered_status="yes",
                color=random.choice(COLORS),
                adoption_fee=random.choice([50, 75, 100, 125, 150]),
                description_public=f"{name} is a wonderful pet!",
                description_internal="Friendly and healthy"
            )
            db.add(pet)

            if i % 10 == 0:
                db.commit()

        db.commit()
        print("   ✓ Created 60 pets")

        print("\n2. Creating 30 people...")
        for i in range(30):
            person = models.Person(
                org_id=1,
                first_name=random.choice(FIRST_NAMES),
                last_name=random.choice(LAST_NAMES) + str(i),
                email=f"person{i}@example.com",
                phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                tag_foster=i < 10,
                tag_current_foster=i < 5,
                tag_adopter=10 <= i < 20,
                tag_volunteer=i % 3 == 0,
                tag_donor=i % 5 == 0
            )
            db.add(person)

        db.commit()
        print("   ✓ Created 30 people")

        # Get or create a default user for org 1
        default_user = db.query(models.User).filter(models.User.org_id == 1).first()
        if not default_user:
            default_user = models.User(
                org_id=1,
                email="admin@happypawsrescue.org",
                full_name="System Admin",
                hashed_password=hash_password("password123"),
                is_active=True
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)

        print("\n3. Creating 40 tasks...")
        for i in range(40):
            task = models.Task(
                org_id=1,
                title=f"Task {i+1}: Follow up on pet care",
                description=f"Task description {i+1}",
                priority=random.choice(["low", "medium", "high", "urgent"]),
                status=random.choice(["pending", "in_progress", "completed"]),
                due_date=(datetime.now() + timedelta(days=random.randint(-10, 30))).date(),
                created_by_user_id=default_user.id
            )
            db.add(task)

        db.commit()
        print("   ✓ Created 40 tasks")

        print("\n4. Creating expense categories and expenses...")
        category_names = ["Medical", "Food & Supplies", "Facility", "Marketing", "Administrative"]
        expense_categories = []

        for cat_name in category_names:
            cat = db.query(models.ExpenseCategory).filter(
                models.ExpenseCategory.org_id == 1,
                models.ExpenseCategory.name == cat_name
            ).first()

            if not cat:
                cat = models.ExpenseCategory(
                    org_id=1,
                    name=cat_name,
                    is_active=True
                )
                db.add(cat)
                db.commit()
                db.refresh(cat)

            expense_categories.append(cat)

        for i in range(30):
            expense = models.Expense(
                org_id=1,
                category_id=random.choice(expense_categories).id,
                amount=random.uniform(25, 500),
                description=f"Expense for operations",
                date_incurred=datetime.now() - timedelta(days=random.randint(1, 180)),
                recorded_by_user_id=default_user.id
            )
            db.add(expense)

        db.commit()
        print("   ✓ Created expense categories and 30 expenses")

        print("\n✅ Successfully created test data!")
        print("\nSummary:")
        print("  • 60 Pets (various statuses across species)")
        print("  • 30 People (fosters, adopters, volunteers, donors)")
        print("  • 40 Tasks (various priorities and statuses)")
        print("  • 30 Expenses (across 5 categories)")
        print("\nAll data created for Organization 1")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_simple_org1_data()
