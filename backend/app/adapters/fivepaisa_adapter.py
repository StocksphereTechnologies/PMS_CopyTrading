"""
5paisa Adapter — Friend's ORIGINAL code
CHANGES: get_instruments uses correct API URL + column names from py5paisa SDK source.
"""
from app.adapters.base import BrokerInterface
from app.models.account import Account
from app.services.fivepaisa_rest_client import FivePaisaRestClient
from app.services.scrip_master_service import ScripMasterService
from app.core.config import settings
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import aiohttp
from io import StringIO
from datetime import datetime

logger = logging.getLogger(__name__)

# Static CSV — contains ALL segments (NSE + NFO + BSE + MCX)
SCRIP_MASTER_URL = "https://images.5paisa.com/website/scripmaster-csv-format.csv"

# Segment-specific API URLs (much faster for individual segments)
SCRIP_MASTER_SEGMENT_URL = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/{segment}"

# Map exchange names to segment slugs for the segment API
SEGMENT_MAP = {
    "NSE": "nse_eq",
    "BSE": "bse_eq",
    "NFO": "nse_fo",
}

# Only cache these popular F&O underlyings (keeps NFO cache manageable)
POPULAR_FNO_UNDERLYINGS = {
    "NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCPNIFTY", "SENSEX",
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK",
    "SBIN", "TATAMOTORS", "TATASTEEL", "BAJFINANCE", "LT",
    "AXISBANK", "KOTAKBANK", "ITC", "HINDUNILVR", "WIPRO",
    "MARUTI", "BHARTIARTL", "SUNPHARMA", "DRREDDY", "ASIANPAINT",
    "ADANIENT", "ADANIPORTS", "TITAN", "ULTRACEMCO", "POWERGRID",
    "M&M", "HEROMOTOCO", "ONGC", "COALINDIA", "NTPC",
    "JSWSTEEL", "HINDALCO", "TATACONSUM", "CIPLA", "BPCL",
}


def _format_expiry(expiry_str: str) -> str:
    """Convert expiry date to short format like '17MAR26'"""
    if not expiry_str or expiry_str.strip() == "":
        return ""
    try:
        for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S",
                    "%d %b %Y", "%d-%m-%Y", "%Y%m%d"]:
            try:
                dt = datetime.strptime(expiry_str.strip()[:10], fmt)
                return dt.strftime("%d%b%y").upper()
            except ValueError:
                continue
        return expiry_str.strip()[:9]
    except Exception:
        return ""


def _is_expired(expiry_str: str) -> bool:
    """Check if an instrument has expired"""
    if not expiry_str or expiry_str.strip() == "":
        return False  # Equity has no expiry, not expired
    try:
        for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S",
                    "%d %b %Y", "%d-%m-%Y", "%Y%m%d"]:
            try:
                dt = datetime.strptime(expiry_str.strip()[:10], fmt)
                return dt.date() < datetime.now().date()
            except ValueError:
                continue
    except Exception:
        pass
    return False


