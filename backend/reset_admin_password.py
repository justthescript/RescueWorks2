#!/usr/bin/env python3
"""
Reset the password for nateweaver94@gmail.com to admin123
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.database import SessionLocal
from app.models import User
from app.security import get_password_hash


def reset_admin_password():
    """Reset the admin password to admin123"""
    db = SessionLocal()

    try:
        # Find the user
        user = db.query(User).filter(User.email == "nateweaver94@gmail.com").first()

        if not user:
            print("❌ User nateweaver94@gmail.com not found!")
            print("Please run populate_test_data.py first to create the user.")
            return False

        # Update the password
        user.hashed_password = get_password_hash("admin123")
        db.commit()

        print("✅ Password reset successfully!")
        print("")
        print("Credentials:")
        print("  Email: nateweaver94@gmail.com")
        print("  Password: admin123")

        return True

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    reset_admin_password()
