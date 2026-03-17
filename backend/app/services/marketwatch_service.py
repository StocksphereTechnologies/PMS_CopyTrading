"""
Marketwatch service: 5PAISA ONLY
MINIMAL FIX: Added _fetch_ltp_batch to get live prices after search.
Everything else is the friend's ORIGINAL code — DO NOT CHANGE.
"""
import asyncio
import aiohttp
import logging
import os
import json
import time
from typing import List, Dict, Any, Optional

from app.models.account import Account
from app.services.account_service import AccountService
from app.adapters.fivepaisa_adapter import FivePaisaAdapter
from app.core.cache import get_cache_value
from app.schemas.marketwatch import InstrumentData

logger = logging.getLogger(__name__)

CACHE_FILE = "instruments_cache_5paisa.json"
FIVEPAISA_MARKET_FEED_URL = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V1/MarketFeed"


class MarketwatchService:

    _memory_cache: Dict[str, Any] = {}

    def __init__(self, db):
        self.db = db
        self._adapters_cache: Dict[int, Any] = {}
        self._cached_paisa_creds = None  # Cache account creds for ticker_loop

    async def _get_adapter(self, account: Account):

        if account.account_id in self._adapters_cache:
            return self._adapters_cache[account.account_id]

        b_name = str(account.broker_name).upper()

        if b_name in ["FIVEPAISA", "5PAISA"]:
            try:
                adapter = FivePaisaAdapter(account=account, db=self.db)
                self._adapters_cache[account.account_id] = adapter
                return adapter
            except Exception as e:
                logger.error(f"Adapter init failed: {e}")

        return None

    def _load_local_cache(self, exch: str):

        key = f"FIVEPAISA_{exch}"

        if key in self._memory_cache:
            return self._memory_cache[key]

        if os.path.exists(CACHE_FILE):

            try:
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f)

                if key in data:

                    if time.time() - data[key]["timestamp"] < 86400:

                        instruments = data[key]["instruments"]
                        self._memory_cache[key] = instruments
                        return instruments

            except Exception:
                pass

        return None

    def _save_local_cache(self, exch: str, instruments):

        key = f"FIVEPAISA_{exch}"

        try:

            data = {}

            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, "r") as f:
                    data = json.load(f)

            data[key] = {
                "timestamp": time.time(),
                "instruments": instruments
            }

            with open(CACHE_FILE, "w") as f:
                json.dump(data, f)

            self._memory_cache[key] = instruments

            logger.info(f"Saved {len(instruments)} instruments for {exch}")

        except Exception as e:
            logger.error(f"Cache save error: {e}")

    async def get_instruments(
        self,
        symbols: Optional[List[str]] = None,
        exchange: Optional[str] = None,
        is_search: bool = False
    ) -> List[InstrumentData]:

        accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)

        accounts = [
            acc for acc in accounts
            if str(acc.broker_name).upper() in ["FIVEPAISA", "5PAISA"]
        ]

        if not accounts:
            logger.warning("No 5paisa accounts")
            return []

        adapters = await asyncio.gather(
            *[self._get_adapter(acc) for acc in accounts]
        )

        adapters = [a for a in adapters if a]

        if not adapters:
            return []

        exchanges = [exchange] if exchange else ["NSE", "NFO", "BSE"]

        instruments: List[InstrumentData] = []

        async def fetch(adapter, exch):

            try:

                broker_instruments = self._load_local_cache(exch)

                if not broker_instruments:
                    broker_instruments = await adapter.get_instruments(exch)

                    if broker_instruments:
                        self._save_local_cache(exch, broker_instruments)

                if not broker_instruments:
                    return []

                normalized = []

                symbol_set = {s.upper() for s in symbols} if symbols else None

                for inst in broker_instruments:

                    symbol = inst.get("Name") or inst.get("Symbol") or inst.get("ShortName")

                    if not symbol:
                        continue

                    if symbol_set and symbol.upper() not in symbol_set:
                        continue

                    obj = await self._normalize_instrument(inst)
                    normalized.append(obj)

                return normalized

            except Exception as e:
                logger.error(f"Fetch error {exch}: {e}")
                return []

        tasks = [fetch(adapters[0], ex) for ex in exchanges]

        results = await asyncio.gather(*tasks)

        for r in results:
            instruments.extend(r)

        # For explicit symbol requests (watchlist), fetch LTP via REST API
        if symbols and instruments:
            await self._fetch_ltp_batch(instruments)

        return instruments

    # Alias: friend's router calls search_instruments, our method is search_symbols
    async def search_instruments(self, query: str, exchange: Optional[str] = None):
        return await self.search_symbols(query, exchange)

    async def search_symbols(self, query: str, exchange: Optional[str] = None):

        instruments = await self.get_instruments(is_search=True)

        if not instruments:
            return []

        # Word-based matching: ALL query words must appear in symbol or name
        # This lets "NIFTY 23450 CE" match "NIFTY 17MAR26 23450 CE"
        query_words = query.lower().split()

        results = []

        for inst in instruments:

            text = f"{inst.symbol or ''} {inst.name or ''}".lower()

            if all(word in text for word in query_words):
                results.append(inst)

            if len(results) >= 100:  # Collect more before sorting
                break

        # Sort by nearest expiry: equity first (no expiry), then F&O by soonest date
        results.sort(key=lambda inst: inst.instrument_token or "9999-99-99")

        # Take top 40 after sorting
        results = results[:40]

        # Fetch LTP for sorted results
        if results:
            await self._fetch_ltp_batch(results)

        return results

    # ═══════════════════════════════════════════════════════════
    # PUBLIC: Fetch LTP for watchlist instruments (called from /ltp endpoint)
    # Uses the SAME _fetch_ltp_batch as search — fresh DB session each call
    # ═══════════════════════════════════════════════════════════
    async def fetch_ltp_for_watchlist(self, raw_instruments: list):
        """Takes [{scrip_code, exchange, symbol}, ...] from frontend, returns LTP data"""
        if not raw_instruments:
            return []

        # Convert to InstrumentData objects
        instruments = []
        for item in raw_instruments[:20]:
            instruments.append(InstrumentData(
                symbol=item.get("symbol", ""),
                exchange=item.get("exchange", "NSE"),
                scrip_code=int(item.get("scrip_code", 0)),
                name=item.get("name", ""),
            ))

        # Fetch live prices using the SAME logic as search
        await self._fetch_ltp_batch(instruments)

        # Return as dicts
        return [inst.model_dump() for inst in instruments]

    # ═══════════════════════════════════════════════════════════
    # PRIVATE: Fetch live prices from 5paisa MarketFeed API
    # ═══════════════════════════════════════════════════════════
    async def _fetch_ltp_batch(self, instruments: List[InstrumentData]):
        """Fetch LTP for a batch of instruments via 5paisa /V1/MarketFeed REST API"""
        try:
            # Use cached credentials if available (avoids stale DB session in ticker_loop)
            if not self._cached_paisa_creds:
                try:
                    accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
                    paisa_acc = next(
                        (acc for acc in accounts
                         if str(acc.broker_name).upper() in ["FIVEPAISA", "5PAISA"]),
                        None
                    )
                    if paisa_acc:
                        self._cached_paisa_creds = {
                            "access_token": paisa_acc.access_token,
                            "user_key": paisa_acc.user_key or paisa_acc.api_key or "",
                        }
                except Exception as db_err:
                    logger.debug(f"DB query failed, using cached creds: {type(db_err).__name__}")

            if not self._cached_paisa_creds:
                logger.warning("No 5paisa credentials for LTP fetch")
                return

            # Build MarketFeed request (max 20 at a time)
            exch_map = {"NSE": "N", "BSE": "B", "NFO": "N", "MCX": "M"}
            exch_type_map = {"NSE": "C", "BSE": "C", "NFO": "D", "MCX": "D"}

            feed_req = []
            for inst in instruments[:20]:
                if inst.scrip_code:
                    feed_req.append({
                        "Exch": exch_map.get(inst.exchange, "N"),
                        "ExchType": exch_type_map.get(inst.exchange, "C"),
                        "ScripCode": int(inst.scrip_code),
                    })

            if not feed_req:
                return

            payload = {
                "head": {"key": self._cached_paisa_creds["user_key"]},
                "body": {
                    "Count": len(feed_req),
                    "MarketFeedData": feed_req,
                    "ClientLoginType": 0,
                    "LastRequestTime": "/Date(0)/",
                    "RefreshRate": "H"
                }
            }

            # Retry up to 3 times — openapi.5paisa.com has intermittent connection issues
            data = None
            for attempt in range(3):
                try:
                    connector = aiohttp.TCPConnector(ssl=False)
                    timeout = aiohttp.ClientTimeout(total=15)
                    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                        async with session.post(
                            FIVEPAISA_MARKET_FEED_URL,
                            json=payload,
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {self._cached_paisa_creds['access_token']}"
                            }
                        ) as response:
                            if response.status != 200:
                                logger.error(f"MarketFeed API error: {response.status}")
                                return
                            data = await response.json()
                    break  # Success
                except (aiohttp.ServerDisconnectedError, aiohttp.ClientConnectorError,
                        aiohttp.ClientOSError, ConnectionResetError) as conn_err:
                    if attempt < 2:
                        logger.debug(f"MarketFeed retry {attempt+1}/3: {type(conn_err).__name__}")
                        await asyncio.sleep(1)
                    else:
                        raise  # Final attempt — let outer handler log it

            if not data:
                return

            feeds = data.get("body", {}).get("Data", [])

            if not feeds:
                logger.warning(f"MarketFeed returned no data. Keys: {list(data.get('body', {}).keys())}")
                return

            # Build lookup by scrip code
            tick_map = {}
            for f in feeds:
                key = str(f.get("Token") or f.get("ScripCode", ""))
                tick_map[key] = f

            # Attach LTP to each instrument
            for inst in instruments:
                tick = tick_map.get(str(inst.scrip_code))
                if tick:
                    inst.last_price = float(tick.get("LastRate") or 0)
                    inst.change = float(tick.get("Chg") or 0)
                    inst.change_percent = float(tick.get("ChgPrc") or 0)
                    inst.volume = int(tick.get("Volume") or 0)
                    inst.high = float(tick.get("High") or 0)
                    inst.low = float(tick.get("Low") or 0)
                    inst.open = float(tick.get("Open") or 0)
                    inst.close = float(tick.get("PClose") or 0)

            logger.info(f"✅ LTP fetched for {len(feeds)}/{len(instruments)} instruments")

        except Exception as e:
            logger.error(f"❌ LTP batch fetch error ({type(e).__name__}): {repr(e)}")

    async def _normalize_instrument(self, inst):

        symbol = inst.get("Name") or inst.get("Symbol") or inst.get("ShortName")

        scrip = inst.get("ScripCode") or inst.get("Scrip_Code") or inst.get("Token")

        # Use ExchType to correctly distinguish NSE cash vs NFO derivatives
        exch_type = inst.get("ExchType", "C")
        if exch_type == "D":
            exchange = "NFO"
        else:
            exchange = self._map_exchange_code(inst.get("Exchange"))

        # Store expiry in instrument_token (unused field) for sorting
        expiry = inst.get("Expiry", "")

        return InstrumentData(
            symbol=symbol,
            exchange=exchange,
            instrument_token=expiry if expiry else None,
            scrip_code=int(scrip) if scrip else 0,
            name=inst.get("FullName") or symbol,
        )

    def _map_exchange_code(self, code):

        mapping = {
            "N": "NSE",
            "B": "BSE",
            "D": "NFO",
            "NSE": "NSE",
            "BSE": "BSE",
            "NFO": "NFO"
        }

        return mapping.get(str(code).upper(), str(code))

    async def _attach_realtime_tick(self, inst):

        try:

            if not inst.scrip_code:
                return

            key = f"market:FIVEPAISA:{inst.scrip_code}"

            tick = await get_cache_value(key)

            if tick:

                inst.last_price = tick.get("ltp") or tick.get("LastRate") or 0
                inst.change = tick.get("change") or tick.get("Chg") or 0
                inst.change_percent = tick.get("pchange") or tick.get("pChg") or 0
                inst.volume = tick.get("volume") or tick.get("Volume") or 0

        except:
            pass
