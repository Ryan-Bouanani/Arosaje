"""add_photo_thumbnail_field_to_plants

Revision ID: thumbnail_001
Revises: 00eb9f546435
Create Date: 2025-09-21 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'thumbnail_001'
down_revision: Union[str, None] = '00eb9f546435'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter le champ photo_thumbnail à la table plants
    op.add_column('plants', sa.Column('photo_thumbnail', sa.Text(), nullable=True))


def downgrade() -> None:
    # Supprimer le champ photo_thumbnail
    op.drop_column('plants', 'photo_thumbnail')