"""
Order service for fetching order data from multiple brokers
"""

import logging
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.account import Account, BrokerName
from app.services.account_service import AccountService
from app.adapters.zerodha_adapter import ZerodhaAdapter
from app.adapters.fivepaisa_adapter import FivePaisaAdapter

logger = logging.getLogger(__name__)

class OrderService:

    @staticmethod
    async def get_orders_for_user(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:

        accounts = await AccountService.get_user_accounts(db, user_id, enabled_only=True)

        if not accounts:
            return []

        import asyncio

        semaphore = asyncio.Semaphore(10)

        async def fetch_orders(account):

            async with semaphore:

                try:

                    if account.broker_name == BrokerName.ZERODHA.value:
                        adapter = ZerodhaAdapter(account=account)

                    elif account.broker_name == BrokerName.FIVEPAISA.value:
                        adapter = FivePaisaAdapter(account=account)
                        

                    else:
                        return []
                        
                    print("Fetching orders for account:", account.account_id, "Broker:", account.broker_name, flush=True)
                    
                    orders = await adapter.get_orders()

                    print(f"Fetched {len(orders)} orders for account {account.account_id}")

                    return orders

                except Exception as e:
                    logger.error(f"Error fetching orders for account {account.account_id}: {e}")
                    return []

        tasks = [fetch_orders(account) for account in accounts]

        results = await asyncio.gather(*tasks)

        orders = []

        for r in results:
            if r:
                orders.extend(r)

        return orders