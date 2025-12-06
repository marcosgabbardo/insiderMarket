"""
Trader data collector
"""
from typing import List, Set, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..api.client import PolymarketAPIClient
from ..models import Trader, Position, Market, Activity
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

    def collect_trader(self, address: str, collect_markets: bool = True) -> Trader:
        """
        Collect comprehensive trader data including positions, trades, and statistics

        Args:
            address: Ethereum address of the trader
            collect_markets: If True, also collect market data for trader's markets

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
                    trader_url=f"https://polymarket.com/profile/{address}",
                    last_synced_at=datetime.utcnow().isoformat(),
                )
                self.db.add(trader)
                self.db.flush()
                logger.info(f"Created new trader", address=address)
            else:
                # Update trader_url if not set
                if not trader.trader_url:
                    trader.trader_url = f"https://polymarket.com/profile/{address}"

            # Collect comprehensive data
            market_ids = self._collect_positions(trader)
            self._collect_trades_and_stats(trader)
            self._collect_activities(trader, market_ids)

            # Note: Username is not available via public API
            # It would need to be scraped from the Polymarket website
            # or obtained through a different method

            trader.last_synced_at = datetime.utcnow().isoformat()
            self.db.commit()

            # Collect markets that the trader is involved in
            # Now using positions directly to get accurate market data
            if collect_markets and market_ids:
                logger.info(f"Auto-collecting {len(market_ids)} markets for trader", address=address)
                self._collect_trader_markets_from_positions(trader)

            return trader

        except Exception as e:
            logger.error("Failed to collect trader", address=address, error=str(e))
            self.db.rollback()
            raise

    def _collect_positions(self, trader: Trader) -> Set[str]:
        """
        Collect and store positions for a trader

        Args:
            trader: Trader model instance

        Returns:
            Set of market IDs from positions
        """
        address = trader.address
        market_ids = set()

        try:
            # Fetch detailed positions from Data API
            positions_data = self.api.get_user_positions_detailed(
                address=address,
                limit=500,
                size_threshold=0.01,  # Include small positions
            )

            logger.info(f"Found {len(positions_data)} positions", address=address)

            # Store each position
            for pos_data in positions_data:
                market_id = pos_data.get("condition_id")
                if market_id:
                    market_ids.add(market_id)

                # Check if position already exists
                position = (
                    self.db.query(Position)
                    .filter(
                        Position.trader_id == trader.id,
                        Position.market_id == market_id,
                        Position.outcome == pos_data.get("outcome"),
                    )
                    .first()
                )

                if position:
                    # Update existing position
                    self._update_position(position, pos_data)
                else:
                    # Create new position
                    position = self._create_position(trader.id, pos_data)
                    self.db.add(position)

            return market_ids

        except Exception as e:
            # 404 means trader has no positions, which is valid
            if "404" in str(e):
                logger.info(f"No positions found for trader (404)", address=address)
                return set()
            else:
                raise

    def _create_position(self, trader_id: int, data: Dict[str, Any]) -> Position:
        """Create a new position from API data"""
        size_value = float(data.get("size", 0))
        initial_value = float(data.get("initialValue", 0))

        return Position(
            trader_id=trader_id,
            market_id=data.get("condition_id"),
            outcome=data.get("outcome"),
            size=size_value,
            shares=size_value,  # Keep both in sync
            initial_value=initial_value,
            invested_amount=initial_value,  # Keep both in sync
            current_value=float(data.get("currentValue", 0)),
            avg_entry_price=float(data.get("avgPrice", 0)),
            realized_pnl=float(data.get("realizedPnl", 0)),
            unrealized_pnl=float(data.get("cashPnl", 0)),
        )

    def _update_position(self, position: Position, data: Dict[str, Any]) -> None:
        """Update an existing position with new data"""
        size_value = float(data.get("size", position.size))

        position.size = size_value
        position.shares = size_value  # Keep both in sync
        position.current_value = float(data.get("currentValue", position.current_value))
        position.avg_entry_price = float(data.get("avgPrice", position.avg_entry_price))
        position.realized_pnl = float(data.get("realizedPnl", position.realized_pnl))
        position.unrealized_pnl = float(data.get("cashPnl", position.unrealized_pnl))

    def _collect_trades_and_stats(self, trader: Trader) -> None:
        """
        Collect trades and calculate trader statistics

        Args:
            trader: Trader model instance
        """
        address = trader.address

        try:
            # Fetch all trades (paginated if necessary)
            all_trades = []
            offset = 0
            limit = 500

            while True:
                trades = self.api.get_user_trades(address=address, limit=limit, offset=offset)
                if not trades:
                    break
                all_trades.extend(trades)

                # If we got less than limit, we've reached the end
                if len(trades) < limit:
                    break

                offset += limit

            logger.info(f"Found {len(all_trades)} total trades", address=address)

            if not all_trades:
                logger.info(f"No trades found for trader", address=address)
                return

            # Calculate statistics
            total_volume = 0.0
            total_trades = len(all_trades)
            markets_traded = set()
            trade_dates = []

            for trade in all_trades:
                # Accumulate volume (in USD)
                cash_amount = abs(float(trade.get("cashAmount", 0)))
                total_volume += cash_amount

                # Track unique markets
                market_id = trade.get("conditionId")
                if market_id:
                    markets_traded.add(market_id)

                # Track trade dates
                timestamp = trade.get("timestamp")
                if timestamp:
                    trade_dates.append(datetime.fromtimestamp(timestamp))

            # Update trader statistics
            trader.total_volume = total_volume
            trader.total_trades = total_trades
            trader.markets_traded = len(markets_traded)

            if trade_dates:
                trader.first_trade_date = min(trade_dates).isoformat()
                trader.last_trade_date = max(trade_dates).isoformat()

            # Calculate win rate and avg position size from positions
            self._calculate_win_rate(trader)
            self._calculate_avg_position_size(trader)

            logger.info(
                f"Updated trader stats",
                address=address,
                volume=total_volume,
                trades=total_trades,
                markets=len(markets_traded),
            )

        except Exception as e:
            if "404" in str(e):
                logger.info(f"No trades found for trader (404)", address=address)
            else:
                raise

    def _calculate_win_rate(self, trader: Trader) -> None:
        """
        Calculate win rate based on trader's positions

        Args:
            trader: Trader model instance
        """
        # Get all positions for the trader
        positions = self.db.query(Position).filter(Position.trader_id == trader.id).all()

        if not positions:
            trader.win_rate = None
            return

        # Count profitable positions (realized_pnl + unrealized_pnl > 0)
        winning_positions = sum(
            1
            for p in positions
            if (p.realized_pnl or 0) + (p.unrealized_pnl or 0) > 0
        )

        trader.win_rate = (winning_positions / len(positions)) * 100 if positions else None

    def _calculate_avg_position_size(self, trader: Trader) -> None:
        """
        Calculate average position size based on trader's positions

        Args:
            trader: Trader model instance
        """
        # Get all positions for the trader
        positions = self.db.query(Position).filter(Position.trader_id == trader.id).all()

        if not positions:
            trader.avg_position_size = None
            return

        # Calculate average initial value across all positions
        total_initial_value = sum(p.initial_value or 0 for p in positions)
        trader.avg_position_size = total_initial_value / len(positions) if positions else None

    def _collect_activities(self, trader: Trader, market_ids: Set[str]) -> None:
        """
        Collect all activities for a trader (trades, splits, merges, redeems, etc.)

        Args:
            trader: Trader model instance
            market_ids: Set of market IDs from positions (for context)
        """
        address = trader.address

        try:
            # Fetch all activities using Data API
            all_activities = []
            limit = 500

            # Try to get activities from Data API
            try:
                activities = self.api.get_user_activity_detailed(
                    address=address,
                    limit=limit
                )
                all_activities.extend(activities)
                logger.info(f"Found {len(all_activities)} activities", address=address)
            except Exception as e:
                # If Data API fails, log and continue
                logger.warning(f"Could not fetch activities from Data API", address=address, error=str(e))
                return

            if not all_activities:
                logger.info(f"No activities found for trader", address=address)
                return

            # Store each activity
            for activity_data in all_activities:
                try:
                    # Check if activity already exists by transaction hash
                    tx_hash = activity_data.get("transactionHash") or activity_data.get("txHash")
                    if tx_hash:
                        existing = (
                            self.db.query(Activity)
                            .filter(
                                Activity.trader_id == trader.id,
                                Activity.transaction_hash == tx_hash,
                            )
                            .first()
                        )
                        if existing:
                            continue

                    # Create new activity
                    activity = self._create_activity(trader.id, activity_data)
                    self.db.add(activity)

                except Exception as e:
                    logger.warning(f"Failed to store activity", error=str(e))
                    continue

            logger.info(f"Stored activities for trader", address=address, count=len(all_activities))

        except Exception as e:
            logger.warning(f"Failed to collect activities", address=address, error=str(e))

    def _create_activity(self, trader_id: int, data: Dict[str, Any]) -> Activity:
        """Create an activity from API data"""
        import json

        timestamp = data.get("timestamp")
        activity_date = None
        if timestamp:
            activity_date = datetime.fromtimestamp(timestamp).isoformat()

        return Activity(
            trader_id=trader_id,
            market_id=data.get("conditionId") or data.get("condition_id"),
            transaction_hash=data.get("transactionHash") or data.get("txHash"),
            activity_type=data.get("type", "TRADE"),
            outcome=data.get("outcome"),
            side=data.get("side"),
            shares_amount=float(data.get("sharesAmount", 0)) if data.get("sharesAmount") else None,
            cash_amount=float(data.get("cashAmount", 0)) if data.get("cashAmount") else None,
            price=float(data.get("price", 0)) if data.get("price") else None,
            fee_amount=float(data.get("feeAmount", 0)) if data.get("feeAmount") else None,
            asset_id=data.get("assetId") or data.get("asset_id"),
            from_asset_id=data.get("fromAssetId") or data.get("from_asset_id"),
            to_asset_id=data.get("toAssetId") or data.get("to_asset_id"),
            timestamp=timestamp,
            activity_date=activity_date,
            realized_pnl=float(data.get("realizedPnl", 0)) if data.get("realizedPnl") else None,
            activity_metadata=json.dumps(data) if data else None,  # Store full data for reference
        )

    def _collect_trader_markets_from_positions(self, trader: Trader) -> None:
        """
        Collect markets based on trader's positions (more reliable than condition_id lookup)

        Args:
            trader: Trader model instance
        """
        from .market_collector import MarketCollector

        try:
            # Get all positions for this trader
            positions = self.db.query(Position).filter(Position.trader_id == trader.id).all()

            if not positions:
                logger.info(f"No positions to collect markets from", trader_address=trader.address)
                return

            collector = MarketCollector(self.api, self.db)
            collected_count = 0
            unique_market_ids = set()

            for position in positions:
                market_id = position.market_id
                if not market_id or market_id in unique_market_ids:
                    continue

                unique_market_ids.add(market_id)

                try:
                    # Check if market already exists by condition_id
                    existing = self.db.query(Market).filter(Market.condition_id == market_id).first()
                    if existing:
                        logger.debug(f"Market already exists", condition_id=market_id)
                        continue

                    # Try to fetch market using condition_id
                    # The Polymarket API sometimes accepts condition_id as market_id
                    try:
                        market_data = self.api.get_market(market_id)
                        collector._store_market(market_data)
                        collected_count += 1
                        logger.debug(f"Collected market from position", condition_id=market_id)
                    except Exception as api_error:
                        logger.debug(
                            f"Could not fetch market by condition_id from position",
                            condition_id=market_id,
                            error=str(api_error)
                        )
                        continue

                except Exception as e:
                    logger.warning(f"Failed to collect market from position", market_id=market_id, error=str(e))
                    continue

            if collected_count > 0:
                self.db.commit()
                logger.info(f"Auto-collected {collected_count} markets from {len(positions)} positions")
            else:
                logger.info(f"No new markets collected from positions")

        except Exception as e:
            logger.error(f"Failed to collect markets from positions", error=str(e))

    def _collect_trader_markets(self, market_ids: Set[str]) -> None:
        """
        Collect market data for markets the trader is involved in

        Args:
            market_ids: Set of market IDs to collect
        """
        from .market_collector import MarketCollector

        try:
            collector = MarketCollector(self.api, self.db)
            collected_count = 0

            for condition_id in market_ids:
                try:
                    # Check if market already exists by condition_id
                    existing = self.db.query(Market).filter(Market.condition_id == condition_id).first()
                    if existing:
                        logger.debug(f"Market already exists", condition_id=condition_id)
                        continue

                    # Try to fetch market using condition_id as market_id
                    # (In many cases, they might be the same or the API might handle it)
                    try:
                        market_data = self.api.get_market(condition_id)
                        collector._store_market(market_data)
                        collected_count += 1
                        logger.debug(f"Collected market", condition_id=condition_id)
                    except Exception as api_error:
                        # If API fails, it might be because condition_id != market_id
                        # We can't fetch without the actual market_id
                        logger.debug(
                            f"Could not fetch market by condition_id",
                            condition_id=condition_id,
                            error=str(api_error)
                        )
                        continue

                except Exception as e:
                    logger.warning(f"Failed to collect market", condition_id=condition_id, error=str(e))
                    continue

            self.db.commit()
            logger.info(f"Auto-collected {collected_count} new markets from {len(market_ids)} positions")

        except Exception as e:
            logger.error(f"Failed to auto-collect markets", error=str(e))


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