# """
# Marketwatch service: 5PAISA ONLY
# MINIMAL FIX: Added _fetch_ltp_batch to get live prices after search.
# Everything else is the friend's ORIGINAL code — DO NOT CHANGE.
# """
# import asyncio
# import aiohttp
# import logging
# import os
# import json
# import time
# from typing import List, Dict, Any, Optional

# from app.models.account import Account
# from app.services.account_service import AccountService
# from app.adapters.fivepaisa_adapter import FivePaisaAdapter
# from app.core.cache import get_cache_value
# from app.schemas.marketwatch import InstrumentData

# logger = logging.getLogger(__name__)

# CACHE_FILE = "instruments_cache_5paisa.json"
# FIVEPAISA_MARKET_FEED_URL = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V1/MarketFeed"


# class MarketwatchService:

#     _memory_cache: Dict[str, Any] = {}

#     def __init__(self, db):
#         self.db = db
#         self._adapters_cache: Dict[int, Any] = {}

#     async def _get_adapter(self, account: Account):

#         if account.account_id in self._adapters_cache:
#             return self._adapters_cache[account.account_id]

#         b_name = str(account.broker_name).upper()

#         if b_name in ["FIVEPAISA", "5PAISA"]:
#             try:
#                 adapter = FivePaisaAdapter(account=account, db=self.db)
#                 self._adapters_cache[account.account_id] = adapter
#                 return adapter
#             except Exception as e:
#                 logger.error(f"Adapter init failed: {e}")

