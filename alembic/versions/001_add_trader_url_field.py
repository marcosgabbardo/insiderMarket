"""add_trader_url_field

Revision ID: 001
Revises:
Create Date: 2025-12-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add trader_url field to traders table"""
    op.add_column('traders', sa.Column('trader_url', sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Remove trader_url field from traders table"""
    op.drop_column('traders', 'trader_url')
