"""
5paisa Direct REST API Client
Secure implementation for order placement bypassing py5paisa library
"""
import httpx
import asyncio
from typing import Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FivePaisaRestClient:
    """
    Direct REST API client for 5paisa order placement
    Uses secure HTTPS with proper authentication
    """
    
    BASE_URL = "https://openapi.5paisa.com/VendorsAPI/Service1.svc"
    
    def __init__(self, credentials: Dict[str, str]):
        """
        Initialize REST client with credentials
        
        Args:
            credentials: Dict with APP_NAME, APP_SOURCE, USER_ID, PASSWORD, USER_KEY, ENCRYPTION_KEY
        """
        self.credentials = credentials
        self.access_token: Optional[str] = None
        self.client_code: Optional[str] = None
        
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            verify=True,
            follow_redirects=False,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def login_with_totp(self, totp: str, pin: str) -> Dict[str, Any]:
        """
        Login using TOTP authentication
        
        Args:
            totp: Time-based OTP from authenticator
            pin: Trading PIN/MPIN
            
        Returns:
            Dict with success status and access_token
        """
        try:
            url = f"{self.BASE_URL}/TOTPLogin"
            
            payload = {
                "head": {
                    "appName": self.credentials.get("APP_NAME", ""),
                    "appVer": "1.0",
                    "key": self.credentials.get("USER_KEY", ""),
                    "osName": "WEB",
                    "requestCode": "5PLoginV4",
                    "userId": self.credentials.get("USER_ID", ""),
                    "password": self.credentials.get("PASSWORD", "")
                },
                "body": {
                    "ClientCode": self.credentials.get("USER_ID", ""),
                    "TOTP": totp,
                    "PIN": pin
                }
            }
            
            logger.info(f" Attempting TOTP login for user {self.credentials.get('USER_ID')}")
            
            response = await self.http_client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("body", {}).get("Status") == 0:
                self.access_token = data["body"].get("AccessToken")
                self.client_code = data["body"].get("ClientCode")
                logger.info(f" TOTP login successful, token obtained")
                return {
                    "success": True,
                    "access_token": self.access_token,
                    "client_code": self.client_code
                }
            else:
                error_msg = data.get("body", {}).get("Message", "Unknown error")
                logger.error(f" TOTP login failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f" HTTP error during login: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f" Login failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def place_order(
        self,
        scrip_code: int,
        exchange: str,
        exchange_type: str,
        order_type: str,
        quantity: int,
        price: float,
        is_intraday: bool = False,
        at_market: bool = False,
        order_validity: int = 0,
        stop_loss_price: float = 0.0,
        disclosed_qty: int = 0,
        target_price: float = 0.0,
        trailing_sl: float = 0.0,
        variety: str = "regular",
        is_amo: bool = False
    ) -> Dict[str, Any]:
        """
        Place order using direct REST API
        
        Args:
            scrip_code: 5paisa scrip code
            exchange: Exchange code (N=NSE, B=BSE)
            exchange_type: C=Cash, D=Derivative
            order_type: B=Buy, S=Sell
            quantity: Order quantity
            price: Order price
            is_intraday: True for MIS, False for CNC
            at_market: True for market order
            order_validity: 0=Day, 1=IOC
            stop_loss_price: For SL orders
            disclosed_qty: Disclosed quantity
            
        Returns:
            Dict with order_id and status
        """
        if not self.access_token:
            logger.error(" No access token available, please login first")
            return {
                "success": False,
                "error": "Not authenticated"
            }
        
        try:
            url = f"{self.BASE_URL}/V1/PlaceOrderRequest"
            
            payload = {
                "head": {
                    "appName": self.credentials.get("APP_NAME", ""),
                    "appVer": "1.0",
                    "key": self.credentials.get("USER_KEY", ""),
                    "osName": "WEB",
                    "requestCode": "5POrdReq",
                    "userId": self.credentials.get("USER_ID", ""),
                    "password": self.credentials.get("PASSWORD", "")
                },
                "body": {
                    "ClientCode": self.client_code,
                    "ScripCode": scrip_code,
                    "Exchange": exchange,
                    "ExchangeType": exchange_type,
                    "OrderType": order_type,
                    "Qty": quantity,
                    "Price": price,
                    "IsIntraday": is_intraday,
                    "AtMarket": at_market,
                    "iOrderValidity": order_validity,
                    "StopLossPrice": stop_loss_price,
                    "DisQty": disclosed_qty,
                    "PublicIP": "0.0.0.0",
                    "AHPlaced": "Y" if is_amo else "N",
                    "AlgoID": 0
                }
            }
            
            # Map Variety specific fields (if using 5paisa's specific BO/CO endpoints or parameters)
            # Standard PlaceOrderRequest often takes StopLossPrice. 
            # For BO, we might need TargetPrice.
            if variety.lower() == "bo":
                payload["body"]["TargetPrice"] = target_price
            
            if trailing_sl > 0:
                payload["body"]["TrailingSL"] = trailing_sl
            
            logger.info(f" Placing order: {order_type} {quantity} @ {price} (ScripCode: {scrip_code})")
            
            response = await self.http_client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            body = data.get("body", {})
            status = body.get("Status", -1)
            
            if status == 0:
                order_id = body.get("BrokerOrderID") or body.get("ExchOrderID")
                logger.info(f" Order placed successfully: {order_id}")
                return {
                    "success": True,
                    "order_id": order_id,
                    "message": body.get("Message", "Order placed")
                }
            else:
                error_msg = body.get("Message", "Order placement failed")
                logger.error(f" Order placement failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f" HTTP error during order placement: {e.response.status_code}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}"
            }
        except Exception as e:
            logger.error(f" Order placement failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
