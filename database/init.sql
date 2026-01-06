-- Meridian Job Tracker Database Schema
-- PostgreSQL 16

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enums
CREATE TYPE job_status AS ENUM (
    'saved',
    'researching',
    'ready_to_apply',
    'applying',
    'applied',
    'interviewing',
    'offer',
    'rejected',
    'withdrawn',
    'archived'
);

CREATE TYPE role_type AS ENUM (
    'cto',
    'vp',
    'director',
    'architect',
    'developer'
);

CREATE TYPE application_method AS ENUM (
    'linkedin_quick_apply',
    'linkedin_full_apply',
    'company_website',
    'email',
    'referral',
    'recruiter',
    'manual'
);

-- Jobs table
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Core job info
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    url TEXT,
    job_board VARCHAR(50),
    job_board_id VARCHAR(255),

    -- Job description
    description_raw TEXT,
    source_html TEXT,

    -- Status tracking
    status job_status NOT NULL DEFAULT 'saved',
    status_changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_reason VARCHAR(100),

    -- Role matching
    target_role role_type,

    -- Priority and organization
    priority INTEGER NOT NULL DEFAULT 50 CHECK (priority >= 0 AND priority <= 100),
    notes TEXT,
    tags TEXT[],

    -- Application details
    application_method application_method,
    applied_at TIMESTAMPTZ,

    -- Decline tracking (arrays for multiple reasons)
    user_decline_reasons VARCHAR(50)[],
    company_decline_reasons VARCHAR(50)[],
    decline_notes TEXT,

    -- Soft delete
    deleted_at TIMESTAMPTZ,

    -- Unique constraint to prevent duplicates
    UNIQUE NULLS NOT DISTINCT (job_board, job_board_id)
);

-- Cover letters table
CREATE TABLE cover_letters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Content
    content TEXT NOT NULL,

    -- Generation metadata
    target_role role_type NOT NULL,
    generation_prompt TEXT,
    model_used VARCHAR(100),

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_current BOOLEAN NOT NULL DEFAULT true,

    -- Approval status
    is_approved BOOLEAN NOT NULL DEFAULT false,
    approved_at TIMESTAMPTZ,

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

-- Emails table (from external email agent)
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Email metadata
    from_email VARCHAR(255) NOT NULL,
    to_email VARCHAR(255),
    subject VARCHAR(500) NOT NULL,
    body TEXT,

    -- Timestamp of the email
    email_timestamp TIMESTAMPTZ NOT NULL,

    -- Tracking
    is_inbound BOOLEAN NOT NULL DEFAULT true,

    -- Soft delete
    deleted_at TIMESTAMPTZ
);

-- Application attempts (for tracking automation)
CREATE TABLE application_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Attempt details
    method application_method NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,

    -- Status
    success BOOLEAN,
    error_message TEXT,

    -- Automation details
    screenshot_path TEXT,
    form_data JSONB,

    -- Human confirmation
    requires_confirmation BOOLEAN NOT NULL DEFAULT false,
    confirmed_at TIMESTAMPTZ,
    confirmed_by VARCHAR(100)
);

-- Agents table (API keys with permissions)
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    name VARCHAR(200) NOT NULL UNIQUE,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Webhooks table
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    url TEXT NOT NULL,
    events TEXT[] NOT NULL DEFAULT '{}',
    secret VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- User decline reasons lookup table