class FivePaisaAdapter(BrokerInterface):
    """5paisa API adapter using direct REST client"""
    
    def __init__(self, account: Account, db: Optional[AsyncSession] = None):
        self.account = account
        self.db = db
        self.cred = {
            "APP_NAME": account.api_key,
            "APP_SOURCE": account.app_source or "10074",
            "USER_ID": account.trading_login_id,
            "PASSWORD": account.encrypted_password,
            "USER_KEY": account.user_key or account.api_key,
            "ENCRYPTION_KEY": account.api_secret
        }
        self.client = FivePaisaRestClient(credentials=self.cred)
        self.client.access_token = account.access_token
        self.client.client_code = account.trading_login_id
    
    async def get_margins(self) -> Dict:
        return {
            "equity": {"available": {"cash": 100000.0}},
            "commodity": {"available": {"cash": 50000.0}}
        }

    async def get_positions(self) -> List[Dict]:
        return []
    
    async def _download_scrip_master(self, exchange: str = "NSE") -> str:
        """Download scrip master CSV.
        For NFO: tries segment-specific URL first (much smaller/faster).
        Falls back to the full static CSV."""
        
        urls = []
        
        # Try segment-specific URL first (fast, returns only that segment)
        segment = SEGMENT_MAP.get(exchange)
        if segment:
            urls.append(SCRIP_MASTER_SEGMENT_URL.format(segment=segment))
        
        # Fallback to full CSV (contains all segments)
        urls.append(SCRIP_MASTER_URL)

        for url in urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            if text and len(text) > 100:
                                logger.info(f"✅ Scrip master downloaded: {len(text)} bytes from {url[:60]}")
                                return text
                        logger.warning(f"URL returned status {resp.status}: {url[:60]}")
            except Exception as e:
                logger.warning(f"Download failed ({type(e).__name__}: {repr(e)}): {url[:60]}")

        logger.error(f"❌ All scrip master URLs failed for {exchange}!")
        return ""

    async def get_instruments(self, exchange: str) -> List[Dict]:
        """
        Fetch instruments from 5paisa scrip master CSV.
        Column names matched to actual py5paisa SDK source.
        """
        try:
            csv_text = await self._download_scrip_master(exchange)
            if not csv_text:
                logger.error("❌ No scrip master data available")
                return []

            reader = csv.DictReader(StringIO(csv_text.strip()))

            # Log column names on first run (helps debug)
            rows = list(reader)
            if rows:
                logger.info(f"CSV columns: {list(rows[0].keys())[:15]}")
            else:
                logger.error("❌ CSV parsed but no rows found")
                return []

            instruments = []

            for row in rows:

                exch = row.get("Exch")
                exch_type = row.get("ExchType")

                # Filter by exchange
                if exchange == "NSE" and not (exch == "N" and exch_type == "C"):
                    continue
                if exchange == "BSE" and not (exch == "B" and exch_type == "C"):
                    continue
                if exchange == "NFO" and not (exch == "N" and exch_type == "D"):
                    continue

                # ── Confirmed CSV columns: Name, Expiry, CpType, StrikeRate, ScripCode ──
                # Name for equity = "RELIANCE"
                # Name for F&O = "NIFTY 25 Jun 2026 CE 23000.00" (full derivative string)
                name_col = row.get("Name") or ""
                scrip = row.get("Scripcode") or row.get("ScripCode") or ""

                if not name_col or not scrip:
                    continue

                # For derivatives: build clean display name from individual columns
                if exch_type == "D":
                    expiry = row.get("Expiry") or ""
                    
                    # Skip expired instruments
                    if _is_expired(expiry):
                        continue

                    # Extract underlying and filter to popular names only
                    underlying = name_col.split()[0] if name_col else ""
                    if underlying.upper() not in POPULAR_FNO_UNDERLYINGS:
                        continue

                    strike = row.get("StrikeRate") or ""
                    cp_type = (row.get("CpType") or "").strip().upper()

                    # Fallback: parse CE/PE and strike from Name column
                    # Name format: "NIFTY 20 Mar 2026 CE 23500.00"
                    # Some CSV sources leave CpType/StrikeRate empty
                    if not cp_type or cp_type == "XX":
                        name_upper = name_col.upper()
                        if " CE " in name_upper:
                            cp_type = "CE"
                        elif " PE " in name_upper:
                            cp_type = "PE"

                    if not strike or strike == "0":
                        # Try to extract strike from Name (last token is usually strike)
                        name_parts = name_col.split()
                        if name_parts:
                            last_part = name_parts[-1]
                            try:
                                strike = str(float(last_part))
                            except (ValueError, TypeError):
                                pass

                    expiry_short = _format_expiry(expiry)

                    parts = [underlying]
                    if expiry_short:
                        parts.append(expiry_short)

                    # Futures: no CE/PE type
                    if not cp_type or cp_type in ("XX", ""):
                        parts.append("FUT")
                    else:
                        # Options: add strike + CE/PE
                        try:
                            strike_val = float(strike) if strike else 0
                            if strike_val > 0:
                                parts.append(str(int(strike_val)))
                        except (ValueError, TypeError):
                            pass
                        parts.append(cp_type)

                    display_name = " ".join(parts)
                    fullname = name_col  # Keep original (e.g. "NIFTY 25 Jun 2026 CE 23000.00")
                else:
                    display_name = name_col
                    fullname = name_col

                instruments.append({
                    "Symbol": display_name,
                    "Name": display_name,
                    "FullName": fullname,
                    "Exchange": exch,
                    "ExchType": exch_type,
                    "ScripCode": int(scrip),
                    "Expiry": row.get("Expiry") or "",  # Pass through for sorting
                })

            logger.info(f"✅ Loaded {len(instruments)} instruments for {exchange}")
            return instruments

        except Exception as e:
            logger.error(f"❌ 5paisa instrument load failed: {e}", exc_info=True)
            return []
    
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        return 2500.50
    
    def normalize_symbol(self, symbol: str, exchange: str) -> str:
        return symbol.upper()
    
    async def place_order(self, order_params: Dict) -> Dict:
        """Place order with 5paisa — UNCHANGED from original"""
        try:
            scrip_code = order_params.get("scrip_code")
            if not scrip_code:
                symbol = order_params.get("tradingsymbol") or order_params.get("symbol")
                exchange = order_params.get("exchange", "NSE")
                scrip_code = ScripMasterService.get_scrip_code(symbol, exchange)
                
            if not scrip_code:
                 return {
                    "order_id": None,
                    "status": "FAILED",
                    "error": f"Could not resolve ScripCode for {order_params.get('tradingsymbol')}"
                }

            side = order_params.get("transaction_type")
            order_type = "B" if side == "BUY" else "S"
            
            exchange = order_params.get("exchange", "NSE")
            exch_type = "C"
            if exchange == "MCX": exch_type = "D"
            
            product = order_params.get("product", "INTRADAY")
            is_intraday = (product == "INTRADAY")

            logger.info(f"Placing 5paisa order via REST: {order_params.get('symbol')} ({scrip_code})")
            
            result = await self.client.place_order(
                scrip_code=scrip_code,
                exchange=exchange[0],
                exchange_type=exch_type,
                order_type=order_type,
                quantity=int(order_params.get("quantity", 0)),
                price=float(order_params.get("price", 0)),
                is_intraday=is_intraday,
                at_market=(order_params.get("order_type") == "MARKET"),
                stop_loss_price=float(order_params.get("trigger_price", 0)),
                disclosed_qty=int(order_params.get("disclosed_qty", 0)),
                target_price=float(order_params.get("target", 0)),
                trailing_sl=float(order_params.get("trailing_stoploss", 0)),
                variety=order_params.get("variety", "regular"),
                is_amo=order_params.get("is_amo", False)
            )
            
            if result.get("success"):
                return {
                    "order_id": result.get("order_id"),
                    "status": "SUCCESS",
                    "message": result.get("message")
                }
            else:
                return {
                    "order_id": None,
                    "status": "FAILED",
                    "error": result.get("error")
                }

        except Exception as e:
            logger.error(f"Error placing 5paisa order: {e}")
            return {
                "order_id": None,
                "status": "FAILED",
                "error": str(e)
            }
