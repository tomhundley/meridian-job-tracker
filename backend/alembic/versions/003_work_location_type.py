"""Add work_location_type column to jobs table.

Revision ID: 003_work_location_type
Revises: 002_decline_reasons
"""

from alembic import op
import sqlalchemy as sa


revision = "003_work_location_type"
down_revision = "002_decline_reasons"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum type
    op.execute(
        """
        CREATE TYPE work_location_type AS ENUM ('remote', 'hybrid', 'on_site');
        """
    )

    # Add column to jobs table
    op.add_column(
        "jobs",
        sa.Column(
            "work_location_type",
            sa.Enum("remote", "hybrid", "on_site", name="work_location_type", create_type=False),
            nullable=True,
        ),
    )

    # Add index for filtering by work location type
    op.create_index(
        "idx_jobs_work_location_type",
        "jobs",
        ["work_location_type"],
        postgresql_where=sa.text("work_location_type IS NOT NULL"),
    )


def downgrade() -> None:
    # Drop index
    op.drop_index("idx_jobs_work_location_type", table_name="jobs")

    # Drop column
    op.drop_column("jobs", "work_location_type")

    # Drop enum type
    op.execute("DROP TYPE work_location_type")
