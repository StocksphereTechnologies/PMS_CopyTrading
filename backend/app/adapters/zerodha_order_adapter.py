# """
# Zerodha order adapter using KiteConnect API
# """

# import logging
# from typing import Dict, Any, Optional, List
# from kiteconnect import KiteConnect
# from app.models.account import Account
# from datetime import datetime, timezone

# logger = logging.getLogger(__name__)


# class ZerodhaOrderAdapter:
#     """Adapter for fetching orders from Zerodha"""

#     async def get_orders(self, account: Account) -> Optional[List[Dict[str, Any]]]:

#         try:

#             if not account.access_token:
#                 logger.error(f"No access token for Zerodha account {account.account_id}")
#                 return None

#             if not account.api_key:
#                 logger.error(f"No API key for Zerodha account {account.account_id}")
#                 return None

#             token = account.access_token

#             # Same deep_clean logic used in margin adapter
#             def deep_clean(t):
#                 if not t: return t
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

#             token = deep_clean(token)

#             print(
#                 f"DEBUG: Zerodha order adapter account {account.account_id} token cleaned.",
#                 flush=True
#             )

#             kite = KiteConnect(api_key=account.api_key)

#             kite.set_access_token(token)

#             logger.info(f"Fetching orders for Zerodha account {account.account_id}")

#             import asyncio
#             raw_orders = await asyncio.to_thread(kite.orders)

#             logger.info(f"Fetched {len(raw_orders)} orders for account {account.account_id}")

#             return self._transform_orders(raw_orders, account)

#         except Exception as e:
#             logger.error(
#                 f"Error fetching Zerodha orders for account {account.account_id}: {e}",
#                 exc_info=True
#             )
#             return None


#     def _transform_orders(self, raw_orders: List[Dict[str, Any]], account: Account) -> List[Dict[str, Any]]:

#         transformed_orders = []

#         for o in raw_orders:

#             transformed_orders.append({

#                 "symbol": o.get("tradingsymbol"),
#                 "trdAcc": account.trading_login_id,
#                 "pseAcc": account.nickname,

#                 "id": o.get("order_id"),
#                 "updateTime": o.get("order_timestamp"),
#                 "status": o.get("status"),

#                 "qty": o.get("quantity", 0),
#                 "price": o.get("price", 0),

#                 "variety": o.get("variety"),
#                 "trade": o.get("transaction_type"),
#                 "order": o.get("order_type"),

#                 "product": o.get("product"),
#                 "exch": o.get("exchange"),

#                 "trigPrc": o.get("trigger_price", 0),

#                 "fillQty": o.get("filled_quantity", 0),
#                 "pendQty": o.get("pending_quantity", 0),

#                 "pubId": "",

#                 "avgPrc": o.get("average_price", 0),

#                 "exchId": o.get("exchange_order_id"),
#                 "parentId": o.get("parent_order_id"),

#                 "discQty": o.get("disclosed_quantity", 0),

#                 "amo": True if o.get("variety") == "amo" else False,

#                 "validity": o.get("validity"),

#                 "rejectReason": o.get("status_message"),

#                 "brStatus": o.get("status"),
#                 "brExch": o.get("exchange"),
#                 "brSymbol": o.get("tradingsymbol"),

#                 "day": "DAY",
#                 "client": account.nickname,

#                 "platform": "Kite",
#                 "broker": "ZERODHA",

#                 "copyTrace": "",

#                 "account_id": account.account_id,

#                 "last_updated": datetime.now(timezone.utc)
#             })

#         return transformed_orders