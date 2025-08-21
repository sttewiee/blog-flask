"""initial

Revision ID: 001
Revises: 
Create Date: 2025-08-21 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tables already exist, just mark them as created
    pass


def downgrade() -> None:
    # Tables already exist, no downgrade needed
    pass
