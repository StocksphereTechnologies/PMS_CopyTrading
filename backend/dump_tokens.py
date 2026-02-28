
import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.getcwd())

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.account import Account

async def dump_raw_tokens():
    print("Connecting to database...")
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Account).where(Account.is_enabled == True))
            accounts = result.scalars().all()
            
            print(f"\nFound {len(accounts)} accounts.")
            print("-" * 50)
            for acc in accounts:
                token = acc.access_token
                print(f"ID: {acc.account_id} | Broker: {acc.broker_name}")
                print(f"  Type: {type(token)}")
                print(f"  Value (repr): {repr(token)}")
                
                # Check if it looks like bytes representation in string
                if isinstance(token, str):
                    if token.startswith("b'") or token.startswith('b"'):
                        print("  ALERT: Value is a STRING literal of bytes representation")
                print("-" * 50)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(dump_raw_tokens())
