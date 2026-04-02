import asyncio
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.account_service import AccountService
from app.models.account import BrokerName
from app.adapters.zerodha_adapter import ZerodhaAdapter
from app.adapters.fivepaisa_adapter import FivePaisaAdapter

class HoldingsService:

    @staticmethod
    async def get_holdings_for_user(db: AsyncSession, user_id: int) -> List[Dict[str, Any]]:

        accounts = await AccountService.get_user_accounts(db, user_id, enabled_only=True)

        if not accounts:
            return []

        semaphore = asyncio.Semaphore(10)

        async def fetch(account):
            async with semaphore:
                try:
                    if account.broker_name == BrokerName.ZERODHA.value:
                        adapter = ZerodhaAdapter(account)
                    elif account.broker_name == BrokerName.FIVEPAISA.value:
                        adapter = FivePaisaAdapter(account)
                    else:
                        return []

                    return await adapter.get_holdings()

                except Exception:
                    return []

        results = await asyncio.gather(*[fetch(a) for a in accounts])

        holdings = []
        for r in results:
            if r:
                holdings.extend(r)

        return holdings