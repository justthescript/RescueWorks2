#!/usr/bin/env python3
"""Initialize the database with the correct schema."""
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import Base, engine
from app import models  # noqa: F401

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
print(f"Database location: {engine.url}")
