
import asyncio
import os
import sys

# Add working directory to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from app.models.account import Account, BrokerName
from sqlalchemy import select

async def check_accounts():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Account).where(Account.is_enabled == True))
        accounts = result.scalars().all()
        
        print(f"\n--- ACTIVE ACCOUNTS REPORT ---")
        print(f"Total enabled accounts found: {len(accounts)}")
        
        zerodha_count = 0
        fivepaisa_count = 0
        
        for acc in accounts:
            if acc.broker_name == "ZERODHA":
                zerodha_count += 1
                status = "VALIDATED" if acc.is_validated else "NOT VALIDATED"
                print(f"[ZERODHA] Account ID: {acc.account_id}, Login ID: {acc.trading_login_id}, Status: {status}")
            elif acc.broker_name == "FIVEPAISA":
                fivepaisa_count += 1
                status = "VALIDATED" if acc.is_validated else "NOT VALIDATED"
                print(f"[FIVEPAISA] Account ID: {acc.account_id}, Login ID: {acc.trading_login_id}, Status: {status}")
        
        print(f"\nSummary:")
        print(f"- Zerodha active: {zerodha_count}")
        print(f"- 5paisa active: {fivepaisa_count}")
        print(f"-------------------------------\n")

if __name__ == "__main__":
    asyncio.run(check_accounts())
