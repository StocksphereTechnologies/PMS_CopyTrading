"""
Self-contained Zerodha Kite Connect HTTP client
Uses httpx for async requests — same approach as the main system's ZerodhaAdapter
"""
import httpx
import logging
from typing import Dict, List, Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class ZerodhaClient:
    """
    Kite Connect REST API client.
    Auth: Authorization: token {api_key}:{access_token}
    All order endpoints use form-encoded POST (not JSON).
    """

    def __init__(self, api_key: str, access_token: str):
        self.api_key = api_key
        self.access_token = access_token
        self.base_url = settings.ZERODHA_API_BASE_URL

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "X-Kite-Version": "3",
            "Authorization": f"token {self.api_key}:{self.access_token}",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Kite API"""
        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            if method == "GET":
                resp = await client.get(url, headers=self._headers, params=params)
            elif method == "POST":
                # Kite API expects form-encoded data for orders
                resp = await client.post(url, headers=self._headers, data=data)
            elif method == "PUT":
                resp = await client.put(url, headers=self._headers, data=data)
            elif method == "DELETE":
                resp = await client.delete(url, headers=self._headers, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")

            try:
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                try:
                    error_data = resp.json()
                    error_msg = error_data.get("message", str(e))
                    logger.error(f"Kite API Error ({resp.status_code}): {error_msg}")
                    return {"status": "error", "message": error_msg}
                except Exception:
                    logger.error(f"Kite API Error ({resp.status_code}): {str(e)}")
                    raise e

    # ─── Order Endpoints ───

    async def get_orders(self) -> List[Dict[str, Any]]:
        """
        GET /orders — Fetch all orders for the day.
        Returns list of order dicts with fields:
        order_id, tradingsymbol, exchange, transaction_type, quantity,
        order_type, product, price, trigger_price, average_price,
        status, status_message, variety, validity, ...
        """
        result = await self._request("GET", "/orders")
        if result.get("status") == "error":
            logger.error(f"Failed to fetch orders: {result.get('message')}")
            return []
        return result.get("data", []) or []

    async def get_order_history(self, order_id: str) -> List[Dict[str, Any]]:
        """GET /orders/{order_id} — Fetch status trail for a specific order"""
        result = await self._request("GET", f"/orders/{order_id}")
        if result.get("status") == "error":
            return []
        return result.get("data", []) or []

    async def place_order(
        self,
        tradingsymbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "NRML",
        price: float = 0,
        trigger_price: float = 0,
        validity: str = "DAY",
        variety: str = "regular",
        disclosed_quantity: int = 0,
        tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        POST /orders/{variety} — Place an order.
        Returns {"order_id": "...", "status": "SUCCESS"} or error.
        """
        data = {
            "tradingsymbol": tradingsymbol,
            "exchange": exchange,
            "transaction_type": transaction_type,
            "quantity": int(quantity),
            "order_type": order_type,
            "product": product,
            "price": float(price),
            "trigger_price": float(trigger_price),
            "validity": validity,
            "disclosed_quantity": int(disclosed_quantity),
        }
        if tag:
            data["tag"] = tag

        logger.info(f"Placing order: {transaction_type} {quantity}x {tradingsymbol} ({order_type})")
        result = await self._request("POST", f"/orders/{variety}", data=data)

        if result.get("status") == "success":
            return {
                "order_id": result["data"]["order_id"],
                "status": "SUCCESS",
                "message": "Order placed successfully",
            }
        else:
            return {
                "order_id": None,
                "status": "FAILED",
                "error": result.get("message", "Unknown error"),
            }

    async def modify_order(
        self,
        order_id: str,
        variety: str = "regular",
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        trigger_price: Optional[float] = None,
        validity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """PUT /orders/{variety}/{order_id} — Modify an open order"""
        data = {}
        if quantity is not None:
            data["quantity"] = int(quantity)
        if price is not None:
            data["price"] = float(price)
        if order_type is not None:
            data["order_type"] = order_type
        if trigger_price is not None:
            data["trigger_price"] = float(trigger_price)
        if validity is not None:
            data["validity"] = validity

        result = await self._request("PUT", f"/orders/{variety}/{order_id}", data=data)
        if result.get("status") == "success":
            return {"order_id": result["data"]["order_id"], "status": "SUCCESS"}
        return {"order_id": None, "status": "FAILED", "error": result.get("message")}

    async def cancel_order(self, order_id: str, variety: str = "regular") -> Dict[str, Any]:
        """DELETE /orders/{variety}/{order_id} — Cancel an open order"""
        result = await self._request("DELETE", f"/orders/{variety}/{order_id}")
        if result.get("status") == "success":
            return {"order_id": result["data"]["order_id"], "status": "SUCCESS"}
        return {"order_id": None, "status": "FAILED", "error": result.get("message")}

    # ─── Profile / Validation ───

    async def get_profile(self) -> Optional[Dict[str, Any]]:
        """GET /user/profile — Validate that token is working"""
        try:
            result = await self._request("GET", "/user/profile")
            if result.get("status") == "error":
                return None
            return result.get("data")
        except Exception as e:
            logger.error(f"Profile fetch failed: {e}")
            return None

    async def get_positions(self) -> List[Dict[str, Any]]:
        """GET /portfolio/positions — Fetch open positions"""
        result = await self._request("GET", "/portfolio/positions")
        if result.get("status") == "error":
            return []
        return result.get("data", {}).get("net", []) or []
