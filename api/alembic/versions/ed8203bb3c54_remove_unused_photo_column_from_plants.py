"""remove_unused_photo_column_from_plants

Revision ID: ed8203bb3c54
Revises: 071add117552
Create Date: 2025-09-18 11:16:32.778865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ed8203bb3c54'
down_revision: Union[str, None] = '071add117552'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Supprimer la colonne photo inutilisée de la table plants
    op.drop_column('plants', 'photo')


def downgrade() -> None:
    # Restaurer la colonne photo (pour rollback)
    op.add_column('plants', sa.Column('photo', sa.VARCHAR(), nullable=True))
