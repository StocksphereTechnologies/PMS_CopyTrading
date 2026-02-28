
import asyncio
import sys
import os

# Add parent directory to path so we can import app
sys.path.append(os.getcwd())

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.account import Account

async def check_tokens():
    print("Connecting to database...")
    try:
        async with AsyncSessionLocal() as db:
            print("Querying accounts...")
            result = await db.execute(select(Account))
            accounts = result.scalars().all()
            
            print(f"\nFound {len(accounts)} accounts.")
            print("-" * 50)
            for acc in accounts:
                token = acc.access_token
                print(f"ID: {acc.account_id} | Broker: {acc.broker_name} | Login ID: {acc.trading_login_id}")
                print(f"  Token Type: {type(token)}")
                if token:
                    # Check if it's a bytestring or a string representation of a bytestring like "b'xxxx'"
                    if isinstance(token, bytes):
                        print(f"  ALERT: Token is BYTES: {repr(token)[:50]}...")
                    elif isinstance(token, str) and (token.startswith("b'") or token.startswith('b"')):
                        print(f"  ALERT: Token is a STRING but looks like a bytestring representation: {token[:50]}...")
                    else:
                        print(f"  Token start: {repr(token)[:50]}...")
                else:
                    print("  Token: None")
                print("-" * 50)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(check_tokens())
