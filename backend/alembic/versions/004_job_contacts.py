"""Add job_contacts table for tracking hiring team members.

Revision ID: 004_job_contacts
Revises: 003_work_location_type
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "004_job_contacts"
down_revision = "003_work_location_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create job_contacts table
    op.create_table(
        "job_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("linkedin_url", sa.Text(), nullable=True),
        sa.Column("linkedin_member_id", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("contact_type", sa.String(50), nullable=False, server_default="recruiter"),
        sa.Column("is_job_poster", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("contacted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_received_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("job_id", "linkedin_url"),
    )

    # Create indexes
    op.create_index("idx_job_contacts_job_id", "job_contacts", ["job_id"])
    op.create_index("idx_job_contacts_linkedin_url", "job_contacts", ["linkedin_url"])
    op.create_index("idx_job_contacts_type", "job_contacts", ["contact_type"])
    op.create_index(
        "idx_job_contacts_contacted",
        "job_contacts",
        ["contacted_at"],
        postgresql_where=sa.text("contacted_at IS NOT NULL"),
    )

    # Create trigger for updated_at
    op.execute(
        """
        CREATE TRIGGER update_job_contacts_updated_at
            BEFORE UPDATE ON job_contacts
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """
    )


def downgrade() -> None:
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS update_job_contacts_updated_at ON job_contacts")

    # Drop indexes
    op.drop_index("idx_job_contacts_contacted", table_name="job_contacts")
    op.drop_index("idx_job_contacts_type", table_name="job_contacts")
    op.drop_index("idx_job_contacts_linkedin_url", table_name="job_contacts")
    op.drop_index("idx_job_contacts_job_id", table_name="job_contacts")

    # Drop table
    op.drop_table("job_contacts")