#         return None

#     def _load_local_cache(self, exch: str):

#         key = f"FIVEPAISA_{exch}"

#         if key in self._memory_cache:
#             return self._memory_cache[key]

#         if os.path.exists(CACHE_FILE):

#             try:
#                 with open(CACHE_FILE, "r") as f:
#                     data = json.load(f)

#                 if key in data:

#                     if time.time() - data[key]["timestamp"] < 86400:

#                         instruments = data[key]["instruments"]
#                         self._memory_cache[key] = instruments
#                         return instruments

#             except Exception:
#                 pass

#         return None

#     def _save_local_cache(self, exch: str, instruments):

#         key = f"FIVEPAISA_{exch}"

#         try:

#             data = {}

#             if os.path.exists(CACHE_FILE):
#                 with open(CACHE_FILE, "r") as f:
#                     data = json.load(f)

#             data[key] = {
#                 "timestamp": time.time(),
#                 "instruments": instruments
#             }

#             with open(CACHE_FILE, "w") as f:
#                 json.dump(data, f)

#             self._memory_cache[key] = instruments

#             logger.info(f"Saved {len(instruments)} instruments for {exch}")

#         except Exception as e:
#             logger.error(f"Cache save error: {e}")

#     async def get_instruments(
#         self,
#         symbols: Optional[List[str]] = None,
#         exchange: Optional[str] = None,
#         is_search: bool = False
#     ) -> List[InstrumentData]:

#         accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)

#         accounts = [
#             acc for acc in accounts
#             if str(acc.broker_name).upper() in ["FIVEPAISA", "5PAISA"]
#         ]

#         if not accounts:
#             logger.warning("No 5paisa accounts")
#             return []

#         adapters = await asyncio.gather(
#             *[self._get_adapter(acc) for acc in accounts]
#         )

#         adapters = [a for a in adapters if a]

#         if not adapters:
#             return []

#         exchanges = [exchange] if exchange else ["NSE", "NFO", "BSE"]

#         instruments: List[InstrumentData] = []

#         async def fetch(adapter, exch):

#             try:

#                 broker_instruments = self._load_local_cache(exch)

#                 if not broker_instruments:
#                     broker_instruments = await adapter.get_instruments(exch)

#                     if broker_instruments:
#                         self._save_local_cache(exch, broker_instruments)

#                 if not broker_instruments:
#                     return []

#                 normalized = []

#                 symbol_set = {s.upper() for s in symbols} if symbols else None

#                 for inst in broker_instruments:

#                     symbol = inst.get("Name") or inst.get("Symbol") or inst.get("ShortName")

#                     if not symbol:
#                         continue

#                     if symbol_set and symbol.upper() not in symbol_set:
#                         continue

#                     obj = await self._normalize_instrument(inst)

