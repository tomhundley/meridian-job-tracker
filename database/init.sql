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
COMMENT ON COLUMN cover_letters.is_current IS 'Whether this is the current version for the job';
COMMENT ON COLUMN application_attempts.requires_confirmation IS 'Whether human confirmation is needed before submitting';
