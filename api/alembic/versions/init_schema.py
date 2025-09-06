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
    """Create initial database schema using SQLAlchemy models"""
    # Import here to avoid circular imports
    from utils.database import Base
    from alembic import context
    
    # Import all models to register them with Base.metadata
    import models.user
    import models.plant
    import models.plant_care
    import models.message
    import models.advice
    import models.photo
    import models.care_report
    import models.botanist_report_advice
    import models.user_status
    
    # Get the database connection from alembic context
    connection = context.get_bind()
    
    # Create all tables from SQLAlchemy models
    Base.metadata.create_all(bind=connection)
    
    print("✅ Initial schema created successfully")


def downgrade():
    """Drop all tables"""
    from utils.database import Base
    from alembic import context
    
    # Import all models to register them with Base.metadata
    import models.user
    import models.plant
    import models.plant_care
    import models.message
    import models.advice
    import models.photo
    import models.care_report
    import models.botanist_report_advice
    import models.user_status
    
    # Get the database connection from alembic context
    connection = context.get_bind()
    
    # Drop all tables
    Base.metadata.drop_all(bind=connection)
    
    print("⚠️ All tables dropped")