CREATE TABLE user_decline_reasons (
    code VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Company decline reasons lookup table
CREATE TABLE company_decline_reasons (
    code VARCHAR(50) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed user decline reasons
INSERT INTO user_decline_reasons (code, display_name, category, sort_order) VALUES
-- Compensation
('salary_too_low', 'Salary below expectations', 'compensation', 1),
('benefits_inadequate', 'Benefits not competitive', 'compensation', 2),
('no_equity', 'No equity/stock options', 'compensation', 3),
-- Location & Remote
('not_remote', 'Not fully remote (hybrid/onsite required)', 'location', 10),
('wrong_location', 'Location not suitable', 'location', 11),
('commute_too_long', 'Commute too long', 'location', 12),
('relocation_required', 'Would require relocation', 'location', 13),
-- Role Fit
('underqualified', 'Not qualified for role', 'role_fit', 20),
('overqualified', 'Role below experience level', 'role_fit', 21),
('wrong_responsibilities', 'Job duties not aligned with goals', 'role_fit', 22),
('wrong_industry', 'Industry not of interest', 'role_fit', 23),
('wrong_tech_stack', 'Technology stack not preferred', 'role_fit', 24),
-- Company Concerns
('culture_concerns', 'Company culture red flags', 'company', 30),
('bad_reviews', 'Negative Glassdoor/reviews', 'company', 31),
('company_too_small', 'Company too small', 'company', 32),
('company_too_large', 'Company too large', 'company', 33),
('financial_instability', 'Company financial concerns', 'company', 34),
('recent_layoffs', 'Recent layoffs or instability', 'company', 35),
-- Process Issues
('slow_process', 'Hiring process too slow', 'process', 40),
('poor_communication', 'Poor recruiter communication', 'process', 41),
('bad_interview', 'Negative interview experience', 'process', 42),
-- Personal
('found_better', 'Found better opportunity', 'personal', 50),
('timing_not_right', 'Timing not right', 'personal', 51),
('bad_feeling', 'Gut feeling / intuition', 'personal', 52),
('lost_interest', 'Lost interest in role', 'personal', 53),
('other', 'Other reason', 'personal', 99);

-- Seed company decline reasons
INSERT INTO company_decline_reasons (code, display_name, category, sort_order) VALUES
-- Candidate Selection
('selected_other', 'Selected another candidate', 'selection', 1),
('position_filled_internal', 'Filled internally', 'selection', 2),
('position_closed', 'Position closed/budget cut', 'selection', 3),
-- Experience & Skills
('insufficient_experience', 'Not enough experience', 'experience', 10),
('overqualified', 'Overqualified', 'experience', 11),
('skills_mismatch', 'Skills don''t match requirements', 'experience', 12),
('failed_technical', 'Did not pass technical assessment', 'experience', 13),
-- Fit & Expectations
('culture_fit', 'Not a culture fit', 'fit', 20),
('salary_too_high', 'Salary expectations too high', 'fit', 21),
('availability_issues', 'Start date/availability issues', 'fit', 22),
-- Verification
('background_check', 'Background check issue', 'verification', 30),
('reference_issue', 'Reference check concern', 'verification', 31),
-- Interview
('interview_performance', 'Interview performance', 'interview', 40),
('communication_concerns', 'Communication concerns', 'interview', 41),
-- Other
('ghosted', 'No response / ghosted', 'other', 50),
('generic_rejection', 'Generic "not moving forward"', 'other', 51),
('other', 'Other reason', 'other', 99);

-- Indexes
CREATE INDEX idx_jobs_status ON jobs(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_company ON jobs(company) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_priority ON jobs(priority DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_target_role ON jobs(target_role) WHERE deleted_at IS NULL;
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
CREATE INDEX idx_jobs_applied_at ON jobs(applied_at DESC) WHERE applied_at IS NOT NULL;

CREATE INDEX idx_cover_letters_job_id ON cover_letters(job_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_cover_letters_is_current ON cover_letters(job_id, is_current) WHERE is_current = true AND deleted_at IS NULL;

CREATE INDEX idx_emails_job_id ON emails(job_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_emails_timestamp ON emails(email_timestamp DESC);

CREATE INDEX idx_application_attempts_job_id ON application_attempts(job_id);
CREATE INDEX idx_application_attempts_pending ON application_attempts(job_id) WHERE requires_confirmation = true AND confirmed_at IS NULL;

CREATE INDEX idx_agents_api_key ON agents(api_key);
CREATE INDEX idx_webhooks_active ON webhooks(is_active) WHERE is_active = true;

CREATE INDEX idx_user_decline_category ON user_decline_reasons(category, sort_order);
CREATE INDEX idx_company_decline_category ON company_decline_reasons(category, sort_order);
CREATE INDEX idx_jobs_user_decline ON jobs USING gin(user_decline_reasons) WHERE user_decline_reasons IS NOT NULL;
CREATE INDEX idx_jobs_company_decline ON jobs USING gin(company_decline_reasons) WHERE company_decline_reasons IS NOT NULL;

-- Full text search on job descriptions
CREATE INDEX idx_jobs_fts ON jobs
    USING gin(to_tsvector('english', COALESCE(description_raw, '') || ' ' || COALESCE(title, '') || ' ' || COALESCE(company, '')))
    WHERE deleted_at IS NULL;

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cover_letters_updated_at
    BEFORE UPDATE ON cover_letters
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emails_updated_at
    BEFORE UPDATE ON emails
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agents_updated_at
    BEFORE UPDATE ON agents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhooks_updated_at
    BEFORE UPDATE ON webhooks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update status_changed_at when status changes
CREATE OR REPLACE FUNCTION update_status_changed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        NEW.status_changed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_jobs_status_changed_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_status_changed_at();

-- Comments for documentation
COMMENT ON TABLE jobs IS 'Job postings being tracked for applications';
COMMENT ON TABLE cover_letters IS 'Generated cover letters for job applications';
COMMENT ON TABLE emails IS 'Email correspondence related to job applications';
COMMENT ON TABLE application_attempts IS 'Automation attempts for job applications';

COMMENT ON COLUMN jobs.priority IS '0-100 scale, higher = more important';
COMMENT ON COLUMN jobs.status IS 'Current status in the application pipeline';
COMMENT ON COLUMN jobs.user_decline_reasons IS 'Array of reason codes when user passes on a job';
COMMENT ON COLUMN jobs.company_decline_reasons IS 'Array of reason codes when company rejects user';
COMMENT ON COLUMN jobs.decline_notes IS 'Additional notes about the decline';
COMMENT ON COLUMN cover_letters.is_current IS 'Whether this is the current version for the job';
COMMENT ON COLUMN application_attempts.requires_confirmation IS 'Whether human confirmation is needed before submitting';

COMMENT ON TABLE user_decline_reasons IS 'Lookup table for reasons user passes on a job';
COMMENT ON TABLE company_decline_reasons IS 'Lookup table for reasons company rejects user';
