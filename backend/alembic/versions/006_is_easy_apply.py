"""Add is_easy_apply boolean to jobs table.

Revision ID: 006_is_easy_apply
Revises: 005_compensation_fields
"""

from alembic import op
import sqlalchemy as sa


revision = "006_is_easy_apply"
down_revision = "005_compensation_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_easy_apply column with default False
    op.add_column(
        "jobs",
        sa.Column("is_easy_apply", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Add index for filtering Easy Apply jobs
    op.create_index(
        "idx_jobs_is_easy_apply",
        "jobs",
        ["is_easy_apply"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_is_easy_apply", table_name="jobs")
    op.drop_column("jobs", "is_easy_apply")
