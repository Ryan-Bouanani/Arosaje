"""Remove start_photo_url and end_photo_url columns from plant_care table

Revision ID: remove_photo_columns
Revises: d4794802ded3
Create Date: 2025-09-05 14:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "remove_photo_columns"
down_revision = "d4794802ded3"
branch_labels = None
depends_on = None


def upgrade():
    """Remove photo URL columns from plant_cares table"""
    # Remove the photo URL columns as they're now handled by care reports
    op.drop_column("plant_cares", "start_photo_url")
    op.drop_column("plant_cares", "end_photo_url")


def downgrade():
    """Add back photo URL columns to plant_cares table"""
    # Re-add the columns if needed for rollback
    op.add_column(
        "plant_cares", sa.Column("start_photo_url", sa.String(), nullable=True)
    )
    op.add_column("plant_cares", sa.Column("end_photo_url", sa.String(), nullable=True))
