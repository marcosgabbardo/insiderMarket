"""
Market data collector
"""
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..api.client import PolymarketAPIClient
from ..models import Market
from ..core.logging import get_logger
from ..core.database import get_db

logger = get_logger(__name__)


class MarketCollector:
    """
    Collects and stores market data from Polymarket
    """

    def __init__(self, api_client: PolymarketAPIClient, db: Session):
        self.api = api_client
        self.db = db

    def collect_markets(
        self, limit: int = 100, offset: int = 0, active_only: bool = True
    ) -> int:
        """
        Collect markets from Polymarket API and store in database

        Args:
            limit: Number of markets to fetch
            offset: Pagination offset
            active_only: Only fetch active markets

        Returns:
            Number of markets collected
        """
        logger.info(
            "Starting market collection",
            limit=limit,
            offset=offset,
            active_only=active_only,
        )

        try:
            # Fetch markets from API
            markets_data = self.api.get_markets(limit=limit, offset=offset, active=active_only)

            if not markets_data:
                logger.warning("No markets returned from API")
                return 0

            collected = 0
            for market_data in markets_data:
                try:
                    self._store_market(market_data)
                    collected += 1
                except Exception as e:
                    logger.error(
                        "Failed to store market",
                        market_id=market_data.get("id"),
                        error=str(e),
                    )
                    continue

            self.db.commit()
            logger.info(f"Successfully collected {collected} markets")
            return collected

        except Exception as e:
            logger.error("Market collection failed", error=str(e))
            self.db.rollback()
            raise

    def _store_market(self, market_data: Dict[str, Any]) -> Market:
        """
        Store or update a market in the database

        Args:
            market_data: Market data from API

        Returns:
            Market model instance
        """
        market_id = market_data.get("id")

        # Check if market already exists
        market = self.db.query(Market).filter(Market.market_id == market_id).first()

        if market:
            # Update existing market
            self._update_market(market, market_data)
            logger.debug(f"Updated market {market_id}")
        else:
            # Create new market
            market = self._create_market(market_data)
            logger.debug(f"Created market {market_id}")

        return market

    def _create_market(self, data: Dict[str, Any]) -> Market:
        """Create a new market from API data"""
        import json

        market = Market(
            market_id=data.get("id"),
            condition_id=data.get("condition_id"),
            question=data.get("question", ""),
            description=data.get("description"),
            category=data.get("category"),
            active=data.get("active", True),
            closed=data.get("closed", False),
            resolved=data.get("resolved", False),
            volume=float(data.get("volume", 0)),
            liquidity=float(data.get("liquidity", 0)),
            outcome_prices=json.dumps(data.get("outcome_prices", {})),
            outcomes=json.dumps(data.get("outcomes", [])),
            winning_outcome=data.get("winning_outcome"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            resolution_date=data.get("resolution_date"),
            last_synced_at=datetime.utcnow().isoformat(),
        )

        self.db.add(market)
        return market

    def _update_market(self, market: Market, data: Dict[str, Any]) -> None:
        """Update an existing market with new data"""
        import json

        market.question = data.get("question", market.question)
        market.description = data.get("description", market.description)
        market.category = data.get("category", market.category)
        market.active = data.get("active", market.active)
        market.closed = data.get("closed", market.closed)
        market.resolved = data.get("resolved", market.resolved)
        market.volume = float(data.get("volume", market.volume))
        market.liquidity = float(data.get("liquidity", market.liquidity))
        market.outcome_prices = json.dumps(data.get("outcome_prices", {}))
        market.outcomes = json.dumps(data.get("outcomes", []))
        market.winning_outcome = data.get("winning_outcome", market.winning_outcome)
        market.end_date = data.get("end_date", market.end_date)
        market.resolution_date = data.get("resolution_date", market.resolution_date)
        market.last_synced_at = datetime.utcnow().isoformat()


def collect_markets_task(limit: int = 100, active_only: bool = True) -> int:
    """
    Standalone task to collect markets

    Args:
        limit: Number of markets to fetch
        active_only: Only fetch active markets

    Returns:
        Number of markets collected
    """
    logger.info("Starting market collection task")

    with PolymarketAPIClient() as api_client:
        db = next(get_db())
        try:
            collector = MarketCollector(api_client, db)
            return collector.collect_markets(limit=limit, active_only=active_only)
        finally:
            db.close()
