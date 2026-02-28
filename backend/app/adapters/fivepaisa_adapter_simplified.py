"""
5paisa adapter - PURE py5paisa implementation (NO REST CLIENT)
"""
import asyncio
from typing import Dict, List, Any, Optional
from py5paisa import FivePaisaClient
from app.adapters.broker_interface import BrokerInterface
from app.models.account import Account
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class FivePaisaAdapter(BrokerInterface):
    """Adapter for 5paisa API using ONLY py5paisa library"""
    
    def __init__(self, account: Account, db: Optional[AsyncSession] = None):
        self.account = account
        self.db = db
        self.client: Optional[FivePaisaClient] = None
        self._instruments_cache: Optional[List[Dict[str, Any]]] = None
        self._authenticated = False
    
    async def _ensure_authenticated(self) -> bool:
        """
        Authenticate using py5paisa library ONLY
        NO REST CLIENT, NO MANUAL TOKEN FLOW
        """
        
        if self._authenticated and self.client:
            logger.info(" Already authenticated")
            return True
        
        try:
            from app.core.encryption import encryption_service
            import pyotp
            
            mpin = encryption_service.decrypt(self.account.encrypted_password)
            totp_secret = encryption_service.decrypt(self.account.encrypted_totp_secret)
            
            totp = pyotp.TOTP(totp_secret)
            totp_value = totp.now()
            
            cred = {
                "APP_NAME": self.account.api_key or "",
                "APP_SOURCE": self.account.app_source or "10074",
                "USER_ID": self.account.trading_login_id,
                "PASSWORD": mpin,
                "USER_KEY": self.account.user_key or "",
                "ENCRYPTION_KEY": self.account.api_secret or ""
            }
            
            logger.info(f" Initializing 5paisa client for user: {self.account.trading_login_id}")
            
            loop = asyncio.get_event_loop()
            self.client = await loop.run_in_executor(
                None,
                lambda: FivePaisaClient(cred=cred)
            )
            
            logger.info(" Logging in with TOTP...")
            
            #this is the ONLY method we use
            login_result = await loop.run_in_executor(
                None,
                lambda: self.client.get_totp_session(
                    client_code=self.account.trading_login_id,
                    totp=totp_value,
                    pin=mpin
                )
            )
            
            logger.info(f" Login result: {login_result}")
            
            # Check if login was successful
            
            if hasattr(self.client, 'access_token') and self.client.access_token:
                logger.info(f" Authentication successful!")
                logger.info(f"Token: {self.client.access_token[:30]}...")
                
                
                self.account.access_token = self.client.access_token
                if hasattr(self.client, 'Jwt_token') and self.client.Jwt_token:
                    self.account.access_token = self.client.Jwt_token
                
                if self.db:
                    try:
                        from datetime import datetime
                        self.account.token_generated_at = datetime.now()
                        self.db.add(self.account)
                        await self.db.commit()
                        logger.info(" Token saved to database")
                    except Exception as e:
                        logger.warning(f"Failed to save token: {e}")
                
                self._authenticated = True
                return True
            else:
                logger.error(" Login failed - no access token received")
                logger.error(f"Client attributes: {[a for a in dir(self.client) if not a.startswith('_')]}")
                return False
                
        except Exception as e:
            logger.error(f" Authentication error: {e}", exc_info=True)
            self._authenticated = False
            return False
    
    async def place_order(self, order_request: Dict[str, Any]) -> Dict[str, Any]:
        """Place order using py5paisa client"""
        
        logger.info(f" 5paisa place_order for {order_request.get('symbol')}")
        
        if not await self._ensure_authenticated():
            logger.error(" Authentication failed")
            return {
                "order_id": None,
                "status": "FAILED",
                "broker": "FIVEPAISA",
                "error": "Authentication failed"
            }
        
        if not hasattr(self.client, 'access_token') or not self.client.access_token:
            logger.error(" Client has no access token")
            return {
                "order_id": None,
                "status": "FAILED",
                "broker": "FIVEPAISA",
                "error": "No access token in client"
            }
        
        logger.info(f" Client authenticated with token: {self.client.access_token[:20]}...")
        
        try:
            scrip_code = order_request.get("scrip_code")
            if not scrip_code:
                scrip_code = await self._get_scrip_code(
                    order_request["symbol"],
                    order_request["exchange"]
                )
            
            if not scrip_code:
                logger.error(f" Scrip code not found for {order_request['symbol']}")
                return {
                    "order_id": None,
                    "status": "FAILED",
                    "broker": "FIVEPAISA",
                    "error": f"Scrip code not found for {order_request['symbol']}"
                }
            
            logger.info(f" Scrip code: {scrip_code}")
            
            exchange_map = {"NSE": "N", "BSE": "B"}
            exchange_code = exchange_map.get(order_request["exchange"], order_request["exchange"])
            
            is_intraday = False
            if "product" in order_request:
                is_intraday = order_request["product"] in ["MIS", "INTRADAY"]
            elif "is_intraday" in order_request:
                is_intraday = order_request["is_intraday"]
            
            order_params = {
                "OrderType": "B" if order_request["transaction_type"] == "BUY" else "S",
                "Exchange": exchange_code,
                "ExchangeType": order_request.get("exchange_type", "C"),
                "ScripCode": int(scrip_code),
                "Qty": int(order_request["quantity"]),
                "IsIntraday": is_intraday,
                "RemoteOrderID": "1",
                "iOrderValidity": 0,
                "PublicIP": "0.0.0.0",
                "AHPlaced": "N",
                "IOCOrder": False,
                "StopLossPrice": 0,
                "IsStopLossOrder": False,
                "DisQty": 0
            }
            
            if order_request["order_type"] == "MARKET":
                order_params["Price"] = 0
                order_params["AtMarket"] = True
            elif order_request["order_type"] == "LIMIT":
                if "price" not in order_request or not order_request["price"]:
                    raise ValueError("Price required for LIMIT orders")
                order_params["Price"] = float(order_request["price"])
                order_params["AtMarket"] = False
            else:
                order_params["IsStopLossOrder"] = True
                order_params["AtMarket"] = False
                if "price" in order_request and order_request["price"]:
                    order_params["Price"] = float(order_request["price"])
                else:
                    order_params["Price"] = 0
                if "trigger_price" in order_request and order_request["trigger_price"]:
                    order_params["StopLossPrice"] = float(order_request["trigger_price"])
            
            if "disclosed_quantity" in order_request and order_request["disclosed_quantity"]:
                order_params["DisQty"] = int(order_request["disclosed_quantity"])
            
            logger.info(f" Order params: {order_params}")
            
            loop = asyncio.get_event_loop()
            
            logger.info(" Calling client.place_order()...")
            response = await loop.run_in_executor(
                None,
                lambda: self.client.place_order(**order_params)
            )
            
            logger.info(f" Response: {response}")
            logger.info(f" Response type: {type(response)}")
            
            if response is None:
                logger.error(" Got None response - client not authenticated properly")
                logger.error(" This means the access token is not working")
                logger.error(" Trying to re-authenticate...")
                
                self._authenticated = False
                self.client = None
                
                if await self._ensure_authenticated():
                    logger.info(" Re-authenticated, retrying order...")
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.client.place_order(**order_params)
                    )
                    logger.info(f" Retry response: {response}")
                else:
                    return {
                        "order_id": None,
                        "status": "FAILED",
                        "broker": "FIVEPAISA",
                        "error": "Re-authentication failed"
                    }
            
            if response and isinstance(response, dict):
                if "BrokerOrderID" in response and response["BrokerOrderID"]:
                    order_id = str(response["BrokerOrderID"])
                    logger.info(f" Order placed! ID: {order_id}")
                    return {
                        "order_id": order_id,
                        "status": "SUCCESS",
                        "broker": "FIVEPAISA"
                    }
                elif "OrderId" in response and response["OrderId"]:
                    order_id = str(response["OrderId"])
                    logger.info(f" Order placed! ID: {order_id}")
                    return {
                        "order_id": order_id,
                        "status": "SUCCESS",
                        "broker": "FIVEPAISA"
                    }
                elif response.get("Status") == 0:
                    order_id = response.get("BrokerOrderID", "SUCCESS")
                    logger.info(f" Order placed (Status=0)! ID: {order_id}")
                    return {
                        "order_id": str(order_id),
                        "status": "SUCCESS",
                        "broker": "FIVEPAISA"
                    }
                elif "Message" in response:
                    error_msg = response.get("Message")
                    logger.error(f" Order failed: {error_msg}")
                    return {
                        "order_id": None,
                        "status": "FAILED",
                        "broker": "FIVEPAISA",
                        "error": error_msg
                    }
                else:
                    logger.warning(f" Unexpected response: {response}")
                    return {
                        "order_id": None,
                        "status": "FAILED",
                        "broker": "FIVEPAISA",
                        "error": f"Unexpected response: {response}"
                    }
            
            return {
                "order_id": None,
                "status": "FAILED",
                "broker": "FIVEPAISA",
                "error": f"Invalid response: {response}"
            }
            
        except Exception as e:
            logger.error(f" Order placement error: {e}", exc_info=True)
            return {
                "order_id": None,
                "status": "FAILED",
                "broker": "FIVEPAISA",
                "error": str(e)
            }
    
    async def _get_scrip_code(self, symbol: str, exchange: str) -> Optional[int]:
        """Get scrip code for symbol"""
        try:
            instruments = self._instruments_cache or await self.get_instruments(exchange)
            
            exchange_map = {"NSE": "N", "BSE": "B"}
            exchange_code = exchange_map.get(exchange, exchange)
            
            for instrument in instruments:
                if (instrument.get("Symbol") == symbol and 
                    instrument.get("Exchange") == exchange_code):
                    return instrument.get("ScripCode")
            
            
            common_scrips = {
                # its for bse not nse need to look for nse scrip codes as well 
                "RELIANCE": 500325,
                "INFY": 408065,
                "TCS": 532540,
                "HDFCBANK": 500180,
                "ICICIBANK": 532174,
                "SBIN": 500112
            }
            
            if symbol in common_scrips:
                logger.warning(f"Using hardcoded scrip: {symbol} -> {common_scrips[symbol]}")
                return common_scrips[symbol]
            
            return None
        except Exception as e:
            logger.error(f"Error getting scrip code: {e}")
            return None
    
    async def get_instruments(self, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch instruments"""
        if self._instruments_cache:
            return self._instruments_cache
        
        if not await self._ensure_authenticated():
            return self._get_mock_instruments()
        
        try:
            loop = asyncio.get_event_loop()
            
            if hasattr(self.client, 'get_scrips'):
                instruments = await loop.run_in_executor(None, self.client.get_scrips)
            elif hasattr(self.client, 'fetch_master'):
                instruments = await loop.run_in_executor(None, self.client.fetch_master)
            else:
                return self._get_mock_instruments()
            
            if instruments is not None:
                try:
                    import pandas as pd
                    if isinstance(instruments, pd.DataFrame) and not instruments.empty:
                        instruments = instruments.to_dict('records')
                        logger.info(f" Fetched {len(instruments)} instruments")
                        self._instruments_cache = instruments
                        return instruments
                except ImportError:
                    pass
            
            return self._get_mock_instruments()
            
        except Exception as e:
            logger.error(f"Error fetching instruments: {e}")
            return self._get_mock_instruments()
    
    def _get_mock_instruments(self) -> List[Dict[str, Any]]:
        """Mock instruments"""
        return [
            {"ScripCode": 500325, "Name": "RELIANCE", "Exchange": "N", "ExchangeType": "C", "Symbol": "RELIANCE"},
            {"ScripCode": 408065, "Name": "INFY", "Exchange": "N", "ExchangeType": "C", "Symbol": "INFY"}
        ]
    
    async def get_ltp(self, symbol: str, exchange: str) -> Optional[float]:
        """Get LTP"""
        if not await self._ensure_authenticated():
            return None
        
        try:
            scrip_code = await self._get_scrip_code(symbol, exchange)
            if not scrip_code:
                return None
            
            loop = asyncio.get_event_loop()
            market_data = await loop.run_in_executor(
                None,
                lambda: self.client.fetch_market_feed_scrip([{
                    "Exch": "N" if exchange == "NSE" else "B",
                    "ExchType": "C",
                    "ScripCode": scrip_code
                }])
            )
            
            if market_data and len(market_data) > 0:
                return market_data[0].get("LastRate")
            return None
        except Exception as e:
            logger.error(f"Error fetching LTP: {e}")
            return None
    
    async def normalize_symbol(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """Normalize symbol"""
        try:
            if not self._instruments_cache:
                await self.get_instruments(exchange)
            
            exchange_map = {"NSE": "N", "BSE": "B"}
            exchange_code = exchange_map.get(exchange, exchange)
            
            for instrument in self._instruments_cache or []:
                if (instrument.get("Symbol") == symbol and 
                    instrument.get("Exchange") == exchange_code):
                    return {
                        "symbol": instrument["Symbol"],
                        "exchange": exchange,
                        "scrip_code": instrument["ScripCode"],
                        "name": instrument.get("Name"),
                        "broker": "FIVEPAISA"
                    }
            
            common_scrips = {
                "RELIANCE": 500325,
                "INFY": 408065,
                "TCS": 532540,
                "HDFCBANK": 500180
            }
            
            scrip_code = common_scrips.get(symbol)
            if scrip_code:
                return {
                    "symbol": symbol,
                    "exchange": exchange,
                    "scrip_code": scrip_code,
                    "broker": "FIVEPAISA"
                }
            
            return {
                "symbol": symbol,
                "exchange": exchange,
                "broker": "FIVEPAISA"
            }
        except Exception as e:
            logger.error(f"Error normalizing: {e}")
            return {
                "symbol": symbol,
                "exchange": exchange,
                "broker": "FIVEPAISA"
            }