# """
# 5paisa Adapter — Friend's ORIGINAL code
# CHANGES: get_instruments uses correct API URL + column names from py5paisa SDK source.
# """
# from app.adapters.base import BrokerInterface
# from app.models.account import Account
# from app.services.fivepaisa_rest_client import FivePaisaRestClient
# from app.services.scrip_master_service import ScripMasterService
# from app.core.config import settings
# import logging
# from typing import Dict, List, Optional
# from sqlalchemy.ext.asyncio import AsyncSession
# import csv
# import aiohttp
# from io import StringIO
# from datetime import datetime

# logger = logging.getLogger(__name__)

# # Static CSV — this was working in the friend's original code
# SCRIP_MASTER_URL = "https://images.5paisa.com/website/scripmaster-csv-format.csv"

# # Fallbacks if primary is down
# SCRIP_MASTER_FALLBACK = "https://www.5paisa.com/docs/default-source/scrip-master/scripmaster-csv-format.csv"


# def _format_expiry(expiry_str: str) -> str:
#     """Convert expiry date to short format like '17MAR26'"""
#     if not expiry_str or expiry_str.strip() == "":
#         return ""
#     try:
#         for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S",
#                     "%d %b %Y", "%d-%m-%Y", "%Y%m%d"]:
#             try:
#                 dt = datetime.strptime(expiry_str.strip()[:10], fmt)
#                 return dt.strftime("%d%b%y").upper()
#             except ValueError:
#                 continue
#         return expiry_str.strip()[:9]
#     except Exception:
#         return ""


