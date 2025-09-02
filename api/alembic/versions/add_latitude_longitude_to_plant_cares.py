"""Add latitude and longitude to plant_cares

Revision ID: add_lat_lng_001
Revises:
Create Date: 2025-01-28

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_lat_lng_001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add latitude column
    op.add_column("plant_cares", sa.Column("latitude", sa.Float(), nullable=True))
    # Add longitude column
    op.add_column("plant_cares", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade():
    # Remove longitude column
    op.drop_column("plant_cares", "longitude")
    # Remove latitude column
    op.drop_column("plant_cares", "latitude")
