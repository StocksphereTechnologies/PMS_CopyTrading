"""
5paisa Adapter — FIXED version for friend
FIXES:
  1. ScripCode resolution via on-demand instrument lookup (not broken ScripMasterService)
  2. NFO exchange type mapping for derivatives (was hardcoded to "C" cash only)
  3. Added get_orders with full mapping
"""
import datetime
import re
from datetime import datetime
from app.adapters.base import BrokerInterface
from app.models.account import Account
from app.services.fivepaisa_rest_client import FivePaisaRestClient
from app.core.config import settings
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import aiohttp
from io import StringIO
from app.core.http import HttpClient

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

# ── Module-level instrument cache (shared across all FivePaisaAdapter instances) ──
# Key: exchange (e.g. "NSE", "NFO"), Value: list of instrument dicts
_instruments_cache: Dict[str, List[Dict]] = {}


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

    def parse_5paisa_date(self, date_str):  
        if not date_str:
            return ""  
        try:
            match = re.search(r'(\d+)', str(date_str))
            if match:
                timestamp = int(match.group(1))
                dt = datetime.fromtimestamp(timestamp / 1000)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass   
        return str(date_str)
    
    def __init__(self, account: Account, db: Optional[AsyncSession] = None):
        self.account = account
        self.db = db
        self.cred = {
            "APP_NAME": account.api_key,
            "APP_SOURCE": account.app_source or "10074",
            "USER_ID": account.trading_login_id,
            "PASSWORD": account.encrypted_password, # Note: decrypted by account service
            "USER_KEY": account.user_key or account.api_key,
            "ENCRYPTION_KEY": account.api_secret
        }
        self.client = FivePaisaRestClient(credentials=self.cred)
        # Token is already managed by account service
        self.client.access_token = account.access_token
        self.client.client_code = account.trading_login_id
    
    
    async def get_margins(self) -> Dict:
        """Fetch margins for 5paisa (Mock)"""
        return {
            "equity": {"available": {"cash": 100000.0}},
            "commodity": {"available": {"cash": 50000.0}}
        }

    async def get_orders(self) -> List[Dict]:
        print("FIVEPAISA GET ORDERS RUNNING")
        try:
            token = str(self.account.access_token or "").strip().replace('"','').replace("'","")
            if not token:
                logger.error(f"No access token for 5paisa account {self.account.account_id}")
                return []

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
                "5Paisa-API-Uid": str(self.account.user_key)
            }

            payload = {
                "head": {
                    "key": self.account.user_key
                },
                "body": {
                    "ClientCode": self.account.trading_login_id
                }
            }

            url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V3/OrderBook"

            client = HttpClient.get_client()

            logger.info(f"5paisa calling OrderBook API for account {self.account.account_id}")
            
            response = await client.post(url, json=payload, headers=headers)

            if response.status_code != 200:
                logger.error(f"5paisa API error {response.status_code}: {response.text}")
                return []

            data = response.json()
            orders = data.get("body", {}).get("OrderBookDetail") or []
            logger.info(f"5paisa raw orders: {orders}")   
            mapped_orders = []
    
            for o in orders:

                side = o.get("BuySell")
                trade = "BUY" if side == "B" else "SELL" if side == "S" else ""

                status = o.get("OrderStatus") or ""
                if status == "Rejected By 5P":
                    status = "REJECTED"

                if "AMO" in status.upper():
                    variety = "amo"
                else:
                    variety = "regular"

                exch = (o.get("Exchange") or o.get("Exch") or "")
                if exch == "N":
                    exch = "NSE"
                elif exch == "B":
                    exch = "BSE"

                br_exch = o.get("Exchange") or o.get("Exch") or ""
                if br_exch == "N":
                    br_exch = "NSE"
                elif br_exch == "B":
                    br_exch = "BSE"

                is_intraday = o.get("IsIntraday")

                if str(is_intraday).lower() == "true":
                    product = "INTRADAY"
                else:
                    product = "DELIVERY"

                ex_id = str(o.get("ExOrderIDS") or o.get("ExchOrderID") or "")
                if ex_id == "0":
                    ex_id = ""

                broker_id = str(o.get("BrokerOrderId") or o.get("BrokerOrderID") or "")
                remote_id = str(o.get("RemoteOrderID") or "")

                order_id = ex_id if ex_id else (broker_id if broker_id else remote_id)

                raw_time = (
                    o.get("OrderDateTime")
                    or o.get("BrokerOrderTime")
                    or o.get("ExchOrderTime")
                    or o.get("OrderTime")
                    or ""
                )

                update_time = self.parse_5paisa_date(raw_time)

                price = o.get("Price") or o.get("Rate") or 0
                qty = o.get("Qty") or o.get("PendingQty") or 0

                mapped_orders.append({
                
                    "symbol": str(o.get("ScripName") or ""),
                    "trdAcc": self.account.trading_login_id,
                    "pseAcc": self.account.nickname,
                    "id": str(order_id),
                    "updateTime": update_time,
                    "status": status,
                    "qty": int(qty),
                    "price": float(price),
                    "variety": variety,         
                    "trade": trade,
                    "order": str(o.get("OrderType") or "LIMIT"),
                    "product": str(product or ""),
                    "exch": str(exch or ""),
                    "trigPrc": float(o.get("TriggerPrice") or 0),
                    "fillQty": int(o.get("QtyExecuted") or 0),
                    "pendQty": int(o.get("QtyRemaining") or 0),
                    "avgPrc": float(o.get("AvgRate") or 0),
                    "exchId": str(o.get("ExchOrderID") or ""),
                    "parentId": "",
                    "discQty": int(o.get("DisQty") or 0),
                    "amo": str(o.get("IsAMO")).lower() == "true",
                    "validity": "DAY",
                    "rejectReason": o.get("Reason") or "",
                    "brStatus": o.get("OrderStatus") or "",
                    "brExch": br_exch,
                    "brSymbol": o.get("ScripName") or "",
                    "day": "DAY",
                    "client": self.account.nickname,
                    "platform": "5paisa",
                    "broker": "FIVEPAISA",
                    "copyTrace": "",
                    "account_id": self.account.account_id
                })      
            logger.info(f"5paisa orders fetched: {len(mapped_orders)}")

            return mapped_orders

        except Exception as e:
            logger.error(f"5paisa order fetch error: {e}", exc_info=True)
        return []
    
    async def get_positions(self) -> List[Dict]:
        return []

    async def get_holdings(self) -> List[Dict]:
        """Fetch holdings from 5paisa"""
        try:
            token = str(self.account.access_token or "").strip()
    
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "5Paisa-API-Uid": str(self.account.user_key)
            }
    
            payload = {
                "head": {"key": self.account.user_key},
                "body": {"ClientCode": self.account.trading_login_id}
            }
    
            url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V3/Holding"
    
            client = HttpClient.get_client()
            response = await client.post(url, json=payload, headers=headers)
    
            if response.status_code != 200:
                return []
    
            data = response.json()
            raw = data.get("body", {}).get("Data", [])
    
            holdings = []
    
            for h in raw:
                print("RAW 5PAISA HOLDING:", h)

                # ✅ Correct fields from 5paisa
                symbol = h.get("Symbol") or ""
                
                # Exchange mapping
                exch = h.get("Exch")
                if exch == "N":
                    exchange = "NSE"
                elif exch == "B":
                    exchange = "BSE"
                else:
                    exchange = ""
                
                qty = int(h.get("Quantity", 0))
                pool = int(h.get("PoolQty", 0))

                t1 = pool
                total_qty = max(qty, pool)

                ltp = float(h.get("CurrentPrice") or 0)
                avg_price = float(h.get("AvgRate") or 0)

                current_value = total_qty * ltp
                invested_value = total_qty * avg_price
                pnl = current_value - invested_value
                
                holdings.append({
                    "pseAcc": self.account.nickname,
                    "trdAcc": self.account.trading_login_id,
                
                    "symbol": symbol,              # ✅ FIXED
                    "exchange": exchange,          # ✅ FIXED
                
                    "totqty": total_qty,
                    "ltp": ltp,                   # ✅ FIXED
                    "currval": current_value,
                    "quantity": qty,
                    "t1qty": t1,
                    "pnl": pnl,
                
                    "account_id": self.account.account_id,
                
                    "product": "DELIVERY",
                    "nsesymbol": symbol,
                    "bsesymbol": "",
                    "isin": "",
                    "insttoken": "",  # reserved for Zerodha only
                    "scripcode": str(h.get("NseCode") or h.get("ScripCode") or ""),
                
                    "collateralQty": 0,
                    "collateralType": "",
                    "haircut": 0,
                    "avgPrice": avg_price,
                
                    "day": "DAY",
                    "platform": "5paisa",
                    "broker": "FIVEPAISA"
                })
    
            return holdings
    
        except Exception as e:
            logger.error(f"5paisa holdings error: {e}")
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
                    if not cp_type or cp_type == "XX":
                        name_upper = name_col.upper()
                        if " CE " in name_upper:
                            cp_type = "CE"
                        elif " PE " in name_upper:
                            cp_type = "PE"

                    if not strike or strike == "0":
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
                    fullname = name_col
                else:
                    display_name = name_col
                    fullname = name_col

                lot_size = row.get("LotSize") or row.get("Lotsize") or 1

                instruments.append({
                    "Symbol": display_name,
                    "Name": display_name,
                    "FullName": fullname,
                    "Exchange": exch,
                    "ExchType": exch_type,
                    "ScripCode": int(scrip),
                    "Expiry": row.get("Expiry") or "",
                    "LotSize": int(lot_size)
                })

            logger.info(f"✅ Loaded {len(instruments)} instruments for {exchange}")
            _instruments_cache[exchange] = instruments
            return instruments

        except Exception as e:
            logger.error(f"❌ 5paisa instrument load failed: {e}", exc_info=True)
            return []
    
    async def _resolve_scrip_code(self, symbol: str, exchange: str) -> Optional[int]:
        """
        Resolve ScripCode for a symbol by searching the instruments list.
        Uses module-level cache AND the local JSON cache file for persistence.
        """
        global _instruments_cache
        
        # 1. Check module-level memory cache
        if exchange in _instruments_cache:
            instruments = _instruments_cache[exchange]
        else:
            # 2. Try to load from the MarketWatch JSON cache file (persistence)
            instruments = []
            try:
                import json
                import os
                cache_file = "instruments_cache_5paisa.json"
                if os.path.exists(cache_file):
                    with open(cache_file, "r") as f:
                        data = json.load(f)
                    key = f"FIVEPAISA_{exchange}"
                    if key in data:
                        instruments = data[key].get("instruments") or []
                        if instruments:
                            logger.info(f"📁 Loaded {len(instruments)} instruments from disk cache for {exchange}")
                            _instruments_cache[exchange] = instruments
            except Exception as e:
                logger.warning(f"Disk cache load failed: {e}")

            
            if not instruments:
                logger.error(f"❌ Instruments not preloaded for {exchange}")
                return None
        
        symbol_upper = symbol.strip().upper()
        
        # Pass 1: Exact match (case-sensitive)
        for inst in instruments:
            if inst.get("Symbol") == symbol or inst.get("Name") == symbol or inst.get("FullName") == symbol:
                logger.info(f"✅ Resolved ScripCode: {symbol} → {inst['ScripCode']} (exact match)")
                return inst["ScripCode"]
        
        # Pass 2: Case-insensitive match
        for inst in instruments:
            sym = (inst.get("Symbol") or "").upper()
            name = (inst.get("Name") or "").upper()
            fullname = (inst.get("FullName") or "").upper()
            if symbol_upper in (sym, name, fullname):
                logger.info(f"✅ Resolved ScripCode: {symbol} → {inst['ScripCode']} (case-insensitive)")
                return inst["ScripCode"]
        
        logger.warning(f"❌ Could not resolve ScripCode for '{symbol}' on {exchange} "
                       f"(searched {len(instruments)} instruments)")
        return None

    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP from 5paisa (Mock)"""
        return None
    
    def normalize_symbol(self, symbol: str, exchange: str) -> str:
        """Normalize symbol for 5paisa"""
        return symbol.upper()

    async def get_lot_size(self, symbol: str, exchange: str) -> int:
        try:
            instruments = await self.get_instruments(exchange)

            for inst in instruments:
                if symbol.strip().upper() == (inst.get("Symbol") or "").upper():
                    return int(inst.get("LotSize", 1))

            return 1
        except Exception as e:
            logger.error(f"Lot size fetch error: {e}")
            return 1
    
    async def place_order(self, order_params: Dict) -> Dict:
        """Place order with 5paisa using FivePaisaRestClient"""
        try:
            # ── Step 1: Resolve ScripCode ──
            scrip_code = order_params.get("scrip_code")
            symbol = order_params.get("tradingsymbol") or order_params.get("symbol")
            exchange = order_params.get("exchange", "NSE")
            
            # 🚀 ADD THIS BLOCK
            if not hasattr(self, "_scrip_cache"):
                self._scrip_cache = {}

            cache_key = f"{exchange}_{symbol}"

            if not scrip_code:
                if cache_key in self._scrip_cache:
                    scrip_code = self._scrip_cache[cache_key]
                else:
                    scrip_code = await self._resolve_scrip_code(symbol, exchange)
                    if scrip_code:
                        self._scrip_cache[cache_key] = scrip_code
                
            if not scrip_code:
                 return {
                    "order_id": None,
                    "status": "FAILED",
                    "error": f"Could not resolve ScripCode for {symbol} on {exchange}"
                }

            # ── Step 2: Map order parameters ──
            side = order_params.get("transaction_type") or order_params.get("side")
            if side == "BUY":
                order_type = "B"
            elif side == "SELL":
                order_type = "S"
            else:
                return {
                    "order_id": None,
                    "status": "FAILED",
                    "error": f"Invalid side: {side}"
                }
            
            # FIX: Map exchange to correct ExchType
            # "C" = Cash (equity), "D" = Derivatives (F&O)
            exch_type = "C"  # Default: Cash/Equity
            if exchange in ("NFO", "MCX"):
                exch_type = "D"  # Derivatives
            
            product = order_params.get("product", "INTRADAY")
            is_intraday = (product == "INTRADAY")

            logger.info(f"Placing 5paisa order: {symbol} (ScripCode={scrip_code}, Exch={exchange}, ExchType={exch_type})")
            
            qty = int(order_params.get("quantity", 1))
            if exchange == "NFO":
                lot_size = 1
                instruments = _instruments_cache.get(exchange, [])
                
                for inst in instruments:
                    if symbol.upper() == (inst.get("Symbol") or "").upper():
                        lot_size = int(inst.get("LotSize", 1))
                        break
                    
                qty = qty * lot_size
            
            logger.info(f"FINAL QTY: {symbol} → {qty}")

            result = await self.client.place_order(
                scrip_code=scrip_code,
                exchange=exchange[0], # N or B
                exchange_type=exch_type,
                order_type=order_type,
                quantity=qty,
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