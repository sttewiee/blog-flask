"""bootstrap existing schema

Revision ID: 7e01109534a6
Revises: 
Create Date: 2025-08-21 14:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '7e01109534a6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if tables already exist
    inspector = inspect(op.get_bind())
    existing_tables = inspector.get_table_names()
    
    # Create tables only if they don't exist
    if 'user' not in existing_tables:
        op.create_table('user',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=100), nullable=False),
            sa.Column('password', sa.String(length=200), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('username')
        )
        print("Created 'user' table")
    else:
        print("'user' table already exists")
    
    if 'post' not in existing_tables:
        op.create_table('post',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        print("Created 'post' table")
    else:
        print("'post' table already exists")


def downgrade() -> None:
    # Drop tables if they exist
    inspector = inspect(op.get_bind())
    existing_tables = inspector.get_table_names()
    
    if 'post' in existing_tables:
        op.drop_table('post')
        print("Dropped 'post' table")
    
    if 'user' in existing_tables:
        op.drop_table('user')
        print("Dropped 'user' table")
