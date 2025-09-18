"""add_english_name_columns

Revision ID: f997224f0474
Revises: 08b55fac9c06
Create Date: 2025-09-16 17:02:15.859418

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f997224f0474'
down_revision: Union[str, None] = '08b55fac9c06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter les nouvelles colonnes anglaises
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
    
    # Migrer les données existantes
    op.execute("UPDATE users SET first_name = prenom, last_name = nom WHERE prenom IS NOT NULL AND nom IS NOT NULL")
    
    # Rendre les nouvelles colonnes non-nullable après migration
    op.alter_column('users', 'first_name', nullable=False)
    op.alter_column('users', 'last_name', nullable=False)


def downgrade() -> None:
    # Restaurer les données vers les anciennes colonnes si elles existent encore
    op.execute("UPDATE users SET prenom = first_name, nom = last_name WHERE first_name IS NOT NULL AND last_name IS NOT NULL")
    
    # Supprimer les colonnes anglaises
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
