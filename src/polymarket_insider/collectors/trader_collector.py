"""
Trader data collector
"""
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from ..api.client import PolymarketAPIClient
from ..models import Trader, Position
from ..core.logging import get_logger
from ..core.database import get_db

logger = get_logger(__name__)


class TraderCollector:
    """
    Collects and stores trader data from Polymarket
    """

    def __init__(self, api_client: PolymarketAPIClient, db: Session):
        self.api = api_client
        self.db = db

    def collect_trader(self, address: str) -> Trader:
        """
        Collect trader data and positions

        Args:
            address: Ethereum address of the trader

        Returns:
            Trader model instance
        """
        logger.info(f"Collecting trader data", address=address)

        try:
            # Get or create trader
            trader = self.db.query(Trader).filter(Trader.address == address).first()

            if not trader:
                trader = Trader(
                    address=address,
                    last_synced_at=datetime.utcnow().isoformat(),
                )
                self.db.add(trader)
                self.db.flush()
                logger.info(f"Created new trader", address=address)

            # Collect positions
            positions_data = self.api.get_positions(address)
            logger.info(f"Found {len(positions_data)} positions", address=address)

            # Update trader stats will be implemented later

            trader.last_synced_at = datetime.utcnow().isoformat()
            self.db.commit()

            return trader

        except Exception as e:
            logger.error("Failed to collect trader", address=address, error=str(e))
            self.db.rollback()
            raise


def collect_traders_task(addresses: List[str]) -> int:
    """
    Standalone task to collect trader data

    Args:
        addresses: List of Ethereum addresses

    Returns:
        Number of traders collected
    """
    logger.info(f"Starting trader collection task", count=len(addresses))

    with PolymarketAPIClient() as api_client:
        db = next(get_db())
        try:
            collector = TraderCollector(api_client, db)
            collected = 0

            for address in addresses:
                try:
                    collector.collect_trader(address)
                    collected += 1
                except Exception as e:
                    logger.error(f"Failed to collect trader", address=address, error=str(e))
                    continue

            return collected
        finally:
            db.close()
