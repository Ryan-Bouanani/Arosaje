"""remove_nom_espece_from_plants

Revision ID: 29da178aced9
Revises: 8cea8bfa4282
Create Date: 2025-09-21 15:56:16.647711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29da178aced9'
down_revision: Union[str, None] = '8cea8bfa4282'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Supprimer les anciennes colonnes françaises de la table plants
    op.drop_column('plants', 'nom')
    op.drop_column('plants', 'espece')


def downgrade() -> None:
    # Restaurer les colonnes françaises (pour rollback)
    op.add_column('plants', sa.Column('nom', sa.VARCHAR(), nullable=True))
    op.add_column('plants', sa.Column('espece', sa.VARCHAR(), nullable=True))
