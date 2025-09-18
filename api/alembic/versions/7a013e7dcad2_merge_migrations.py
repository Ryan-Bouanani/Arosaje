"""merge_migrations

Revision ID: 7a013e7dcad2
Revises: add_refresh_tokens_001, init_schema
Create Date: 2025-09-12 15:16:09.377150

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '7a013e7dcad2'
down_revision: Union[str, None] = ('add_refresh_tokens_001', 'init_schema')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