# def _is_expired(expiry_str: str) -> bool:
#     """Check if an instrument has expired"""
#     if not expiry_str or expiry_str.strip() == "":
#         return False  # Equity has no expiry, not expired
#     try:
#         for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S",
#                     "%d %b %Y", "%d-%m-%Y", "%Y%m%d"]:
#             try:
#                 dt = datetime.strptime(expiry_str.strip()[:10], fmt)
#                 return dt.date() < datetime.now().date()
#             except ValueError:
#                 continue
#     except Exception:
#         pass
#     return False


# class FivePaisaAdapter(BrokerInterface):
#     """5paisa API adapter using direct REST client"""
    
#     def __init__(self, account: Account, db: Optional[AsyncSession] = None):
#         self.account = account
#         self.db = db
#         self.cred = {
#             "APP_NAME": account.api_key,
#             "APP_SOURCE": account.app_source or "10074",
#             "USER_ID": account.trading_login_id,
#             "PASSWORD": account.encrypted_password,
#             "USER_KEY": account.user_key or account.api_key,
#             "ENCRYPTION_KEY": account.api_secret
#         }
#         self.client = FivePaisaRestClient(credentials=self.cred)
#         self.client.access_token = account.access_token
#         self.client.client_code = account.trading_login_id
    
#     async def get_margins(self) -> Dict:
#         return {
#             "equity": {"available": {"cash": 100000.0}},
#             "commodity": {"available": {"cash": 50000.0}}
#         }

#     async def get_positions(self) -> List[Dict]:
#         return []
    
#     async def _download_scrip_master(self) -> str:
#         """Download scrip master CSV — tries multiple URLs with the EXACT same
#         aiohttp pattern that was working in the original adapter."""
        
#         urls = [
#             SCRIP_MASTER_URL,       # API endpoint
#             SCRIP_MASTER_FALLBACK,  # Old static CSV
#         ]

#         for url in urls:
#             try:
#                 # Using the EXACT same pattern as the friend's original working code
#                 async with aiohttp.ClientSession() as session:
#                     async with session.get(url) as resp:
#                         if resp.status == 200:
#                             text = await resp.text()
#                             if text and len(text) > 100:
#                                 logger.info(f"✅ Scrip master downloaded: {len(text)} bytes from {url[:60]}")
#                                 return text
#                         logger.warning(f"URL returned status {resp.status}: {url[:60]}")
#             except Exception as e:
#                 logger.warning(f"Download failed ({type(e).__name__}: {repr(e)}): {url[:60]}")

#         logger.error("❌ All scrip master URLs failed!")
#         return ""

#     async def get_instruments(self, exchange: str) -> List[Dict]:
#         """
#         Fetch instruments from 5paisa scrip master CSV.
#         Column names matched to actual py5paisa SDK source.
#         """
#         try:
#             csv_text = await self._download_scrip_master()
#             if not csv_text:
#                 logger.error("❌ No scrip master data available")
#                 return []

#             reader = csv.DictReader(StringIO(csv_text.strip()))

#             # Log column names on first run (helps debug)
#             rows = list(reader)
#             if rows:
#                 logger.info(f"CSV columns: {list(rows[0].keys())[:15]}")
#             else:
#                 logger.error("❌ CSV parsed but no rows found")
#                 return []

#             instruments = []

#             for row in rows:

#                 exch = row.get("Exch")
#                 exch_type = row.get("ExchType")

#                 # Filter by exchange
#                 if exchange == "NSE" and not (exch == "N" and exch_type == "C"):
#                     continue
#                 if exchange == "BSE" and not (exch == "B" and exch_type == "C"):
#                     continue
#                 if exchange == "NFO" and not (exch == "N" and exch_type == "D"):
#                     continue

#                 # ── Confirmed CSV columns: Name, Expiry, CpType, StrikeRate, ScripCode ──
#                 # Name for equity = "RELIANCE"
#                 # Name for F&O = "NIFTY 25 Jun 2026 CE 23000.00" (full derivative string)
#                 name_col = row.get("Name") or ""
#                 scrip = row.get("Scripcode") or row.get("ScripCode") or ""

#                 if not name_col or not scrip:
#                     continue

#                 # For derivatives: build clean display name from individual columns
#                 if exch_type == "D":
#                     expiry = row.get("Expiry") or ""
                    
#                     # Skip expired instruments
#                     if _is_expired(expiry):
#                         continue

