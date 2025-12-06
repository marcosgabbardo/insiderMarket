"""
Trader scoring model for insider analysis (Phase 2)
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class TraderScore(Base, TimestampMixin):
    """
    Insider trading scores and analysis metrics
    """
    __tablename__ = 'trader_scores'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    trader_id = Column(Integer, ForeignKey('traders.id'), nullable=False, unique=True)

    # Overall scores
    insider_score = Column(Float, default=0.0, index=True)  # Composite score 0-100
    confidence_level = Column(Float, default=0.0)  # Statistical confidence

    # Component scores
    early_entry_score = Column(Float, default=0.0)  # Enters before big moves
    timing_accuracy_score = Column(Float, default=0.0)  # Precise timing
    volume_pattern_score = Column(Float, default=0.0)  # Unusual volume patterns
    win_rate_score = Column(Float, default=0.0)  # High win rate
    correlation_score = Column(Float, default=0.0)  # Correlation with other insiders

    # Statistics
    analyzed_trades = Column(Integer, default=0)
    early_entries = Column(Integer, default=0)
    significant_wins = Column(Integer, default=0)

    # Pattern details
    detected_patterns = Column(Text, nullable=True)  # JSON with pattern details
    correlated_traders = Column(Text, nullable=True)  # JSON with correlated trader IDs

    # Tracking
    last_analyzed_at = Column(String(50), nullable=True)
    analysis_version = Column(String(20), default='1.0')

    # Relationship
    trader = relationship("Trader", backref="score", uselist=False)

    __table_args__ = (
        Index('idx_score_insider', 'insider_score'),
        Index('idx_score_trader', 'trader_id'),
        Index('idx_score_confidence', 'confidence_level'),
    )

    def __repr__(self):
        return f"<TraderScore(trader_id={self.trader_id}, insider_score={self.insider_score:.2f})>"
