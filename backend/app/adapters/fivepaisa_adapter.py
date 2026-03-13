import datetime
import re
from datetime import datetime
from app.adapters.base import BrokerInterface
from app.models.account import Account
from app.services.fivepaisa_rest_client import FivePaisaRestClient
from app.services.scrip_master_service import ScripMasterService
from app.core.config import settings
import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


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

            from app.core.http import HttpClient
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
        """Fetch positions for 5paisa (Mock)"""
        return []
    
    async def get_instruments(self, exchange: Optional[str] = None) -> List[Dict]:
        """Fetch instruments from 5paisa (Mock)"""
        return []
    
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP from 5paisa (Mock)"""
        return 2500.50
    
    def normalize_symbol(self, symbol: str, exchange: str) -> str:
        """Normalize symbol for 5paisa"""
        return symbol.upper()
    
    async def place_order(self, order_params: Dict) -> Dict:
        """Place order with 5paisa using FivePaisaRestClient"""
        try:
            # Resolve ScripCode using ScripMasterService
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

            # Map Transaction Type
            side = order_params.get("transaction_type")
            order_type = "B" if side == "BUY" else "S"
            
            # Map Exchange Segment
            exchange = order_params.get("exchange", "NSE")
            exch_type = "C" # Cash
            if exchange == "MCX": exch_type = "D" # Derivatives
            
            # Is Intraday
            product = order_params.get("product", "INTRADAY")
            is_intraday = (product == "INTRADAY")

            logger.info(f"Placing 5paisa order via REST: {order_params.get('symbol')} ({scrip_code})")
            
            result = await self.client.place_order(
                scrip_code=scrip_code,
                exchange=exchange[0], # N or B
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
