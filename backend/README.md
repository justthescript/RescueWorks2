# RescueWorks Backend

FastAPI based backend for the RescueWorks multi tenant rescue management platform.

This backend exposes JSON APIs for:

- Organizations and users
- Pets and applications
- Medical records and appointments
- Events and signups
- Tasks
- Expenses and categories
- Messaging
- Payments and coupons

See ../frontend for a React dashboard that consumes these APIs.

## Database Setup

### Migrations

Database migrations are managed with Alembic and run automatically on startup via `start.sh`.

### Test Data Seeding

To populate the database with test data for development and testing:

1. Set the environment variable `SEED_DATABASE=true`
2. On Railway: Add this to your service environment variables
3. Local development: Add to your `.env` file

The seed script (`seed_database.py`) creates:
- Sample organization (Pawsitive Rescue)
- Test users with different roles:
  - `admin@pawsitiverescue.org` (Admin)
  - `staff@pawsitiverescue.org` (Staff)
  - `sarah.foster@example.com` (Advanced Foster)
  - `mike.foster@example.com` (Intermediate Foster)
  - `emma.foster@example.com` (Advanced Foster)
- Sample pets in various statuses (available, in foster, needs foster, etc.)
- Foster placements
- Expense categories and sample expenses
- People (potential adopters)
- Sample tasks

**All test accounts use password: `password123`**

To run the seed script manually:
```bash
python seed_database.py
```
