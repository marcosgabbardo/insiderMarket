"""
Trader model
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Index
from .base import Base, TimestampMixin


class Trader(Base, TimestampMixin):
    """
    Trader profile and statistics
    """
    __tablename__ = 'traders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    address = Column(String(42), unique=True, nullable=False, index=True)  # Ethereum address

    # Profile information
    username = Column(String(255), nullable=True)
    ens_name = Column(String(255), nullable=True)

    # Statistics
    total_volume = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    markets_traded = Column(Integer, default=0)
    win_rate = Column(Float, nullable=True)
    avg_position_size = Column(Float, nullable=True)

    # Activity tracking
    first_trade_date = Column(String(50), nullable=True)
    last_trade_date = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)

    # Metadata
    last_synced_at = Column(String(50), nullable=True)

    __table_args__ = (
        Index('idx_trader_address', 'address'),
        Index('idx_trader_volume', 'total_volume'),
        Index('idx_trader_active', 'is_active'),
    )

    def __repr__(self):
        return f"<Trader(address={self.address}, username={self.username}, total_volume={self.total_volume})>"
