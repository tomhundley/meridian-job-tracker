"""Add user preference flags: is_favorite, is_perfect_fit, is_ai_forward.

Revision ID: 007_user_preference_flags
Revises: 006_is_easy_apply
"""

from alembic import op
import sqlalchemy as sa


revision = "007_user_preference_flags"
down_revision = "006_is_easy_apply"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add user preference flags
    op.add_column(
        "jobs",
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "jobs",
        sa.Column("is_perfect_fit", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "jobs",
        sa.Column("is_ai_forward", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Add indexes for filtering
    op.create_index(
        "idx_jobs_is_favorite",
        "jobs",
        ["is_favorite"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_jobs_is_perfect_fit",
        "jobs",
        ["is_perfect_fit"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_jobs_is_ai_forward",
        "jobs",
        ["is_ai_forward"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_jobs_is_ai_forward", table_name="jobs")
    op.drop_index("idx_jobs_is_perfect_fit", table_name="jobs")
    op.drop_index("idx_jobs_is_favorite", table_name="jobs")
    op.drop_column("jobs", "is_ai_forward")
    op.drop_column("jobs", "is_perfect_fit")
    op.drop_column("jobs", "is_favorite")
