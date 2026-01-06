"""Initial schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


job_status_enum = postgresql.ENUM(
    "saved",
    "researching",
    "ready_to_apply",
    "applying",
    "applied",
    "interviewing",
    "offer",
    "rejected",
    "withdrawn",
    "archived",
    name="job_status",
)

role_type_enum = postgresql.ENUM(
    "cto",
    "vp",
    "director",
    "architect",
    "developer",
    name="role_type",
)

application_method_enum = postgresql.ENUM(
    "linkedin_quick_apply",
    "linkedin_full_apply",
    "company_website",
    "email",
    "referral",
    "recruiter",
    "manual",
    name="application_method",
)


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    job_status_enum.create(op.get_bind(), checkfirst=True)
    role_type_enum.create(op.get_bind(), checkfirst=True)
    application_method_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255)),
        sa.Column("url", sa.Text()),
        sa.Column("job_board", sa.String(length=50)),
        sa.Column("job_board_id", sa.String(length=255)),
        sa.Column("description_raw", sa.Text()),
        sa.Column("source_html", sa.Text()),
        sa.Column("status", job_status_enum, nullable=False, server_default=sa.text("'saved'")),
        sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_reason", sa.String(length=100)),
        sa.Column("target_role", role_type_enum),
        sa.Column(
            "priority",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("50"),
        ),
        sa.Column("notes", sa.Text()),
        sa.Column("tags", postgresql.ARRAY(sa.Text())),
        sa.Column("application_method", application_method_enum),
        sa.Column("applied_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("priority >= 0 AND priority <= 100", name="check_priority_range"),
        sa.UniqueConstraint("job_board", "job_board_id", name="uq_job_board_id"),
    )

    op.create_table(
        "cover_letters",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("target_role", role_type_enum, nullable=False),
        sa.Column("generation_prompt", sa.Text()),
        sa.Column("model_used", sa.String(length=100)),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "emails",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("from_email", sa.String(length=255), nullable=False),
        sa.Column("to_email", sa.String(length=255)),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("email_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_inbound", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "application_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("method", application_method_enum, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("success", sa.Boolean()),
        sa.Column("error_message", sa.Text()),
        sa.Column("screenshot_path", sa.Text()),
        sa.Column("form_data", postgresql.JSONB()),
        sa.Column("requires_confirmation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("confirmed_by", sa.String(length=100)),
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("api_key", sa.String(length=255), nullable=False),
        sa.Column("permissions", postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("name", name="uq_agent_name"),
        sa.UniqueConstraint("api_key", name="uq_agent_api_key"),
    )

    op.create_table(
        "webhooks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("events", postgresql.ARRAY(sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("secret", sa.String(length=255)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )

    op.create_index("idx_jobs_status", "jobs", ["status"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_jobs_company", "jobs", ["company"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_jobs_priority", "jobs", ["priority"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_jobs_target_role", "jobs", ["target_role"], postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("idx_jobs_created_at", "jobs", ["created_at"])
    op.create_index(
        "idx_jobs_applied_at",
        "jobs",
        ["applied_at"],
        postgresql_where=sa.text("applied_at IS NOT NULL"),
    )

    op.create_index(
        "idx_cover_letters_job_id",
        "cover_letters",
        ["job_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "idx_cover_letters_is_current",
        "cover_letters",
        ["job_id", "is_current"],
        postgresql_where=sa.text("is_current = true AND deleted_at IS NULL"),
    )

    op.create_index(
        "idx_emails_job_id",
        "emails",
        ["job_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("idx_emails_timestamp", "emails", ["email_timestamp"])

    op.create_index("idx_application_attempts_job_id", "application_attempts", ["job_id"])
    op.create_index(
        "idx_application_attempts_pending",
        "application_attempts",
        ["job_id"],
        postgresql_where=sa.text("requires_confirmation = true AND confirmed_at IS NULL"),
    )

    op.create_index("idx_agents_api_key", "agents", ["api_key"])
    op.create_index(
        "idx_webhooks_active",
        "webhooks",
        ["is_active"],
        postgresql_where=sa.text("is_active = true"),
    )

    op.execute(
        """
        CREATE INDEX idx_jobs_fts ON jobs
        USING gin(
            to_tsvector(
                'english',
                COALESCE(description_raw, '') || ' ' || COALESCE(title, '') || ' ' || COALESCE(company, '')
            )
        )
        WHERE deleted_at IS NULL;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
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
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_webhooks_updated_at ON webhooks")
    op.execute("DROP TRIGGER IF EXISTS update_agents_updated_at ON agents")
    op.execute("DROP TRIGGER IF EXISTS update_emails_updated_at ON emails")
    op.execute("DROP TRIGGER IF EXISTS update_cover_letters_updated_at ON cover_letters")
    op.execute("DROP TRIGGER IF EXISTS update_jobs_updated_at ON jobs")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column")

    op.execute("DROP INDEX IF EXISTS idx_jobs_fts")

    op.drop_index("idx_webhooks_active", table_name="webhooks")
    op.drop_index("idx_agents_api_key", table_name="agents")
    op.drop_index("idx_application_attempts_pending", table_name="application_attempts")
    op.drop_index("idx_application_attempts_job_id", table_name="application_attempts")
    op.drop_index("idx_emails_timestamp", table_name="emails")
    op.drop_index("idx_emails_job_id", table_name="emails")
    op.drop_index("idx_cover_letters_is_current", table_name="cover_letters")
    op.drop_index("idx_cover_letters_job_id", table_name="cover_letters")
    op.drop_index("idx_jobs_applied_at", table_name="jobs")
    op.drop_index("idx_jobs_created_at", table_name="jobs")
    op.drop_index("idx_jobs_target_role", table_name="jobs")
    op.drop_index("idx_jobs_priority", table_name="jobs")
    op.drop_index("idx_jobs_company", table_name="jobs")
    op.drop_index("idx_jobs_status", table_name="jobs")

    op.drop_table("webhooks")
    op.drop_table("agents")
    op.drop_table("application_attempts")
    op.drop_table("emails")
    op.drop_table("cover_letters")
    op.drop_table("jobs")

    application_method_enum.drop(op.get_bind(), checkfirst=True)
    role_type_enum.drop(op.get_bind(), checkfirst=True)
    job_status_enum.drop(op.get_bind(), checkfirst=True)
