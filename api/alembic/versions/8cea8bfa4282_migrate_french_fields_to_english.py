"""migrate_french_fields_to_english

Revision ID: 8cea8bfa4282
Revises: ed8203bb3c54
Create Date: 2025-09-21 14:57:52.474350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cea8bfa4282'
down_revision: Union[str, None] = 'ed8203bb3c54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Migration des données des champs français vers anglais
    connection = op.get_bind()

    # 1. Migrer les données non nulles depuis les champs français
    connection.execute(sa.text("""
        UPDATE users
        SET first_name = COALESCE(first_name, prenom, '')
        WHERE first_name IS NULL OR first_name = ''
    """))

    connection.execute(sa.text("""
        UPDATE users
        SET last_name = COALESCE(last_name, nom, '')
        WHERE last_name IS NULL OR last_name = ''
    """))

    connection.execute(sa.text("""
        UPDATE users
        SET location = COALESCE(location, localisation)
        WHERE location IS NULL AND localisation IS NOT NULL
    """))

    # 2. Supprimer les anciennes colonnes françaises
    op.drop_column('users', 'nom')
    op.drop_column('users', 'prenom')
    op.drop_column('users', 'localisation')


def downgrade() -> None:
    # Recréer les colonnes françaises
    op.add_column('users', sa.Column('nom', sa.String(), nullable=True))
    op.add_column('users', sa.Column('prenom', sa.String(), nullable=True))
    op.add_column('users', sa.Column('localisation', sa.String(), nullable=True))

    # Restaurer les données dans les champs français
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users
        SET nom = last_name, prenom = first_name, localisation = location
    """))
