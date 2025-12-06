"""add_activity_table

Revision ID: 002
Revises: 001
Create Date: 2025-12-06 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create activities table"""
    op.create_table(
        'activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('trader_id', sa.Integer(), nullable=False),
        sa.Column('market_id', sa.String(length=100), nullable=True),
        sa.Column('transaction_hash', sa.String(length=66), nullable=True),
        sa.Column('activity_type', sa.String(length=20), nullable=False),
        sa.Column('outcome', sa.String(length=255), nullable=True),
        sa.Column('side', sa.String(length=10), nullable=True),
        sa.Column('shares_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('cash_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('fee_amount', sa.Float(), nullable=True, default=0.0),
        sa.Column('asset_id', sa.String(length=100), nullable=True),
        sa.Column('from_asset_id', sa.String(length=100), nullable=True),
        sa.Column('to_asset_id', sa.String(length=100), nullable=True),
        sa.Column('timestamp', sa.Integer(), nullable=True),
        sa.Column('activity_date', sa.String(length=50), nullable=True),
        sa.Column('realized_pnl', sa.Float(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.String(length=50), nullable=True),
        sa.Column('updated_at', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['trader_id'], ['traders.id'], ),
    )

    # Create indexes
    op.create_index('idx_activity_trader', 'activities', ['trader_id'])
    op.create_index('idx_activity_market', 'activities', ['market_id'])
    op.create_index('idx_activity_type', 'activities', ['activity_type'])
    op.create_index('idx_activity_timestamp', 'activities', ['timestamp'])
    op.create_index('idx_activity_trader_market', 'activities', ['trader_id', 'market_id'])
    op.create_index('idx_activity_tx_hash', 'activities', ['transaction_hash'])


def downgrade() -> None:
    """Drop activities table"""
    op.drop_index('idx_activity_tx_hash', table_name='activities')
    op.drop_index('idx_activity_trader_market', table_name='activities')
    op.drop_index('idx_activity_timestamp', table_name='activities')
    op.drop_index('idx_activity_type', table_name='activities')
    op.drop_index('idx_activity_market', table_name='activities')
    op.drop_index('idx_activity_trader', table_name='activities')
    op.drop_table('activities')
