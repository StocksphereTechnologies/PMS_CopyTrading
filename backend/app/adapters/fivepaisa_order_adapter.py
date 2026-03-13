# """
# 5paisa order adapter using direct API
# """

# import logging
# from typing import Dict, Any, Optional, List
# from datetime import datetime, timezone
# from app.models.account import Account

# logger = logging.getLogger(__name__)


# class FivePaisaOrderAdapter:
#     """Adapter for fetching orders from 5paisa"""

#     async def get_orders(self, account: Account) -> Optional[List[Dict[str, Any]]]:

#         try:

#             token = account.access_token

#             if not token:
#                 logger.error(f"No access token for 5paisa account {account.account_id}")
#                 return None

#             # Clean token (same logic as margin adapter)
#             def deep_clean(t):
#                 if not t: 
#                     return t
#                 if isinstance(t, bytes):
#                     return deep_clean(t.decode("utf-8"))
#                 if isinstance(t, str):
#                     t = t.strip()

#                     if len(t) >= 2 and ((t[0] == "'" and t[-1] == "'") or (t[0] == '"' and t[-1] == '"')):
#                         return deep_clean(t[1:-1])

#                     if len(t) > 3 and t.startswith("b") and t[1] in ("'", '"') and t.endswith(t[1]):
#                         return deep_clean(t[2:-1])

#                     return t

#                 return str(t)

#             clean_token = deep_clean(token)

#             headers = {
#                 "Content-Type": "application/json",
#                 "Authorization": f"Bearer {clean_token}",
#                 "5Paisa-API-Uid": "ka7SFqAU6SC"
#             }

#             payload = {
#                 "head": {
#                     "key": account.user_key
#                 },
#                 "body": {
#                     "ClientCode": account.trading_login_id
#                 }
#             }

#             url = "https://Openapi.5paisa.com/VendorsAPI/Service1.svc/V3/OrderBook"

#             from app.core.http import HttpClient
#             client = HttpClient.get_client()

#             response = await client.post(url, json=payload, headers=headers, timeout=10.0)

#             if response.status_code != 200:
#                 logger.error(f"5paisa Order API Error {response.status_code}: {response.text}")
#                 return None

#             resp_data = response.json()

#             if resp_data.get("head", {}).get("status") != "0":
#                 error_msg = resp_data.get("head", {}).get("statusDescription", "Unknown error")
#                 logger.error(f"5paisa logical error: {error_msg}")
#                 return None

#             orders = resp_data.get("body", {}).get("OrderBookDetail", [])

#             if not orders:
#                 return []

#             return self._transform_orders(orders, account)

#         except Exception as e:
#             logger.error(f"Error fetching orders for account {account.account_id}: {e}", exc_info=True)
#             return None


#     def _transform_orders(self, raw_orders: List[Dict[str, Any]], account: Account) -> List[Dict[str, Any]]:

#         transformed_orders = []

#         for o in raw_orders:

#             transformed_orders.append({

#                 "symbol": o.get("ScripName", ""),
#                 "trdAcc": account.trading_login_id,
#                 "pseAcc": account.nickname,

#                 "id": o.get("OrderID"),
#                 "updateTime": o.get("OrderDateTime"),
#                 "status": o.get("OrderStatus"),

#                 "qty": o.get("Qty", 0),
#                 "price": o.get("Price", 0),

#                 "variety": o.get("OrderType"),
#                 "trade": o.get("BuySell"),
#                 "order": o.get("OrderType"),

#                 "product": o.get("ExchangeType"),
#                 "exch": o.get("Exchange"),

#                 "trigPrc": o.get("TriggerPrice", 0),

#                 "fillQty": o.get("QtyExecuted", 0),
#                 "pendQty": o.get("QtyRemaining", 0),

#                 "avgPrc": o.get("AvgRate", 0),

#                 "exchId": o.get("ExchOrderID"),
#                 "parentId": "",

#                 "discQty": o.get("DisQty", 0),

#                 "amo": False,
#                 "validity": "DAY",

#                 "rejectReason": o.get("Reason"),

#                 "brStatus": o.get("OrderStatus"),
#                 "brExch": o.get("Exchange"),
#                 "brSymbol": o.get("ScripName"),

#                 "day": "DAY",
#                 "client": account.nickname,

#                 "platform": "5paisa",
#                 "broker": "5PAISA",

#                 "copyTrace": "",

#             })

#         return transformed_orders