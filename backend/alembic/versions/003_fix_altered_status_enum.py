"""Fix altered_status enum values

Revision ID: 003_fix_altered_status_enum
Revises: 002_add_pet_color_adoption_fee
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_fix_altered_status_enum'
down_revision = '002_add_pet_color_adoption_fee'
branch_labels = None
depends_on = None


def upgrade():
    """
    Fix the alteredstatus enum to use 'yes', 'no', 'unsure' instead of
    'altered', 'not_altered', 'unknown' to match the application code.
    """
    # Step 1: Alter the column to use VARCHAR temporarily
    op.execute("ALTER TABLE pets ALTER COLUMN altered_status TYPE VARCHAR USING altered_status::text")

    # Step 2: Drop the old enum type
    op.execute("DROP TYPE alteredstatus")

    # Step 3: Create the new enum type with correct values
    op.execute("CREATE TYPE alteredstatus AS ENUM ('yes', 'no', 'unsure')")

    # Step 4: Convert the column back to use the new enum
    # Update any existing data to use the new values
    op.execute("UPDATE pets SET altered_status = 'yes' WHERE altered_status = 'altered'")
    op.execute("UPDATE pets SET altered_status = 'no' WHERE altered_status = 'not_altered'")
    op.execute("UPDATE pets SET altered_status = 'unsure' WHERE altered_status = 'unknown'")

    # Step 5: Alter the column to use the new enum type
    op.execute("ALTER TABLE pets ALTER COLUMN altered_status TYPE alteredstatus USING altered_status::alteredstatus")


def downgrade():
    """
    Revert the alteredstatus enum back to original values.
    """
    # Step 1: Alter the column to use VARCHAR temporarily
    op.execute("ALTER TABLE pets ALTER COLUMN altered_status TYPE VARCHAR USING altered_status::text")

    # Step 2: Drop the new enum type
    op.execute("DROP TYPE alteredstatus")

    # Step 3: Create the old enum type
    op.execute("CREATE TYPE alteredstatus AS ENUM ('altered', 'not_altered', 'unknown')")

    # Step 4: Convert any data back to old values
    op.execute("UPDATE pets SET altered_status = 'altered' WHERE altered_status = 'yes'")
    op.execute("UPDATE pets SET altered_status = 'not_altered' WHERE altered_status = 'no'")
    op.execute("UPDATE pets SET altered_status = 'unknown' WHERE altered_status = 'unsure'")

    # Step 5: Alter the column to use the old enum type
    op.execute("ALTER TABLE pets ALTER COLUMN altered_status TYPE alteredstatus USING altered_status::alteredstatus")
