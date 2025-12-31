
"""add indexes and pg_trgm gin

Revision ID: 60e2a8991e90
Revises: f3bb17fe477b
Create Date: 2025-12-31 10:32:52.978509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '60e2a8991e90'
down_revision: Union[str, None] = 'f3bb17fe477b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_index("ix_trips_departure_date", "trips", ["departure_date"])
    op.create_index("ix_trips_return_date", "trips", ["return_date"])
    op.create_index("ix_trips_origin", "trips", ["origin"])
    op.create_index("ix_trips_destination", "trips", ["destination"])
    op.create_index("ix_trips_car_number", "trips", ["car_number"])
    op.create_index("ix_trips_driver_tab_number", "trips", ["driver_tab_number"])

    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_trips_cargo_trgm_gin ON trips USING GIN ((cargo::text) gin_trgm_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_trips_cargo_trgm_gin")

    op.drop_index("ix_trips_driver_tab_number", table_name="trips")
    op.drop_index("ix_trips_car_number", table_name="trips")
    op.drop_index("ix_trips_destination", table_name="trips")
    op.drop_index("ix_trips_origin", table_name="trips")
    op.drop_index("ix_trips_return_date", table_name="trips")
    op.drop_index("ix_trips_departure_date", table_name="trips")