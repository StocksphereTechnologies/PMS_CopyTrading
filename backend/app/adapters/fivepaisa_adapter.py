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
