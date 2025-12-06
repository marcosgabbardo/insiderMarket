"""
Position models - current and historical
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Position(Base, TimestampMixin):
    """
    Current positions of traders
    """
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)

    # Position data
    outcome = Column(String(255), nullable=False)  # YES/NO or outcome name
    shares = Column(Float, default=0.0)
    avg_entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)

    # Value
    invested_amount = Column(Float, default=0.0)
    current_value = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)

    # Metadata
    last_updated = Column(String(50), nullable=True)

    # Relationships
    trader = relationship("Trader", backref="positions")
    market = relationship("Market", backref="positions")

    __table_args__ = (
        Index('idx_position_trader', 'trader_id'),
        Index('idx_position_market', 'market_id'),
        Index('idx_position_trader_market', 'trader_id', 'market_id'),
    )

    def __repr__(self):
        return f"<Position(trader_id={self.trader_id}, market_id={self.market_id}, shares={self.shares})>"


class PositionHistory(Base, TimestampMixin):
    """
    Historical snapshots of positions
    """
    __tablename__ = 'position_history'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)

    # Position snapshot
    outcome = Column(String(255), nullable=False)
    shares = Column(Float, default=0.0)
    price = Column(Float, nullable=True)
    value = Column(Float, nullable=True)

    # Change tracking
    shares_change = Column(Float, default=0.0)  # Delta from previous snapshot
    action = Column(String(20), nullable=True)  # BUY, SELL, ENTRY, EXIT

    # Timing
    snapshot_date = Column(String(50), nullable=False, index=True)

    # Relationships
    trader = relationship("Trader", backref="position_history")
    market = relationship("Market", backref="position_history")

    __table_args__ = (
        Index('idx_history_trader', 'trader_id'),
        Index('idx_history_market', 'market_id'),
        Index('idx_history_date', 'snapshot_date'),
        Index('idx_history_trader_market_date', 'trader_id', 'market_id', 'snapshot_date'),
    )

    def __repr__(self):
        return f"<PositionHistory(trader_id={self.trader_id}, market_id={self.market_id}, date={self.snapshot_date})>"
