"""
Market model
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, Index
from .base import Base, TimestampMixin


class Market(Base, TimestampMixin):
    """
    Polymarket market information
    """
    __tablename__ = 'markets'

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), unique=True, nullable=False, index=True)  # Polymarket market ID
    condition_id = Column(String(100), nullable=True, index=True)

    # Market details
    question = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)

    # Market status
    active = Column(Boolean, default=True)
    closed = Column(Boolean, default=False)
    resolved = Column(Boolean, default=False)

    # Market data
    volume = Column(Float, default=0.0)
    liquidity = Column(Float, default=0.0)
    outcome_prices = Column(Text, nullable=True)  # JSON string

    # Outcome information
    outcomes = Column(Text, nullable=True)  # JSON string with outcomes
    winning_outcome = Column(String(255), nullable=True)

    # Timing
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    resolution_date = Column(String(50), nullable=True)

    # Tracking
    total_positions = Column(Integer, default=0)
    unique_traders = Column(Integer, default=0)
    last_synced_at = Column(String(50), nullable=True)

    __table_args__ = (
        Index('idx_market_id', 'market_id'),
        Index('idx_market_active', 'active'),
        Index('idx_market_category', 'category'),
        Index('idx_market_volume', 'volume'),
    )

    def __repr__(self):
        return f"<Market(market_id={self.market_id}, question={self.question[:50]}...)>"
