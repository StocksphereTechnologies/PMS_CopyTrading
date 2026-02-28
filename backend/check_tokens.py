
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.account import Account

async def check_tokens():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Account).where(Account.is_enabled == True))
        accounts = result.scalars().all()
        
        print("\n--- Token Diagnostic ---")
        for acc in accounts:
            token = acc.access_token
            print(f"ID: {acc.account_id} | Broker: {acc.broker_name}")
            print(f"  Type: {type(token)}")
            if isinstance(token, bytes):
                print(f"  Value (bytes): {token}")
            elif isinstance(token, str):
                print(f"  Value (str): {token[:20]}...")
            else:
                print(f"  Value: {token}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(check_tokens())
