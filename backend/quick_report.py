
import asyncio
import os
import sys
from sqlalchemy import select

# Add current dir to sys.path
sys.path.insert(0, os.getcwd())

from app.core.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models.account import Account

async def quick_report():
    print("QUICK REPORT START")
    try:
        async with AsyncSessionLocal() as db:
            print("DB CONNECTED")
            # Users
            res = await db.execute(select(User))
            users = res.scalars().all()
            print(f"Users found: {len(users)}")
            for u in users:
                print(f"USER: ID={u.user_id}, Email={u.email}")
                
            # Accounts
            res = await db.execute(select(Account))
            accs = res.scalars().all()
            print(f"Accounts found: {len(accs)}")
            for a in accs:
                print(f"ACC: ID={a.account_id}, OwnerID={a.owner_id}, Broker={a.broker_name}, ID={a.trading_login_id}")
    except Exception as e:
        print(f"QUICK REPORT ERROR: {e}")
    finally:
        await engine.dispose()
        print("QUICK REPORT END")

if __name__ == "__main__":
    asyncio.run(quick_report())
