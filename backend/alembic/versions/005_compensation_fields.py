"""Add compensation fields to jobs table.

Revision ID: 005_compensation_fields
Revises: 004_job_contacts
"""

from alembic import op
import sqlalchemy as sa


revision = "005_compensation_fields"
down_revision = "004_job_contacts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the employment_type enum
    op.execute(
        """
        CREATE TYPE employment_type AS ENUM (
            'full_time',
            'part_time',
            'contract',
            'contract_to_hire',
            'temporary',
            'internship'
        );
        """
    )

    # Add compensation columns to jobs table
    op.add_column("jobs", sa.Column("salary_min", sa.Integer(), nullable=True))
    op.add_column("jobs", sa.Column("salary_max", sa.Integer(), nullable=True))
    op.add_column(
        "jobs",
        sa.Column("salary_currency", sa.String(3), nullable=True, server_default="USD"),
    )
    op.add_column(
        "jobs",
        sa.Column(
            "employment_type",
            sa.Enum(
                "full_time",
                "part_time",
                "contract",
                "contract_to_hire",
                "temporary",
                "internship",
                name="employment_type",
                create_type=False,
            ),
            nullable=True,
        ),
    )

    # Add indexes for compensation queries
    op.create_index(
        "idx_jobs_salary",
        "jobs",
        ["salary_min", "salary_max"],
        postgresql_where=sa.text("salary_min IS NOT NULL AND deleted_at IS NULL"),
    )
    op.create_index(
        "idx_jobs_employment_type",
        "jobs",
        ["employment_type"],
        postgresql_where=sa.text("employment_type IS NOT NULL AND deleted_at IS NULL"),
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index("idx_jobs_employment_type", table_name="jobs")
    op.drop_index("idx_jobs_salary", table_name="jobs")

    # Drop columns
    op.drop_column("jobs", "employment_type")
    op.drop_column("jobs", "salary_currency")
    op.drop_column("jobs", "salary_max")
    op.drop_column("jobs", "salary_min")

    # Drop enum type
    op.execute("DROP TYPE employment_type")
