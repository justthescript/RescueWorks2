"""Add missing task relationship columns

Revision ID: 005_add_task_relationship_columns
Revises: 004_add_people_tags
Create Date: 2025-12-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_task_relationship_columns'
down_revision = '004_add_people_tags'
branch_labels = None
depends_on = None


def upgrade():
    """Add missing task relationship columns."""
    op.add_column('tasks', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('related_pet_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('related_application_id', sa.Integer(), nullable=True))
    op.add_column('tasks', sa.Column('related_event_id', sa.Integer(), nullable=True))

    op.create_foreign_key('tasks_created_by_user_id_fkey', 'tasks', 'users', ['created_by_user_id'], ['id'])
    op.create_foreign_key('tasks_related_pet_id_fkey', 'tasks', 'pets', ['related_pet_id'], ['id'])
    op.create_foreign_key(
        'tasks_related_application_id_fkey',
        'tasks',
        'applications',
        ['related_application_id'],
        ['id'],
    )


def downgrade():
    """Drop task relationship columns."""
    op.drop_constraint('tasks_related_application_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_related_pet_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tasks_created_by_user_id_fkey', 'tasks', type_='foreignkey')

    op.drop_column('tasks', 'related_event_id')
    op.drop_column('tasks', 'related_application_id')
    op.drop_column('tasks', 'related_pet_id')
    op.drop_column('tasks', 'created_by_user_id')
