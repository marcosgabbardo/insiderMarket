#!/usr/bin/env python
"""
Debug script to check market collection
"""
from src.polymarket_insider.core.database import get_db
from src.polymarket_insider.models import Trader, Position, Activity, Market
from src.polymarket_insider.api.client import PolymarketAPIClient

def debug_market_collection(trader_address: str):
    """Check why markets aren't being collected"""

    db = next(get_db())

    try:
        # Get trader
        trader = db.query(Trader).filter(Trader.address == trader_address).first()
        if not trader:
            print(f"❌ Trader not found: {trader_address}")
            return

        print(f"✅ Found trader: {trader.address}")
        print(f"   ID: {trader.id}")

        # Check positions
        positions = db.query(Position).filter(Position.trader_id == trader.id).all()
        print(f"\n📊 Positions: {len(positions)}")

        position_market_ids = set()
        positions_without_market = 0
        for p in positions:
            if p.market_id:
                position_market_ids.add(p.market_id)
                print(f"   ✅ Position has market_id: {p.market_id[:16]}... (outcome={p.outcome})")
            else:
                positions_without_market += 1
                print(f"   ❌ Position WITHOUT market_id (outcome={p.outcome})")

        if positions_without_market > 0:
            print(f"   ⚠️  {positions_without_market} positions without market_id")

        # Check activities
        activities = db.query(Activity).filter(Activity.trader_id == trader.id).all()
        print(f"\n🔄 Activities: {len(activities)}")

        activity_market_ids = set()
        activities_without_market = 0
        for a in activities[:5]:  # Show first 5
            if a.market_id:
                activity_market_ids.add(a.market_id)
                print(f"   ✅ Activity has market_id: {a.market_id[:16]}... (type={a.activity_type})")
            else:
                activities_without_market += 1
                print(f"   ❌ Activity WITHOUT market_id (type={a.activity_type})")

        if activities_without_market > 0:
            print(f"   ⚠️  {activities_without_market} activities without market_id")

        # Combine market IDs
        all_market_ids = position_market_ids | activity_market_ids
        print(f"\n🎯 Total unique market_ids: {len(all_market_ids)}")
        print(f"   From positions: {len(position_market_ids)}")
        print(f"   From activities: {len(activity_market_ids)}")

        if not all_market_ids:
            print("\n❌ NO MARKET IDs found! Markets cannot be collected.")
            return

        # Check existing markets
        existing_markets = db.query(Market).all()
        print(f"\n💾 Existing markets in DB: {len(existing_markets)}")

        existing_condition_ids = {m.condition_id for m in existing_markets if m.condition_id}
        print(f"   Existing condition_ids: {len(existing_condition_ids)}")

        # Check which markets need to be collected
        markets_to_collect = all_market_ids - existing_condition_ids
        print(f"\n📥 Markets to collect: {len(markets_to_collect)}")

        if markets_to_collect:
            print("\n🔍 Testing API for first 3 market_ids:")
            with PolymarketAPIClient() as api:
                for i, market_id in enumerate(list(markets_to_collect)[:3]):
                    print(f"\n   {i+1}. Testing market_id: {market_id[:16]}...")
                    try:
                        market_data = api.get_market(market_id)
                        print(f"      ✅ SUCCESS - Got market: {market_data.get('question', 'N/A')[:50]}")
                    except Exception as e:
                        error_str = str(e)
                        if "422" in error_str:
                            print(f"      ⚠️  422 Error - condition_id != market_id")
                        elif "404" in error_str:
                            print(f"      ❌ 404 Error - Market not found")
                        else:
                            print(f"      ❌ Error: {error_str[:100]}")
        else:
            print("   All markets already in database!")

    finally:
        db.close()

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python debug_market_collection.py <trader_address>")
        print("\nExample:")
        print("  python debug_market_collection.py 0x82a1b239e7e0ff25a2ac12a20b59fd6b5f90e03a")
        sys.exit(1)

    trader_address = sys.argv[1]
    debug_market_collection(trader_address)
