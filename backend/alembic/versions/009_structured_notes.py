"""Convert notes from Text to JSONB array.

Revision ID: 009_structured_notes
Revises: 008_location_compatible
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "009_structured_notes"
down_revision = "008_location_compatible"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new JSONB column for structured notes
    op.add_column(
        "jobs",
        sa.Column(
            "notes_structured",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            server_default="[]",
        ),
    )

    # Migrate existing text notes to structured format
    # Each existing note becomes: [{"text": old_note, "timestamp": now, "source": "user"}]
    op.execute("""
        UPDATE jobs
        SET notes_structured = jsonb_build_array(
            jsonb_build_object(
                'text', notes,
                'timestamp', to_char(COALESCE(updated_at, created_at), 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
                'source', 'user'
            )
        )
        WHERE notes IS NOT NULL AND notes != '';
    """)

    # Drop old notes column
    op.drop_column("jobs", "notes")

    # Rename notes_structured to notes
    op.alter_column("jobs", "notes_structured", new_column_name="notes")


def downgrade() -> None:
    # Rename notes back to notes_structured
    op.alter_column("jobs", "notes", new_column_name="notes_structured")

    # Add back the text notes column
    op.add_column(
        "jobs",
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # Extract first note text from structured notes
    op.execute("""
        UPDATE jobs
        SET notes = notes_structured->0->>'text'
        WHERE notes_structured IS NOT NULL
          AND jsonb_array_length(notes_structured) > 0;
    """)

    # Drop the structured notes column
    op.drop_column("jobs", "notes_structured")
