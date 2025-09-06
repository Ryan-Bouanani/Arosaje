"""Initial schema creation

Revision ID: init_schema
Revises: 
Create Date: 2025-09-06 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'init_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Initial schema - tables created by main.py"""
    # Tables are created automatically by Base.metadata.create_all() 
    # in main.py when the API starts up
    # This migration is just a placeholder to track the initial state
    pass


def downgrade():
    """Drop all tables - not implemented"""
    # Dropping all tables would be destructive
    # If needed, implement specific table drops
    pass