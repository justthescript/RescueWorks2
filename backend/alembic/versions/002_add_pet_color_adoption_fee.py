"""Add color and adoption_fee to pets table

Revision ID: 002_add_pet_color_adoption_fee
Revises: 001_initial_schema
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_pet_color_adoption_fee'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing color and adoption_fee columns to pets table"""
    # Add color column
    op.add_column('pets', sa.Column('color', sa.String(), nullable=True))

    # Add adoption_fee column
    op.add_column('pets', sa.Column('adoption_fee', sa.Float(), nullable=True))


def downgrade():
    """Remove color and adoption_fee columns from pets table"""
    op.drop_column('pets', 'adoption_fee')
    op.drop_column('pets', 'color')
