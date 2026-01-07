"""Add is_location_compatible field for location validation.

Revision ID: 008_location_compatible
Revises: 007_user_preference_flags
"""

from alembic import op
import sqlalchemy as sa


revision = "008_location_compatible"
down_revision = "007_user_preference_flags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_location_compatible column with default True
    # (existing jobs assumed compatible until re-analyzed)
    op.add_column(
        "jobs",
        sa.Column(
            "is_location_compatible",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
    )

    # Add index for filtering incompatible jobs
    op.create_index(
        "idx_jobs_location_compatible",
        "jobs",
        ["is_location_compatible"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_location_compatible", table_name="jobs")
    op.drop_column("jobs", "is_location_compatible")
