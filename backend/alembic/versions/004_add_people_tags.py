"""Add missing people tag columns

Revision ID: 004_add_people_tags
Revises: 003_fix_altered_status_enum
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_add_people_tags'
down_revision = '003_fix_altered_status_enum'
branch_labels = None
depends_on = None


def upgrade():
    """Add tag columns and metadata fields to people."""
    op.add_column('people', sa.Column('tag_foster_waitlist', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_do_not_foster', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_do_not_volunteer', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_has_dogs', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_has_cats', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_has_kids', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_processing_application', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('tag_owner_surrender', sa.Boolean(), nullable=True))
    op.add_column('people', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('people', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('people', sa.Column('updated_at', sa.DateTime(), nullable=True))

    op.create_foreign_key('people_user_id_fkey', 'people', 'users', ['user_id'], ['id'])


def downgrade():
    """Drop added columns from people."""
    op.drop_constraint('people_user_id_fkey', 'people', type_='foreignkey')

    op.drop_column('people', 'updated_at')
    op.drop_column('people', 'created_at')
    op.drop_column('people', 'user_id')
    op.drop_column('people', 'tag_owner_surrender')
    op.drop_column('people', 'tag_processing_application')
    op.drop_column('people', 'tag_has_kids')
    op.drop_column('people', 'tag_has_cats')
    op.drop_column('people', 'tag_has_dogs')
    op.drop_column('people', 'tag_do_not_volunteer')
    op.drop_column('people', 'tag_do_not_foster')
    op.drop_column('people', 'tag_foster_waitlist')