#                     strike = row.get("StrikeRate") or ""
#                     cp_type = row.get("CpType") or ""

#                     # Extract underlying from Name (first word is always the underlying)
#                     # "NIFTY 25 Jun 2026 CE 23000.00" → "NIFTY"
#                     underlying = name_col.split()[0] if name_col else ""

#                     expiry_short = _format_expiry(expiry)

#                     parts = [underlying]
#                     if expiry_short:
#                         parts.append(expiry_short)

#                     # Futures: CpType is empty or "XX"
#                     if not cp_type or cp_type == "XX":
#                         parts.append("FUT")
#                     else:
#                         # Options: add strike + CE/PE
#                         try:
#                             strike_val = float(strike) if strike else 0
#                             if strike_val > 0:
#                                 parts.append(str(int(strike_val)))
#                         except (ValueError, TypeError):
#                             pass
#                         parts.append(cp_type.upper())

#                     display_name = " ".join(parts)
#                     fullname = name_col  # Keep original for display (e.g. "NIFTY 25 Jun 2026 CE 23000.00")
#                 else:
#                     display_name = name_col
#                     fullname = name_col

#                 instruments.append({
#                     "Symbol": display_name,
#                     "Name": display_name,
#                     "FullName": fullname,
#                     "Exchange": exch,
#                     "ExchType": exch_type,
#                     "ScripCode": int(scrip),
#                     "Expiry": row.get("Expiry") or "",  # Pass through for sorting
#                 })

#             logger.info(f"✅ Loaded {len(instruments)} instruments for {exchange}")
#             return instruments

#         except Exception as e:
#             logger.error(f"❌ 5paisa instrument load failed: {e}", exc_info=True)
#             return []
    
#     async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
#         return 2500.50
    
#     def normalize_symbol(self, symbol: str, exchange: str) -> str:
#         return symbol.upper()
    
#     async def place_order(self, order_params: Dict) -> Dict:
#         """Place order with 5paisa — UNCHANGED from original"""
#         try:
#             scrip_code = order_params.get("scrip_code")
#             if not scrip_code:
#                 symbol = order_params.get("tradingsymbol") or order_params.get("symbol")
#                 exchange = order_params.get("exchange", "NSE")
#                 scrip_code = ScripMasterService.get_scrip_code(symbol, exchange)
                
#             if not scrip_code:
#                  return {
#                     "order_id": None,
#                     "status": "FAILED",
#                     "error": f"Could not resolve ScripCode for {order_params.get('tradingsymbol')}"
#                 }

#             side = order_params.get("transaction_type")
#             order_type = "B" if side == "BUY" else "S"
            
#             exchange = order_params.get("exchange", "NSE")
#             exch_type = "C"
#             if exchange == "MCX": exch_type = "D"
            
#             product = order_params.get("product", "INTRADAY")
#             is_intraday = (product == "INTRADAY")

#             logger.info(f"Placing 5paisa order via REST: {order_params.get('symbol')} ({scrip_code})")
            
#             result = await self.client.place_order(
#                 scrip_code=scrip_code,
#                 exchange=exchange[0],
#                 exchange_type=exch_type,
#                 order_type=order_type,
#                 quantity=int(order_params.get("quantity", 0)),
#                 price=float(order_params.get("price", 0)),
#                 is_intraday=is_intraday,
#                 at_market=(order_params.get("order_type") == "MARKET"),
#                 stop_loss_price=float(order_params.get("trigger_price", 0)),
#                 disclosed_qty=int(order_params.get("disclosed_qty", 0)),
#                 target_price=float(order_params.get("target", 0)),
#                 trailing_sl=float(order_params.get("trailing_stoploss", 0)),
#                 variety=order_params.get("variety", "regular"),
#                 is_amo=order_params.get("is_amo", False)
#             )
            
#             if result.get("success"):
#                 return {
#                     "order_id": result.get("order_id"),
#                     "status": "SUCCESS",
#                     "message": result.get("message")
#                 }
#             else:
#                 return {
#                     "order_id": None,
#                     "status": "FAILED",
#                     "error": result.get("error")
#                 }

#         except Exception as e:
#             logger.error(f"Error placing 5paisa order: {e}")
#             return {
#                 "order_id": None,
#                 "status": "FAILED",
#                 "error": str(e)
#             }
