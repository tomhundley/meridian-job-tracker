"""Add RAG fields to cover_letters table.

Revision ID: 010
Revises: 009_structured_notes
Create Date: 2025-01-07

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "010_cover_letter_rag"
down_revision: str | None = "009_structured_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add rag_evidence and rag_context_used columns to cover_letters."""
    op.add_column(
        "cover_letters",
        sa.Column("rag_evidence", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "cover_letters",
        sa.Column("rag_context_used", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    """Remove RAG columns from cover_letters."""
    op.drop_column("cover_letters", "rag_context_used")
    op.drop_column("cover_letters", "rag_evidence")
