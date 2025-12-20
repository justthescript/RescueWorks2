"""Initial schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Initial migration creates all tables for RescueWorks.
    This migration represents the baseline schema for all sprints (1-4).
    """

    # Organizations table
    op.create_table('organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('logo_url', sa.String(), nullable=True),
        sa.Column('primary_contact_email', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)

    # Users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Roles table
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    # User Roles table
    op.create_table('user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Token Blacklist table
    op.create_table('token_blacklist',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('blacklisted_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_blacklist_token'), 'token_blacklist', ['token'], unique=True)

    # Refresh Tokens table
    op.create_table('refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_tokens_token'), 'refresh_tokens', ['token'], unique=True)

    # Pets table
    op.create_table('pets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('species', sa.String(), nullable=False),
        sa.Column('breed', sa.String(), nullable=True),
        sa.Column('sex', sa.String(), nullable=True),
        sa.Column('intake_date', sa.Date(), nullable=True),
        sa.Column('microchip_number', sa.String(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('altered_status', sa.Enum('yes', 'no', 'unsure', name='alteredstatus'), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('intake', 'needs_foster', 'in_foster', 'available', 'pending', 'adopted', 'medical_hold', name='petstatus'), nullable=True),
        sa.Column('description_public', sa.Text(), nullable=True),
        sa.Column('description_internal', sa.Text(), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True),
        sa.Column('foster_user_id', sa.Integer(), nullable=True),
        sa.Column('adopter_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['adopter_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['foster_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Applications table
    op.create_table('applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('applicant_user_id', sa.Integer(), nullable=True),
        sa.Column('applicant_person_id', sa.Integer(), nullable=True),
        sa.Column('pet_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.Enum('adoption', 'foster', 'volunteer', 'board', name='applicationtype'), nullable=False),
        sa.Column('status', sa.Enum('submitted', 'under_review', 'interview_scheduled', 'approved', 'denied', name='applicationstatus'), nullable=True),
        sa.Column('answers_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['applicant_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Foster Profiles table
    op.create_table('foster_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('experience_level', sa.Enum('none', 'beginner', 'intermediate', 'advanced', name='fosterexperiencelevel'), nullable=True),
        sa.Column('preferred_species', sa.String(), nullable=True),
        sa.Column('preferred_ages', sa.String(), nullable=True),
        sa.Column('max_capacity', sa.Integer(), nullable=True),
        sa.Column('current_capacity', sa.Integer(), nullable=True),
        sa.Column('home_type', sa.Enum('house', 'apartment', 'condo', 'townhouse', 'other', name='hometype'), nullable=True),
        sa.Column('has_yard', sa.Boolean(), nullable=True),
        sa.Column('has_other_pets', sa.Boolean(), nullable=True),
        sa.Column('other_pets_description', sa.Text(), nullable=True),
        sa.Column('has_children', sa.Boolean(), nullable=True),
        sa.Column('children_ages', sa.String(), nullable=True),
        sa.Column('can_handle_medical', sa.Boolean(), nullable=True),
        sa.Column('can_handle_behavioral', sa.Boolean(), nullable=True),
        sa.Column('training_completed', sa.Text(), nullable=True),
        sa.Column('certifications', sa.Text(), nullable=True),
        sa.Column('available_from', sa.DateTime(), nullable=True),
        sa.Column('available_until', sa.DateTime(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.Column('total_fosters', sa.Integer(), nullable=True),
        sa.Column('successful_adoptions', sa.Integer(), nullable=True),
        sa.Column('avg_foster_duration_days', sa.Float(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('background_check_status', sa.String(), nullable=True),
        sa.Column('background_check_date', sa.DateTime(), nullable=True),
        sa.Column('insurance_verified', sa.Boolean(), nullable=True),
        sa.Column('references_checked', sa.Boolean(), nullable=True),
        sa.Column('notes_internal', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Foster Placements table
    op.create_table('foster_placements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('foster_profile_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('outcome', sa.Enum('active', 'adopted', 'returned', 'transferred', name='placementoutcome'), nullable=True),
        sa.Column('success_reason', sa.Text(), nullable=True),
        sa.Column('return_reason', sa.Text(), nullable=True),
        sa.Column('agreement_signed', sa.Boolean(), nullable=True),
        sa.Column('agreement_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['foster_profile_id'], ['foster_profiles.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Foster Placement Notes table
    op.create_table('foster_placement_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('placement_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(), nullable=True),
        sa.Column('is_important', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['placement_id'], ['foster_placements.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # People table
    op.create_table('people',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('street_1', sa.String(), nullable=True),
        sa.Column('street_2', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('zip_code', sa.String(), nullable=True),
        sa.Column('tag_adopter', sa.Boolean(), nullable=True),
        sa.Column('tag_potential_adopter', sa.Boolean(), nullable=True),
        sa.Column('tag_adopt_waitlist', sa.Boolean(), nullable=True),
        sa.Column('tag_do_not_adopt', sa.Boolean(), nullable=True),
        sa.Column('tag_foster', sa.Boolean(), nullable=True),
        sa.Column('tag_available_foster', sa.Boolean(), nullable=True),
        sa.Column('tag_current_foster', sa.Boolean(), nullable=True),
        sa.Column('tag_dormant_foster', sa.Boolean(), nullable=True),
        sa.Column('tag_volunteer', sa.Boolean(), nullable=True),
        sa.Column('tag_donor', sa.Boolean(), nullable=True),
        sa.Column('tag_board_member', sa.Boolean(), nullable=True),
        sa.Column('tag_staff', sa.Boolean(), nullable=True),
        sa.Column('tag_vendor', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Additional tables (Tasks, Events, Payments, Expenses, etc.)
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('open', 'in_progress', 'completed', 'archived', name='taskstatus'), nullable=True),
        sa.Column('priority', sa.Enum('low', 'normal', 'high', 'urgent', name='taskpriority'), nullable=True),
        sa.Column('assigned_to_user_id', sa.Integer(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('expense_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('date_incurred', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('vendor_name', sa.String(), nullable=True),
        sa.Column('recorded_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['expense_categories.id'], ),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['recorded_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('pet_id', sa.Integer(), nullable=True),
        sa.Column('purpose', sa.Enum('adoption_fee', 'donation', 'event_ticket', 'reimbursement', 'other', name='paymentpurpose'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('gateway_payment_id', sa.String(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', 'refunded', 'canceled', name='paymentstatus'), nullable=True),
        sa.Column('status_detail', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('organization_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('org_id', sa.Integer(), nullable=False),
        sa.Column('email_provider', sa.String(), nullable=True),
        sa.Column('email_api_key', sa.String(), nullable=True),
        sa.Column('sms_provider', sa.String(), nullable=True),
        sa.Column('sms_api_key', sa.String(), nullable=True),
        sa.Column('stripe_public_key', sa.String(), nullable=True),
        sa.Column('stripe_secret_key', sa.String(), nullable=True),
        sa.Column('paypal_client_id', sa.String(), nullable=True),
        sa.Column('paypal_secret', sa.String(), nullable=True),
        sa.Column('petfinder_api_key', sa.String(), nullable=True),
        sa.Column('petfinder_secret', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_settings_org_id'), 'organization_settings', ['org_id'], unique=True)


def downgrade():
    """Drop all tables"""
    op.drop_table('organization_settings')
    op.drop_table('payments')
    op.drop_table('expenses')
    op.drop_table('expense_categories')
    op.drop_table('tasks')
    op.drop_table('people')
    op.drop_table('foster_placement_notes')
    op.drop_table('foster_placements')
    op.drop_table('foster_profiles')
    op.drop_table('applications')
    op.drop_table('pets')
    op.drop_table('refresh_tokens')
    op.drop_table('token_blacklist')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('organizations')
