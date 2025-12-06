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
    market_id = Column(String(100), nullable=True)  # Condition ID from Polymarket API

    # Position data
    outcome = Column(String(255), nullable=False)  # YES/NO or outcome name
    size = Column(Float, default=0.0)  # Position size (shares/tokens)
    shares = Column(Float, default=0.0)  # Alias for size (backward compatibility)
    avg_entry_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)

    # Value tracking
    initial_value = Column(Float, default=0.0)  # Initial investment
    invested_amount = Column(Float, default=0.0)  # Alias for initial_value
    current_value = Column(Float, nullable=True)

    # PnL tracking
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, nullable=True)

    # Metadata
    last_updated = Column(String(50), nullable=True)

    # Relationships
    trader = relationship("Trader", backref="positions")

    __table_args__ = (
        Index('idx_position_trader', 'trader_id'),
        Index('idx_position_market', 'market_id'),
        Index('idx_position_trader_market', 'trader_id', 'market_id'),
    )

    def __repr__(self):
        return f"<Position(trader_id={self.trader_id}, market_id={self.market_id}, size={self.size})>"


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
