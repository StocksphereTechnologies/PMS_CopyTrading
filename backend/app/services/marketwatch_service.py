"""
Marketwatch service: 5PAISA — CONTINUOUS & PERSISTENT
1. Ensures OI, AvgPrice, and Depth STICK to the table once fetched.
2. Merges high-frequency LTP updates without clearing other fields.
3. Automatically subscribes new symbols to the live WebSocket stream.
"""
import asyncio
import aiohttp
import logging
import os
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.models.account import Account
from app.services.account_service import AccountService
from app.adapters.fivepaisa_adapter import FivePaisaAdapter
from app.core.cache import get_cache_value
from app.schemas.marketwatch import InstrumentData
from app.services.market_data_stream import MarketDataStream # Sync Link

logger = logging.getLogger(__name__)

CACHE_FILE = "instruments_cache_5paisa.json"
FIVEPAISA_MARKET_FEED_URL = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V1/MarketFeed"


class MarketwatchService:

    _memory_cache: Dict[str, Any] = {}
    
    # 🔥 GLOBAL PERSISTENT MEMORY (Ensures data sticks!)
    _persistent_store: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db):
        self.db = db
        self._adapters_cache: Dict[int, Any] = {}
        self._cached_paisa_creds = None

    async def _get_adapter(self, account: Account):
        if account.account_id in self._adapters_cache:
            return self._adapters_cache[account.account_id]
        if str(account.broker_name).upper() in ["FIVEPAISA", "5PAISA"]:
            try:
                adapter = FivePaisaAdapter(account=account, db=self.db)
                self._adapters_cache[account.account_id] = adapter
                return adapter
            except Exception as e:
                logger.error(f"Adapter error: {e}")
        return None

    async def get_instruments(
        self,
        symbols: Optional[List[str]] = None,
        exchange: Optional[str] = None
    ) -> List[InstrumentData]:
        # Basic instrument lookup
        accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
        acc = next((a for a in accounts if str(a.broker_name).upper() in ["FIVEPAISA", "5PAISA"]), None)
        if not acc: return []
        adapter = await self._get_adapter(acc)
        if not adapter: return []

        exchanges = [exchange] if exchange else ["NSE", "NFO", "BSE"]
        instruments: List[InstrumentData] = []

        async def fetch(ex):
            try:
                key = f"FIVEPAISA_{ex}"
                insts = self._memory_cache.get(key)
                if not insts:
                    if os.path.exists(CACHE_FILE):
                        with open(CACHE_FILE, "r") as f:
                            data = json.load(f)
                            if key in data: insts = data[key]["instruments"]
                if not insts:
                    insts = await adapter.get_instruments(ex)
                    if insts:
                        self._memory_cache[key] = insts
                        all_d = {}
                        if os.path.exists(CACHE_FILE):
                            with open(CACHE_FILE, "r") as f: all_d = json.load(f)
                        all_d[key] = {"timestamp": time.time(), "instruments": insts}
                        with open(CACHE_FILE, "w") as f: json.dump(all_d, f)
                
                normalized = []
                sym_set = {s.upper() for s in symbols} if symbols else None
                for i in (insts or []):
                    # Optimized matching
                    s = i.get("Name") or i.get("Symbol") or ""
                    if sym_set and s.upper() not in sym_set:
                        if i.get("Symbol", "").upper() not in sym_set: continue
                    normalized.append(await self._normalize_instrument(i))
                return normalized
            except Exception: return []

        results = await asyncio.gather(*[fetch(ex) for ex in exchanges])
        for r in results: instruments.extend(r)

        if symbols and instruments:
            await self._fetch_ltp_batch(instruments)
        return instruments

    async def search_symbols(self, query: str, exchange: Optional[str] = None):
        """Standard search method called by the API route"""
        instruments = await self.get_instruments(exchange=exchange)
        if not instruments: return []
        q = query.lower()
        results = [i for i in instruments if q in (i.symbol or "").lower() or q in (i.name or "").lower()]
        results = results[:40]
        if results: 
            await self._fetch_ltp_batch(results)
        return results

    async def fetch_ltp_for_watchlist(self, raw_instruments: list):
        if not raw_instruments: return []
        
        # 🚀 ROBUST SCRIP-CODE RESOLUTION
        tasks = [self.get_instruments(symbols=[i.get("symbol")], exchange=i.get("exchange")) for i in raw_instruments]
        resolved = await asyncio.gather(*tasks)
        instruments = [r[0] for r in resolved if r]

        await self._fetch_ltp_batch(instruments)
        return [inst.model_dump() for inst in instruments]

    async def _fetch_ltp_batch(self, instruments: List[InstrumentData]):
        try:
            creds = await self._get_cached_creds()
            if not creds: return

            exch_map = {"NSE": "N", "BSE": "B", "NFO": "N", "MCX": "M"}
            exch_type_map = {"NSE": "C", "BSE": "C", "NFO": "D", "MCX": "D"}

            feed_req = [
                {"Exch": exch_map.get(i.exchange, "N"), "ExchType": exch_type_map.get(i.exchange, "C"), "ScripCode": int(i.scrip_code)}
                for i in instruments if i.scrip_code
            ]
            if not feed_req: return

            payload = {
                "head": {"key": creds["user_key"]},
                "body": {"Count": len(feed_req), "MarketFeedData": feed_req, "ClientLoginType": 0, "LastRequestTime": "/Date(0)/", "RefreshRate": "H"}
            }

            data = await self._post_request(FIVEPAISA_MARKET_FEED_URL, payload, creds["access_token"])
            if data and data.get("body", {}).get("Data"):
                feeds = data["body"]["Data"]
                print(f"\n📊 5PAISA TICK: {json.dumps(feeds[0])}\n") # Live debugging
                tick_map = {str(f.get("Token") or f.get("ScripCode", "")): f for f in feeds}
                self._sync_and_persist(instruments, tick_map)
        except Exception as e:
            logger.error(f"LTP fetch error: {e}")

    def _sync_and_persist(self, instruments, tick_map):
        """Syncs from API and merges with persistent memory"""
        
        def safe_update(obj, field, val, key):
            # 🔥 PERSISTENCE: If API sends 0/Null, use last known GOOD value
            if (val is None or val == 0) and key in self._persistent_store:
                val = self._persistent_store[key].get(field, val)
            
            if val is not None:
                try:
                    setattr(obj, field, val)
                    # Update Memory
                    if key not in self._persistent_store: self._persistent_store[key] = {}
                    if val != 0: self._persistent_store[key][field] = val
                except: pass

        for inst in instruments:
            k = str(inst.scrip_code)
            tick = tick_map.get(k)
            if tick:
                lr = float(tick.get("LastRate") or tick.get("LTP") or 0)
                pc = float(tick.get("PClose") or tick.get("Close") or 0)
                chg = float(tick.get("Chg") or 0)
                cp = tick.get("ChgPcnt") or tick.get("ChgPrc") or 0
                if pc > 0 and (not cp): cp = ((lr-pc)/pc)*100

                safe_update(inst, "last_price", lr, k)
                safe_update(inst, "prev_close", pc, k)
                safe_update(inst, "change", chg, k)
                safe_update(inst, "change_percent", round(float(cp), 2), k)
                safe_update(inst, "volume", int(tick.get("TotalQty") or tick.get("Volume") or 0), k)
                safe_update(inst, "high", float(tick.get("High") or 0), k)
                safe_update(inst, "low", float(tick.get("Low") or 0), k)
                safe_update(inst, "open", float(tick.get("Open") or 0), k)
                
                # 🔥 OI & Extended Depth
                safe_update(inst, "oi", int(tick.get("OpenInterest") or tick.get("OI") or 0), k)
                safe_update(inst, "ltq", int(tick.get("LastQty") or tick.get("LTQ") or 0), k)
                safe_update(inst, "avg_price", float(tick.get("AvgRate") or tick.get("AvgPrice") or 0), k)
                safe_update(inst, "buy_price", float(tick.get("BidRate") or tick.get("BidPrice") or 0), k)
                safe_update(inst, "sell_price", float(tick.get("OffRate") or tick.get("OfferRate") or 0), k)

                # Time (Auto-refresh if stale)
                ltt = tick.get("TickDt") or tick.get("TickTime") or ""
                if "/Date(" in str(ltt):
                    try:
                        ts = int(str(ltt).split("(")[1].split("+")[0].split(")")[0]) / 1000
                        # If more than 30 mins old, it's a stale rest capture - use current time
                        if time.time() - ts > 1800: ltt_str = datetime.now().strftime("%H:%M:%S")
                        else: ltt_str = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
                    except: ltt_str = datetime.now().strftime("%H:%M:%S")
                else: ltt_str = str(ltt) if ltt else datetime.now().strftime("%H:%M:%S")
                safe_update(inst, "last_trade_time", ltt_str, k)

                # 🔥 AUTO-SUBSCRIBE TO LIVE STREAM
                MarketDataStream.subscribe(inst.scrip_code)
            
            # 🔥 LIVE REAL-TIME OVERLAY
            asyncio.create_task(self._attach_live_tick(inst))

    async def _attach_live_tick(self, inst):
        try:
            if inst.scrip_code:
                k = str(inst.scrip_code)
                live = await get_cache_value(f"market:FIVEPAISA:{k}")
                if live:
                    # Update all real-time fields
                    if live.get("ltp"): inst.last_price = live["ltp"]
                    if live.get("change_percent"): inst.change_percent = live["change_percent"]
                    if live.get("volume"): inst.volume = live["volume"]
                    if live.get("oi"): inst.oi = live["oi"]
                    
                    # Update Time to NOW for live feedback
                    inst.last_trade_time = datetime.now().strftime("%H:%M:%S")
                    
                    # Store in persistent memory to survive next REST poll
                    if k not in self._persistent_store: self._persistent_store[k] = {}
                    self._persistent_store[k].update(live)
                    self._persistent_store[k]["last_trade_time"] = inst.last_trade_time
        except Exception: pass

    async def _get_cached_creds(self):
        if not self._cached_paisa_creds:
            try:
                accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
                acc = next((a for a in accounts if str(a.broker_name).upper() in ["FIVEPAISA", "5PAISA"]), None)
                if acc: self._cached_paisa_creds = {"access_token": acc.access_token, "user_key": acc.user_key or ""}
            except Exception: pass
        return self._cached_paisa_creds

    async def _post_request(self, url, payload, token):
        try:
            connector = aiohttp.TCPConnector(ssl=False)
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=8)) as s:
                async with s.post(url, json=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}) as r:
                    return await r.json() if r.status == 200 else None
        except Exception: return None

    async def _normalize_instrument(self, inst):
        s = inst.get("Name") or inst.get("Symbol") or ""
        sc = inst.get("ScripCode") or inst.get("Scrip_Code") or inst.get("Token")
        et = inst.get("ExchType", "C")
        ex = "NFO" if et == "D" else self._map_exchange_code(inst.get("Exchange"))
        return InstrumentData(symbol=s, exchange=ex, scrip_code=int(sc) if sc else 0, name=inst.get("FullName") or s)

    def _map_exchange_code(self, code):
        m = {"N": "NSE", "B": "BSE", "D": "NFO", "NSE": "NSE", "BSE": "BSE", "NFO": "NFO"}
        return m.get(str(code).upper(), str(code))
        