#                     if symbols:
#                         await self._attach_realtime_tick(obj)

#                     normalized.append(obj)

#                 return normalized

#             except Exception as e:
#                 logger.error(f"Fetch error {exch}: {e}")
#                 return []

#         tasks = [fetch(adapters[0], ex) for ex in exchanges]

#         results = await asyncio.gather(*tasks)

#         for r in results:
#             instruments.extend(r)

#         return instruments

#     async def search_instruments(self, query: str):
#         instruments = await self.get_instruments()

#         if not instruments:
#             return []

#         query = query.lower()

#         return [
#             item for item in instruments
#             if query in (item.symbol or "").lower()
#             or query in (item.name or "").lower()
#         ]


#     async def search_symbols(self, query: str):

#         instruments = await self.get_instruments(is_search=True)

#         if not instruments:
#             return []

#         # Word-based matching: ALL query words must appear in symbol or name
#         # This lets "NIFTY 23450 CE" match "NIFTY 17MAR26 23450 CE"
#         query_words = query.lower().split()

#         results = []

#         for inst in instruments:

#             text = f"{inst.symbol or ''} {inst.name or ''}".lower()

#             if all(word in text for word in query_words):
#                 results.append(inst)

#             if len(results) >= 100:  # Collect more before sorting
#                 break

#         # Sort by nearest expiry: equity first (no expiry), then F&O by soonest date
#         results.sort(key=lambda inst: inst.instrument_token or "9999-99-99")

#         # Take top 40 after sorting
#         results = results[:40]

#         # Fetch LTP for sorted results
#         if results:
#             await self._fetch_ltp_batch(results)

#         return results

#     # ═══════════════════════════════════════════════════════════
#     # NEW METHOD: Fetch live prices from 5paisa MarketFeed API
#     # ═══════════════════════════════════════════════════════════
#     async def _fetch_ltp_batch(self, instruments: List[InstrumentData]):
#         """Fetch LTP for a batch of instruments via 5paisa /V1/MarketFeed REST API"""
#         try:
#             # Get 5paisa account for auth token
#             accounts = await AccountService.get_all_accounts(self.db, enabled_only=True)
#             paisa_acc = next(
#                 (acc for acc in accounts
#                  if str(acc.broker_name).upper() in ["FIVEPAISA", "5PAISA"]),
#                 None
#             )
#             if not paisa_acc:
#                 logger.warning("No 5paisa account for LTP fetch")
#                 return

#             # Build MarketFeed request (max 20 at a time)
#             exch_map = {"NSE": "N", "BSE": "B", "NFO": "N", "MCX": "M"}
#             exch_type_map = {"NSE": "C", "BSE": "C", "NFO": "D", "MCX": "D"}

#             feed_req = []
#             for inst in instruments[:20]:
#                 if inst.scrip_code:
#                     feed_req.append({
#                         "Exch": exch_map.get(inst.exchange, "N"),
#                         "ExchType": exch_type_map.get(inst.exchange, "C"),
#                         "ScripCode": int(inst.scrip_code),
#                     })

#             if not feed_req:
#                 return

