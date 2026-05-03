"""Add allowed_batches column to rooms table

Revision ID: add_allowed_batches
Revises: c67899263671
Create Date: 2026-05-03 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_allowed_batches'
down_revision = 'c67899263671'
branch_labels = None
depends_on = None


def upgrade():
    # Add allowed_batches column to rooms table (JSON type, nullable)
    # If None, all student groups are allowed; if a list, only those batches are allowed
    op.add_column('rooms', sa.Column('allowed_batches', sa.JSON(), nullable=True))


def downgrade():
    # Remove allowed_batches column if downgrading
    op.drop_column('rooms', 'allowed_batches')
