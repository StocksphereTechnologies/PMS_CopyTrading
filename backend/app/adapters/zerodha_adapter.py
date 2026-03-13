"""Zerodha Kite Connect adapter"""
from typing import List, Dict, Optional, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from app.adapters.base import BrokerInterface
from app.models.account import Account
from app.schemas.position import Position
from app.config import settings
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class ZerodhaAdapter(BrokerInterface):
    """Zerodha Kite Connect API adapter"""
    
    def parse_zerodha_time(self, ts):
        if not ts:
            return ""

        try:
            if isinstance(ts, str):
                return ts
            return ts.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(ts)
    
    def __init__(self, account: Account, db: Optional[AsyncSession] = None):
        self.account = account
        self.db = db
        self.api_key = account.api_key
        self.api_secret = account.api_secret

        # Clean token 
        token = account.access_token
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        if token:
            self.access_token = token.strip().replace("'", "").replace('"', "")
            if self.access_token.startswith("b") and len(self.access_token) > 2:
                 self.access_token = self.access_token[1:]
        else:
            self.access_token = None
            
        self.base_url = settings.ZERODHA_API_BASE_URL
        self.api_url = self.base_url  # usually https://api.kite.trade
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to Kite API"""
        url = f"{self.api_url}{endpoint}"
        headers = {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}"
        }
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                # Kite API expects form-encoded data, not JSON
                response = await client.post(url, headers=headers, data=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", str(e))
                    logger.error(f"Zerodha API Error ({response.status_code}): {error_msg}")
                    # Return error as success=false format for the adapter to handle
                    return {"status": "error", "message": error_msg}
                except:
                    logger.error(f"Zerodha API Error ({response.status_code}): {str(e)}")
                    raise e
            
    # not working as of now facing issues with the websocket connection
    async def get_instruments(self, exchange: Optional[str] = None) -> List[Dict]:
        """Fetch instruments from Zerodha (Kite API returns CSV for instruments)"""
        try:
            endpoint = "/instruments"
            if exchange:
                endpoint = f"/instruments/{exchange}"
            
            # Kite Connect /instruments endpoint returns a large CSV file.
            # For simplicity in this implementation, we might prefer a mock or 
            # a cached version. However, for "perfection", we should fetch it.
            # NOTE: Fetching the full CSV daily is recommended.
            
            headers = {"X-Kite-Version": "3", "Authorization": f"token {self.api_key}:{self.access_token}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_url}{endpoint}", headers=headers)
                response.raise_for_status()
                
                # CSV parsing: Zerodha instruments are CSV
                import csv
                import io
                content = response.text
                f = io.StringIO(content)
                reader = csv.DictReader(f)
                return list(reader)
                
        except Exception as e:
            logger.error(f"Error fetching instruments from Zerodha: {e}")
            return []
    
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP from Zerodha via direct API call"""
        try:
            params = {"i": f"{exchange}:{symbol}"}
            data = await self._make_request("GET", "/quote/ltp", params=params)
            
            if "data" in data and f"{exchange}:{symbol}" in data["data"]:
                return float(data["data"][f"{exchange}:{symbol}"]["last_price"])
            return None
        except Exception as e:
            logger.error(f"Error fetching LTP from Zerodha for {exchange}:{symbol}: {e}")
            return None
    
    async def get_margins(self) -> Dict:
        """Fetch margin data from Zerodha and transform to unified format"""
        try:
            print(f"DEBUG: [Zerodha] Fetching real-time margins for account {self.account.account_id} ({self.account.trading_login_id})...", flush=True)
            data = await self._make_request("GET", "/user/margins")
            raw_margins = data.get("data", {})
            transformed = self._transform_margins(raw_margins)
            print(f"DEBUG: [Zerodha] Margins fetched successfully for account {self.account.account_id}.", flush=True)
            return transformed
        except Exception as e:
            logger.error(f"Error fetching margins from Zerodha: {e}")
            return {}

    async def get_positions(self) -> List[Position]:
        """Fetch positions from Zerodha and transform to unified Position schema"""
        try:
            print(f"DEBUG: [Zerodha] Fetching real-time positions for account {self.account.account_id} ({self.account.trading_login_id})...", flush=True)
            data = await self._make_request("GET", "/portfolio/positions")
            net_positions = data.get("data", {}).get("net", [])
            print(f"DEBUG: [Zerodha] Positions fetched successfully ({len(net_positions)} found) for account {self.account.account_id}.", flush=True)
            return [self._map_position(pos) for pos in net_positions]
        except Exception as e:
            logger.error(f"Error fetching positions from Zerodha: {e}")
            return []
        
    async def get_orders(self) -> List[Dict]:
        """Fetch orders from Zerodha and transform to unified order format"""
        try:
            print(f"DEBUG: [Zerodha] Fetching real-time orders for account {self.account.account_id} ({self.account.trading_login_id})...", flush=True)
            data = await self._make_request("GET", "/orders")
            raw_orders = data.get("data", [])
            print(f"DEBUG: [Zerodha] Orders fetched successfully ({len(raw_orders)} found) for account {self.account.account_id}.", flush=True)
            return [self._map_order(o) for o in raw_orders]
        except Exception as e:
            logger.error(f"Error fetching orders from Zerodha: {e}")
            return []
       
    def _transform_margins(self, raw_margins: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Zerodha margin response to unified format"""
        from datetime import datetime, timezone
        equity = raw_margins.get("equity", {})
        commodity = raw_margins.get("commodity", {})
        
        return {
            "account_id": self.account.account_id,
            "broker_name": self.account.broker_name,
            "nickname": self.account.nickname,
            "trading_login_id": self.account.trading_login_id,
            "equity": {
                "enabled": equity.get("enabled", True),
                "net": float(equity.get("net", 0.0)),
                "available": {
                    "cash": float(equity.get("available", {}).get("cash", 0.0)),
                    "opening_balance": float(equity.get("available", {}).get("opening_balance", 0.0)),
                    "live_balance": float(equity.get("available", {}).get("live_balance", 0.0)),
                },
                "utilised": {
                    "debits": float(equity.get("utilised", {}).get("debits", 0.0)),
                    "exposure": float(equity.get("utilised", {}).get("exposure", 0.0)),
                    "m2m_realised": float(equity.get("utilised", {}).get("m2m_realised", 0.0)),
                    "m2m_unrealised": float(equity.get("utilised", {}).get("m2m_unrealised", 0.0)),
                }
            },
            "commodity": {
                "enabled": commodity.get("enabled", True),
                "net": float(commodity.get("net", 0.0)),
                "available": {
                    "cash": float(commodity.get("available", {}).get("cash", 0.0)),
                }
            } if commodity else None,
            "last_updated": datetime.now(timezone.utc)
        }

    def _map_position(self, p: Dict[str, Any]) -> Position:
        """Map Zerodha raw position to unified Position schema"""
        from datetime import datetime, timezone
        net_qty = int(p.get("quantity", 0))
        
        # Calculate direction
        direction = "NEUTRAL"
        if net_qty > 0:
            direction = "LONG"
        elif net_qty < 0:
            direction = "SHORT"

        return Position(
            id=str(p.get("instrument_token", "")),
            symbol=p.get("tradingsymbol", ""),
            m2m=float(p.get("m2m", 0.0)),
            pnl=float(p.get("pnl", 0.0)),
            atpnl=float(p.get("pnl", 0.0)),
            realpl=float(p.get("realised", 0.0)),
            unrealpl=float(p.get("unrealised", 0.0)),
            netqty=net_qty,
            ltp=float(p.get("last_price", 0.0)),
            buyqty=int(p.get("buy_quantity", 0)),
            sellqty=int(p.get("sell_quantity", 0)),
            buyval=float(p.get("buy_value", 0.0)),
            sellval=float(p.get("sell_value", 0.0)),
            netval=float(p.get("buy_value", 0.0)) - float(p.get("sell_value", 0.0)),
            bavg=float(p.get("buy_price", 0.0)),
            savg=float(p.get("sell_price", 0.0)),
            state=p.get("product", ""), # NRML, MIS etc
            direction=direction,
            type=p.get("product", ""),
            category=p.get("exchange", ""),
            broker="Zerodha",
            overqty=int(p.get("overnight_quantity", 0)),
            multiplier=float(p.get("multiplier", 1.0)),
            exch=p.get("exchange", ""),
            brexch=p.get("exchange", ""),
            brsymbol=p.get("tradingsymbol", ""),
            day="NET",
            platform="Kite",
            accid=self.account.trading_login_id,
            account_id=self.account.account_id,
            last_updated=datetime.now(timezone.utc)
        )
    
    def _map_order(self, order: Dict) -> Dict:
        """Map Zerodha raw order to unified order schema"""
        ts = order.get("order_timestamp")
        update_time = self.parse_zerodha_time(ts)

        product = order.get("product")
        if product == "MIS":
            product = "INTRADAY"
        elif product == "CNC":
            product = "DELIVERY"
        elif product == "NRML":
            product = "NORMAL"
        else:
            product = product or ""
        
        return {
            "symbol": str(order.get("tradingsymbol") or ""),
            "trdAcc": self.account.trading_login_id,
            "pseAcc": self.account.nickname,
    
            "id": str(order.get("order_id") or ""),
            "updateTime": str(update_time or ""),
    
            "status": order.get("status") or "",
    
            "qty": int(order.get("quantity") or 0),
            "price": float(order.get("price") or 0),
    
            "variety": order.get("variety") or "",
            "trade": str(order.get("transaction_type") or ""),
            "order": str(order.get("order_type") or ""),
            "product": product,    
            "exch": str(order.get("exchange") or ""),
            "trigPrc": float(order.get("trigger_price") or 0),
    
            "fillQty": int(order.get("filled_quantity") or 0),
            "pendQty": int(order.get("pending_quantity") or 0),
    
            "pubId": "",
            "avgPrc": float(order.get("average_price") or 0),
    
            "exchId": str(order.get("exchange_order_id") or ""),
            "parentId": str(order.get("parent_order_id") or ""),
    
            "discQty": int(order.get("disclosed_quantity") or 0),
    
            "amo": order.get("variety", "").lower() == "amo",
    
            "validity": order.get("validity") or "DAY",
            "rejectReason": order.get("status_message") or "",
    
            "brStatus": order.get("status") or "",
            "brExch": str(order.get("exchange") or ""),
            "brSymbol": order.get("tradingsymbol") or "",
    
            "day": "DAY",
            "client": self.account.nickname,
            "platform": "Kite",
            "broker": "ZERODHA",
    
            "copyTrace": "",
            "account_id": self.account.account_id
    }   
    def normalize_symbol(self, symbol: str, exchange: str) -> str:
        """Normalize symbol for Zerodha (usually uppercase)"""
        return symbol.upper()
    
    async def place_order(self, order_params: Dict) -> Dict:
        """Place order with Zerodha using Kite API"""
        try:
            product = order_params.get('product')
            if product == "INTRADAY": product = "MIS"
            elif product == "DELIVERY": product = "CNC"
            elif product == "NORMAL": product = "NRML"
            
            # Map order_type (MARKET, LIMIT, SL, SL-M)
            order_type = order_params.get("order_type")
            if order_type == "SL_MARKET": order_type = "SL-M"
            
            # Prepare data for Kite API
            data = {
                "exchange": order_params.get("exchange"),
                "tradingsymbol": order_params.get("tradingsymbol"),
                "transaction_type": order_params.get("transaction_type"),
                "quantity": int(order_params.get("quantity", 0)),
                "order_type": order_type,
                "product": product,
                "validity": order_params.get("validity", "DAY"),
                "price": float(order_params.get("price", 0)),
                "trigger_price": float(order_params.get("trigger_price", 0)),
                "disclosed_quantity": int(order_params.get("disclosed_quantity", 0)),
                "tag": order_params.get("tag")
            }
            
            # Map Variety (regular, bo, co, amo)
            variety = order_params.get("variety", "regular").lower()
            if order_params.get("is_amo"):
                variety = "amo"
            
            # Add BO/CO specific fields
            if variety == "bo" or variety == "co":
                data.update({
                    "squareoff": float(order_params.get("target", 0)),
                    "stoploss": float(order_params.get("stoploss", 0)),
                    "trailing_stoploss": float(order_params.get("trailing_stoploss", 0))
                })

            logger.info(f"Placing Zerodha {variety} order: {order_params.get('tradingsymbol')} x {order_params.get('quantity')}")
            result = await self._make_request("POST", f"/orders/{variety}", data=data)
            
            if result.get("status") == "success":
                return {
                    "order_id": result["data"]["order_id"],
                    "status": "SUCCESS",
                    "message": "Order placed successfully"
                }
            else:
                return {
                    "order_id": None,
                    "status": "FAILED",
                    "error": result.get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error placing Zerodha order: {e}")
            return {
                "order_id": None,
                "status": "FAILED",
                "error": str(e)
            }
