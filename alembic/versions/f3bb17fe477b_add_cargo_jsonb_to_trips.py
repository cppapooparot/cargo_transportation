
"""add cargo jsonb to trips

Revision ID: f3bb17fe477b
Revises: 1a4df9631f8e
Create Date: 2025-12-31 10:32:26.664952

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f3bb17fe477b'
down_revision: Union[str, None] = '1a4df9631f8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "trips",
        sa.Column(
            "cargo",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.alter_column("trips", "cargo", server_default=None)


def downgrade() -> None:
    op.drop_column("trips", "cargo")