"""add_nullable_constraints_manual

Revision ID: 00eb9f546435
Revises: 29da178aced9
Create Date: 2025-09-21 18:59:24.521272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00eb9f546435'
down_revision: Union[str, None] = '29da178aced9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter contraintes NOT NULL sur les champs critiques

    # Table users - email et password obligatoires
    op.alter_column('users', 'email', nullable=False)
    op.alter_column('users', 'password', nullable=False)

    # Table plants - name obligatoire
    op.alter_column('plants', 'name', nullable=False)

    # Table plant_cares - status obligatoire
    op.alter_column('plant_cares', 'status', nullable=False)

    # Table conversations - type obligatoire
    op.alter_column('conversations', 'type', nullable=False)

    # Supprimer l'ancien champ localisation de plant_cares s'il existe encore
    try:
        op.drop_column('plant_cares', 'localisation')
    except:
        pass  # Ignore si la colonne n'existe pas


def downgrade() -> None:
    # Retirer les contraintes NOT NULL (rollback)
    op.alter_column('users', 'email', nullable=True)
    op.alter_column('users', 'password', nullable=True)
    op.alter_column('plants', 'name', nullable=True)
    op.alter_column('plant_cares', 'status', nullable=True)
    op.alter_column('conversations', 'type', nullable=True)

    # Restaurer localisation
    op.add_column('plant_cares', sa.Column('localisation', sa.VARCHAR(), nullable=True))
