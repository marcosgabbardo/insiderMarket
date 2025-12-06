"""
Bet/Trade model
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Bet(Base, TimestampMixin):
    """
    Individual bets/trades
    """
    __tablename__ = 'bets'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'), nullable=False)

    # Trade identifiers
    trade_id = Column(String(100), unique=True, nullable=True, index=True)
    transaction_hash = Column(String(66), nullable=True, index=True)

    # Trade details
    side = Column(String(10), nullable=False)  # BUY or SELL
    outcome = Column(String(255), nullable=False)  # YES/NO or outcome name
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    # Values
    amount = Column(Float, nullable=False)  # Total amount in USD
    fee = Column(Float, default=0.0)

    # Timing
    trade_date = Column(String(50), nullable=False, index=True)
    block_number = Column(Integer, nullable=True)

    # Result (if market resolved)
    result = Column(String(20), nullable=True)  # WIN, LOSS, PUSH
    pnl = Column(Float, nullable=True)

    # Relationships
    trader = relationship("Trader", backref="bets")
    market = relationship("Market", backref="bets")

    __table_args__ = (
        Index('idx_bet_trader', 'trader_id'),
        Index('idx_bet_market', 'market_id'),
        Index('idx_bet_date', 'trade_date'),
        Index('idx_bet_trader_date', 'trader_id', 'trade_date'),
        Index('idx_bet_market_date', 'market_id', 'trade_date'),
    )

    def __repr__(self):
        return f"<Bet(trader_id={self.trader_id}, market_id={self.market_id}, side={self.side}, amount={self.amount})>"
