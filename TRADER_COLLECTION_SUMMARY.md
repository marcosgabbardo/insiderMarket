# Trader Data Collection - Complete Implementation

This branch contains all improvements made to trader data collection, including:

## ✅ Completed Features

### 1. Trader Model Enhancements
- **trader_url**: Full Polymarket profile URL (`https://polymarket.com/profile/{address}`)
- **total_volume**: Correctly calculated from trades with ISO date fixes
- **win_rate**: Calculated from position P&L
- **avg_position_size**: Average initial value across all positions
- Migration: `alembic/versions/001_add_trader_url_field.py`

### 2. Activity Tracking System
- **New Model**: `Activity` table to track ALL trader activities
- **Activity Types**: TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION
- **Fields**: transaction_hash, amounts, fees, timestamps, P&L, full metadata
- **Migration**: `alembic/versions/002_add_activity_table.py`
- **Note**: Field renamed from `metadata` to `activity_metadata` (SQLAlchemy reserved word)

### 3. Position Market ID Guarantee
- **Fallback System**: If positions API fails (403), builds positions from trades
- **Auto-Repair**: Fills missing market_id in positions using activities data
- **Method**: `_build_positions_from_trades()` aggregates BUY/SELL trades
- **Method**: `_fix_positions_market_id()` repairs incomplete data

### 4. Market Collection Improvements
- **Dual Source**: Collects markets from BOTH positions AND activities
- **422 Error Handling**: Treats 422 as expected (condition_id ≠ market_id)
- **Better Logging**: Shows breakdown of collected, existing, failed markets
- **Method**: `_collect_trader_markets_from_positions_and_activities()`

### 5. Debug Tools
- **Script**: `debug_market_collection.py` - Diagnostic tool to troubleshoot market collection issues

## 📊 Data Flow

```
Trader Collection
    ↓
1. Try Positions API
    ↓ (if fails)
2. Build Positions from Trades → positions with market_id ✅
    ↓
3. Collect Trades & Calculate Stats → total_volume, win_rate, etc. ✅
    ↓
4. Collect Activities → full history with market_id ✅
    ↓
5. Fix Positions without market_id → using activities ✅
    ↓
6. Collect Markets → from positions + activities ✅
```

## 🗄️ Database Schema

### traders
- `trader_url` (NEW) - Full profile URL
- `total_volume` - Total trading volume (USD)
- `win_rate` - Percentage of profitable positions
- `avg_position_size` - Average position initial value
- `username` - Not available via API (requires web scraping)

### activities (NEW TABLE)
- Full transaction history for all traders
- Deduplicates by transaction_hash
- Stores complete metadata as JSON
- Replaces need for PositionHistory

### positions
- `market_id` - Always filled (from API, trades, or activities)

### markets
- Collected from positions + activities
- Handles 422 errors gracefully

## 🚀 Usage

### Collect a Trader
```python
from src.polymarket_insider.api.client import PolymarketAPIClient
from src.polymarket_insider.collectors.trader_collector import TraderCollector
from src.polymarket_insider.core.database import get_db

with PolymarketAPIClient() as api:
    db = next(get_db())
    collector = TraderCollector(api, db)

    trader = collector.collect_trader(
        address='0x...',
        collect_markets=True  # Auto-collect markets
    )
```

### Debug Market Collection
```bash
python debug_market_collection.py <trader_address>
```

## 🔧 Migrations

Apply all migrations:
```bash
alembic upgrade head
```

Or step by step:
```bash
alembic upgrade 001  # Add trader_url
alembic upgrade 002  # Add activities table
```

## ✅ Guarantees

After these improvements:
- ✅ Positions ALWAYS have market_id
- ✅ Activities track complete history
- ✅ Markets collected from multiple sources
- ✅ Robust fallback when APIs fail (403)
- ✅ 422 errors handled gracefully
- ✅ All trader stats calculated correctly

## 📝 Known Limitations

- **username**: Not available via public API (requires web scraping)
- **422 errors**: Some markets cannot be fetched (condition_id ≠ market_id)
- **API Rate Limits**: Large traders may require pagination

## 🎯 Testing

Test with a trader:
```bash
# Run diagnostic
python debug_market_collection.py 0x82a1b239e7e0ff25a2ac12a20b59fd6b5f90e03a

# Check database
python -c "
from src.polymarket_insider.core.database import get_db
from src.polymarket_insider.models import Trader, Position, Activity, Market

db = next(get_db())
print(f'Traders: {db.query(Trader).count()}')
print(f'Positions: {db.query(Position).count()}')
print(f'Activities: {db.query(Activity).count()}')
print(f'Markets: {db.query(Market).count()}')
"
```
