"""
Activity model - All trader activities
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Activity(Base, TimestampMixin):
    """
    Historical activities of traders

    Stores all types of activities:
    - TRADE: Buy/sell trades
    - SPLIT: Token splits
    - MERGE: Token merges
    - REDEEM: Position redemptions
    - REWARD: Rewards received
    - CONVERSION: Token conversions
    """
    __tablename__ = 'activities'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    market_id = Column(String(100), nullable=True)  # Condition ID from Polymarket

    # Activity identification
    transaction_hash = Column(String(66), nullable=True, index=True)  # Ethereum tx hash
    activity_type = Column(String(20), nullable=False, index=True)  # TRADE, SPLIT, MERGE, etc.

    # Trade/Activity details
    outcome = Column(String(255), nullable=True)  # YES/NO or outcome name
    side = Column(String(10), nullable=True)  # BUY, SELL

    # Amounts
    shares_amount = Column(Float, default=0.0)  # Number of shares
    cash_amount = Column(Float, default=0.0)  # Cash value (USD)
    price = Column(Float, nullable=True)  # Execution price

    # Fees
    fee_amount = Column(Float, default=0.0)

    # Asset information
    asset_id = Column(String(100), nullable=True)  # Token/asset ID
    from_asset_id = Column(String(100), nullable=True)  # For conversions
    to_asset_id = Column(String(100), nullable=True)  # For conversions

    # Timing
    timestamp = Column(Integer, nullable=True, index=True)  # Unix timestamp
    activity_date = Column(String(50), nullable=True)  # ISO date string

    # PnL tracking (for closed positions)
    realized_pnl = Column(Float, nullable=True)

    # Additional metadata (JSON)
    activity_metadata = Column(Text, nullable=True)  # JSON string for extra data

    # Relationships
    trader = relationship("Trader", backref="activities")

    __table_args__ = (
        Index('idx_activity_trader', 'trader_id'),
        Index('idx_activity_market', 'market_id'),
        Index('idx_activity_type', 'activity_type'),
        Index('idx_activity_timestamp', 'timestamp'),
        Index('idx_activity_trader_market', 'trader_id', 'market_id'),
        Index('idx_activity_tx_hash', 'transaction_hash'),
    )

    def __repr__(self):
        return f"<Activity(trader_id={self.trader_id}, type={self.activity_type}, market_id={self.market_id})>"