#             payload = {
#                 "head": {"key": paisa_acc.user_key or paisa_acc.api_key or ""},
#                 "body": {
#                     "Count": len(feed_req),
#                     "MarketFeedData": feed_req,
#                     "ClientLoginType": 0,
#                     "LastRequestTime": "/Date(0)/",
#                     "RefreshRate": "H"
#                 }
#             }

#             # ssl=False needed because 5paisa API has cert issues
#             # (py5paisa SDK also uses verify=False for all requests)
#             connector = aiohttp.TCPConnector(ssl=False)
#             async with aiohttp.ClientSession(connector=connector) as session:
#                 async with session.post(
#                     FIVEPAISA_MARKET_FEED_URL,
#                     json=payload,
#                     headers={
#                         "Content-Type": "application/json",
#                         "Authorization": f"Bearer {paisa_acc.access_token}"
#                     }
#                 ) as response:
#                     if response.status != 200:
#                         logger.error(f"MarketFeed API error: {response.status}")
#                         return
#                     data = await response.json()
#             feeds = data.get("body", {}).get("Data", [])

#             if not feeds:
#                 logger.warning(f"MarketFeed returned no data. Keys: {list(data.get('body', {}).keys())}")
#                 return

#             # Build lookup by scrip code
#             tick_map = {}
#             for f in feeds:
#                 key = str(f.get("Token") or f.get("ScripCode", ""))
#                 tick_map[key] = f

#             # Attach LTP to each instrument
#             for inst in instruments:
#                 tick = tick_map.get(str(inst.scrip_code))
#                 if tick:
#                     inst.last_price = float(tick.get("LastRate") or 0)
#                     inst.change = float(tick.get("Chg") or 0)
#                     inst.change_percent = float(tick.get("ChgPrc") or 0)
#                     inst.volume = int(tick.get("Volume") or 0)
#                     inst.high = float(tick.get("High") or 0)
#                     inst.low = float(tick.get("Low") or 0)
#                     inst.open = float(tick.get("Open") or 0)
#                     inst.close = float(tick.get("PClose") or 0)

#             logger.info(f"✅ LTP fetched for {len(feeds)}/{len(instruments)} instruments")

#         except Exception as e:
#             logger.error(f"❌ LTP batch fetch error ({type(e).__name__}): {repr(e)}")

#     async def _normalize_instrument(self, inst):

#         symbol = inst.get("Name") or inst.get("Symbol") or inst.get("ShortName")

#         scrip = inst.get("ScripCode") or inst.get("Scrip_Code") or inst.get("Token")

#         # Use ExchType to correctly distinguish NSE cash vs NFO derivatives
#         exch_type = inst.get("ExchType", "C")
#         if exch_type == "D":
#             exchange = "NFO"
#         else:
#             exchange = self._map_exchange_code(inst.get("Exchange"))

#         # Store expiry in instrument_token (unused field) for sorting
#         expiry = inst.get("Expiry", "")

#         return InstrumentData(
#             symbol=symbol,
#             exchange=exchange,
#             instrument_token=expiry if expiry else None,
#             scrip_code=int(scrip) if scrip else 0,
#             name=inst.get("FullName") or symbol,
#         )

#     def _map_exchange_code(self, code):

#         mapping = {
#             "N": "NSE",
#             "B": "BSE",
#             "D": "NFO",
#             "NSE": "NSE",
#             "BSE": "BSE",
#             "NFO": "NFO"
#         }

#         return mapping.get(str(code).upper(), str(code))

#     async def _attach_realtime_tick(self, inst):

#         try:

#             if not inst.scrip_code:
#                 return

#             key = f"market:FIVEPAISA:{inst.scrip_code}"

#             tick = await get_cache_value(key)

#             if tick:

#                 inst.last_price = tick.get("ltp") or tick.get("LastRate") or 0
#                 inst.change = tick.get("change") or tick.get("Chg") or 0
#                 inst.change_percent = tick.get("pchange") or tick.get("pChg") or 0
#                 inst.volume = tick.get("volume") or tick.get("Volume") or 0

#         except:
#             pass