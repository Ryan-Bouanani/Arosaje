"""fix_null_data_and_add_constraints

Revision ID: 6757ecbde92e
Revises: thumbnail_001
Create Date: 2025-09-26 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6757ecbde92e'
down_revision: Union[str, None] = 'thumbnail_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ajouter contraintes NOT NULL sur les champs critiques après correction des données existantes
    """

    # 1. Corriger les données existantes avec valeurs par défaut appropriées
    print("🔧 Correction des données existantes...")

    # Plants: corriger species NULL
    op.execute("""
        UPDATE plants
        SET species = 'Plante d''intérieur'
        WHERE species IS NULL OR species = ''
    """)

    # PlantCares: corriger care_instructions NULL
    op.execute("""
        UPDATE plant_cares
        SET care_instructions = 'Instructions à définir par le propriétaire'
        WHERE care_instructions IS NULL OR care_instructions = ''
    """)

    # PlantCares: corriger location NULL
    op.execute("""
        UPDATE plant_cares
        SET location = 'Localisation à préciser'
        WHERE location IS NULL OR location = ''
    """)

    print("✅ Données existantes corrigées")

    # 2. Appliquer les contraintes NOT NULL
    print("🔒 Application des contraintes NOT NULL...")

    # Plants: rendre species obligatoire
    op.alter_column('plants', 'species', nullable=False)

    # PlantCares: rendre care_instructions et location obligatoires
    op.alter_column('plant_cares', 'care_instructions', nullable=False)
    op.alter_column('plant_cares', 'location', nullable=False)

    print("✅ Contraintes NOT NULL appliquées:")
    print("   - plants.species: nullable=False")
    print("   - plant_cares.care_instructions: nullable=False")
    print("   - plant_cares.location: nullable=False")


def downgrade() -> None:
    """
    Rollback: retirer les contraintes NOT NULL
    """
    print("⏪ Rollback des contraintes NOT NULL...")

    # Retirer les contraintes NOT NULL
    op.alter_column('plants', 'species', nullable=True)
    op.alter_column('plant_cares', 'care_instructions', nullable=True)
    op.alter_column('plant_cares', 'location', nullable=True)

    print("✅ Contraintes NOT NULL supprimées (rollback)")
