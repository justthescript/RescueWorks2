-- Migration: Add Foster Coordinator Features
-- This migration adds comprehensive foster management capabilities including:
-- 1. Foster profiles with detailed information
-- 2. Foster placements tracking
-- 3. Enhanced pet-foster relationship management

-- ============================================================================
-- CREATE ENUM TYPES
-- ============================================================================

-- Foster experience level enum
-- Note: If using PostgreSQL, uncomment these. For SQLite, enums are handled by SQLAlchemy
-- CREATE TYPE foster_experience_level AS ENUM ('none', 'beginner', 'intermediate', 'advanced');
-- CREATE TYPE home_type AS ENUM ('house', 'apartment', 'condo', 'townhouse', 'other');
-- CREATE TYPE placement_outcome AS ENUM ('active', 'adopted', 'returned', 'transferred');

-- ============================================================================
-- CREATE FOSTER PROFILES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS foster_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    org_id INTEGER NOT NULL,

    -- Experience and preferences
    experience_level VARCHAR(20) DEFAULT 'none',
    preferred_species VARCHAR(255),
    preferred_ages VARCHAR(255),
    max_capacity INTEGER DEFAULT 1,
    current_capacity INTEGER DEFAULT 0,

    -- Home information
    home_type VARCHAR(20),
    has_yard BOOLEAN DEFAULT 0,
    has_other_pets BOOLEAN DEFAULT 0,
    other_pets_description TEXT,
    has_children BOOLEAN DEFAULT 0,
    children_ages VARCHAR(255),

    -- Qualifications
    can_handle_medical BOOLEAN DEFAULT 0,
    can_handle_behavioral BOOLEAN DEFAULT 0,
    training_completed TEXT,
    certifications TEXT,

    -- Availability
    available_from DATETIME,
    available_until DATETIME,
    is_available BOOLEAN DEFAULT 1,

    -- Performance metrics
    total_fosters INTEGER DEFAULT 0,
    successful_adoptions INTEGER DEFAULT 0,
    avg_foster_duration_days REAL,
    rating REAL,

    -- Admin fields
    background_check_status VARCHAR(20),
    background_check_date DATETIME,
    insurance_verified BOOLEAN DEFAULT 0,
    references_checked BOOLEAN DEFAULT 0,
    notes_internal TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id)
);

-- ============================================================================
-- CREATE FOSTER PLACEMENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS foster_placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    pet_id INTEGER NOT NULL,
    foster_profile_id INTEGER NOT NULL,

    -- Placement details
    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expected_end_date DATETIME,
    actual_end_date DATETIME,
    outcome VARCHAR(20) DEFAULT 'active',

    -- Placement metadata
    placement_notes TEXT,
    return_reason TEXT,
    success_notes TEXT,

    -- Agreement and documentation
    agreement_signed BOOLEAN DEFAULT 0,
    agreement_signed_date DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (pet_id) REFERENCES pets(id),
    FOREIGN KEY (foster_profile_id) REFERENCES foster_profiles(id)
);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_foster_profiles_user_id ON foster_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_foster_profiles_org_id ON foster_profiles(org_id);
CREATE INDEX IF NOT EXISTS idx_foster_profiles_is_available ON foster_profiles(is_available);

CREATE INDEX IF NOT EXISTS idx_foster_placements_pet_id ON foster_placements(pet_id);
CREATE INDEX IF NOT EXISTS idx_foster_placements_foster_profile_id ON foster_placements(foster_profile_id);
CREATE INDEX IF NOT EXISTS idx_foster_placements_org_id ON foster_placements(org_id);
CREATE INDEX IF NOT EXISTS idx_foster_placements_outcome ON foster_placements(outcome);

-- ============================================================================
-- NOTES
-- ============================================================================

-- This migration adds the following tables:
--
-- 1. foster_profiles
--    - Stores detailed information about foster caregivers
--    - Tracks experience, preferences, home environment, and qualifications
--    - Maintains performance metrics and availability status
--
-- 2. foster_placements
--    - Records the history of pet-foster pairings
--    - Tracks placement duration, outcomes, and notes
--    - Supports workflow management including agreement tracking
--
-- The enhanced matching algorithm uses data from both tables to:
--    - Match pets with compatible fosters based on multiple criteria
--    - Balance workload across available fosters
--    - Consider experience levels and special needs
--    - Track success rates and improve matching over time
