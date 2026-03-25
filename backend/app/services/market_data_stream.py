"""
PERFECTED: 5PAISA Dynamic Market Data Stream
1. Fixes "Zero-Overwrite" by merging instead of replacing Redis cache.
2. Supports Dynamic Subscriptions (any symbol added by user).
3. Optimized for complete data mapping (AvgPrice, Buy/Sell, Volume).
"""
import asyncio
import json
import logging
import os
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import websockets
from app.core.cache import set_cache, get_cache_value
from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# 🔥 GLOBAL SUBSCRIPTION REGISTRY
DYNAMIC_INSTRUMENTS: Set[int] = {25, 26} # Defaults (Nifty, BankNifty)

class MarketDataStream:
    """Dynamic real-time market data streaming for 5paisa"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.running = False
        self._current_subs: Set[int] = set()

    @classmethod
    def subscribe(cls, scrip_code: int):
        """Add a scrip code to the global live-stream registry"""
        if scrip_code:
            DYNAMIC_INSTRUMENTS.add(int(scrip_code))

    async def start_streaming(self):
        self.running = True
        all_accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
        paisa_acc = next((acc for acc in all_accounts if str(acc.broker_name).upper() in ["FIVEPAISA", "5PAISA"]), None)
        
        if not paisa_acc:
            logger.warning("No enabled 5paisa accounts to stream")
            return

        asyncio.create_task(self._main_loop(paisa_acc))

    async def _main_loop(self, account: Account):
        """Main loop that allows re-subscribing as symbols change"""
        while self.running:
            try:
                # Build Subscription List
                scrip_list = list(DYNAMIC_INSTRUMENTS)
                instruments = [{"Exchange": "N", "ExchangeType": "C", "ScripCode": sc} for sc in scrip_list]
                self._current_subs = set(scrip_list)

                ws_url = "wss://openfeed.5paisa.com/feeds"
                async with websockets.connect(ws_url) as websocket:
                    # Authenticate & Subscribe
                    payload = {
                        "Method": "Conf",
                        "Operation": "Subscribe",
                        "ClientCode": account.trading_login_id,
                        "InstrumentList": instruments
                    }
                    await websocket.send(json.dumps(payload))
                    logger.info(f"5paisa real-time stream active for {len(scrip_list)} instruments")

                    while self.running:
                        # CHECK FOR NEW SUBSCRIPTIONS (Re-connect if list changed)
                        if not DYNAMIC_INSTRUMENTS.issubset(self._current_subs):
                            logger.info("New symbols added, re-subscribing...")
                            break # Exit inner loop to re-connect and subscribe

                        try:
                            message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                            data = json.loads(message)
                            scrip_code = data.get("ScripCode")
                            if scrip_code:
                                await self._process_tick(scrip_code, data)
                        except asyncio.TimeoutError:
                            continue # Still alive, just no ticks
            
            except Exception as e:
                logger.error(f"5paisa Stream Error: {e}")
                await asyncio.sleep(5)

    async def _process_tick(self, scrip_code: int, data: Dict[str, Any]):
        """Merges incoming tick with existing cache (No Zero-Overwrite)"""
        cache_key = f"market:FIVEPAISA:{scrip_code}"
        
        # 1. Fetch current (to merge)
        current = await get_cache_value(cache_key) or {}
        
        # 2. Extract NEW data (Only update if present and non-zero)
        def merge(target, source_key, target_key):
            val = data.get(source_key)
            if val is not None and val != 0:
                target[target_key] = val

        # Map 5paisa Webhook fields
        merge(current, "LastRate", "ltp")
        merge(current, "ChgPrc", "change_percent")
        merge(current, "Volume", "volume")
        merge(current, "OpenInterest", "oi")
        merge(current, "LastQty", "ltq")
        merge(current, "AvgRate", "avg_price")
        merge(current, "BidRate", "buy_price")
        merge(current, "OfferRate", "sell_price")
        
        current["timestamp"] = datetime.now().isoformat()

        # 3. Save BACK to Redis
        await set_cache(cache_key, current, expire=30)

    async def stop_streaming(self):
        self.running = False
        logger.info("Market data streaming stopped.")

