#!/bin/bash
set -e

echo "========================================"
echo "RescueWorks Backend Startup"
echo "========================================"
echo "Build: $(date)"

# Show database connection info (masked for security)
if [ -n "$DATABASE_URL" ]; then
    # Mask the password in the URL for logging
    MASKED_URL=$(echo "$DATABASE_URL" | sed -E 's/(:\/\/[^:]+:)[^@]+(@)/\1****\2/')
    echo "Database URL: $MASKED_URL"
else
    echo "DATABASE_URL not set - using SQLite"
fi

echo ""
echo "Running database migrations..."
alembic upgrade head

# Seed database with test data if SEED_DATABASE is set to "true"
if [ "$SEED_DATABASE" = "true" ]; then
    echo ""
    echo "Seeding database with test data..."
    python seed_database.py
fi

echo ""
echo "Starting FastAPI application on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
