"""Add decline reasons lookup tables and job columns.

Revision ID: 002_decline_reasons
Revises: 001_initial
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "002_decline_reasons"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user decline reasons lookup table
    op.create_table(
        "user_decline_reasons",
        sa.Column("code", sa.String(length=50), primary_key=True),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Create company decline reasons lookup table
    op.create_table(
        "company_decline_reasons",
        sa.Column("code", sa.String(length=50), primary_key=True),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # Add indexes for category grouping
    op.create_index(
        "idx_user_decline_category",
        "user_decline_reasons",
        ["category", "sort_order"],
    )
    op.create_index(
        "idx_company_decline_category",
        "company_decline_reasons",
        ["category", "sort_order"],
    )

    # Add columns to jobs table
    op.add_column(
        "jobs",
        sa.Column("user_decline_reasons", postgresql.ARRAY(sa.String(50))),
    )
    op.add_column(
        "jobs",
        sa.Column("company_decline_reasons", postgresql.ARRAY(sa.String(50))),
    )
    op.add_column(
        "jobs",
        sa.Column("decline_notes", sa.Text()),
    )

    # Add GIN indexes for array columns
    op.execute(
        """
        CREATE INDEX idx_jobs_user_decline ON jobs USING gin(user_decline_reasons)
        WHERE user_decline_reasons IS NOT NULL;
        """
    )
    op.execute(
        """
        CREATE INDEX idx_jobs_company_decline ON jobs USING gin(company_decline_reasons)
        WHERE company_decline_reasons IS NOT NULL;
        """
    )

    # Seed user decline reasons
    op.execute(
        """
        INSERT INTO user_decline_reasons (code, display_name, category, sort_order) VALUES
        -- Compensation
        ('salary_too_low', 'Salary below expectations', 'compensation', 1),
        ('benefits_inadequate', 'Benefits not competitive', 'compensation', 2),
        ('no_equity', 'No equity/stock options', 'compensation', 3),
        -- Location & Remote
        ('not_remote', 'Not fully remote', 'location', 1),
        ('wrong_location', 'Location not suitable', 'location', 2),
        ('commute_too_long', 'Commute too long', 'location', 3),
        ('relocation_required', 'Would require relocation', 'location', 4),
        -- Role Fit
        ('underqualified', 'Not qualified for role', 'role_fit', 1),
        ('overqualified', 'Role below experience level', 'role_fit', 2),
        ('wrong_responsibilities', 'Job duties not aligned', 'role_fit', 3),
        ('wrong_industry', 'Industry not of interest', 'role_fit', 4),
        ('wrong_tech_stack', 'Technology stack not preferred', 'role_fit', 5),
        -- Company Concerns
        ('culture_concerns', 'Company culture red flags', 'company', 1),
        ('bad_reviews', 'Negative Glassdoor/reviews', 'company', 2),
        ('company_too_small', 'Company too small', 'company', 3),
        ('company_too_large', 'Company too large', 'company', 4),
        ('financial_instability', 'Company financial concerns', 'company', 5),
        ('recent_layoffs', 'Recent layoffs or instability', 'company', 6),
        -- Process Issues
        ('slow_process', 'Hiring process too slow', 'process', 1),
        ('poor_communication', 'Poor recruiter communication', 'process', 2),
        ('bad_interview', 'Negative interview experience', 'process', 3),
        -- Personal
        ('found_better', 'Found better opportunity', 'personal', 1),
        ('timing_not_right', 'Timing not right', 'personal', 2),
        ('bad_feeling', 'Gut feeling / intuition', 'personal', 3),
        ('lost_interest', 'Lost interest in role', 'personal', 4),
        ('other', 'Other reason', 'personal', 99);
        """
    )

    # Seed company decline reasons
    op.execute(
        """
        INSERT INTO company_decline_reasons (code, display_name, category, sort_order) VALUES
        -- Candidate Selection
        ('selected_other', 'Selected another candidate', 'selection', 1),
        ('position_filled_internal', 'Filled internally', 'selection', 2),
        ('position_closed', 'Position closed/budget cut', 'selection', 3),
        -- Experience & Skills
        ('insufficient_experience', 'Not enough experience', 'experience', 1),
        ('overqualified', 'Overqualified', 'experience', 2),
        ('skills_mismatch', 'Skills don''t match requirements', 'experience', 3),
        ('failed_technical', 'Did not pass technical assessment', 'experience', 4),
        -- Fit & Expectations
        ('culture_fit', 'Not a culture fit', 'fit', 1),
        ('salary_too_high', 'Salary expectations too high', 'fit', 2),
        ('availability_issues', 'Start date/availability issues', 'fit', 3),
        -- Verification
        ('background_check', 'Background check issue', 'verification', 1),
        ('reference_issue', 'Reference check concern', 'verification', 2),
        -- Interview
        ('interview_performance', 'Interview performance', 'interview', 1),
        ('communication_concerns', 'Communication concerns', 'interview', 2),
        -- Other
        ('ghosted', 'No response / ghosted', 'other', 1),
        ('generic_rejection', 'Generic "not moving forward"', 'other', 2),
        ('other', 'Other reason', 'other', 99);
        """
    )


def downgrade() -> None:
    # Drop indexes on jobs
    op.execute("DROP INDEX IF EXISTS idx_jobs_company_decline")
    op.execute("DROP INDEX IF EXISTS idx_jobs_user_decline")

    # Drop columns from jobs
    op.drop_column("jobs", "decline_notes")
    op.drop_column("jobs", "company_decline_reasons")
    op.drop_column("jobs", "user_decline_reasons")

    # Drop indexes on lookup tables
    op.drop_index("idx_company_decline_category", table_name="company_decline_reasons")
    op.drop_index("idx_user_decline_category", table_name="user_decline_reasons")

    # Drop lookup tables
    op.drop_table("company_decline_reasons")
    op.drop_table("user_decline_reasons")
