
import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Add current dir to sys.path
sys.path.insert(0, os.getcwd())

from app.core.database import AsyncSessionLocal, engine
from app.models.user import User
from app.models.account import Account

async def generate_report():
    print("\n" + "="*80)
    print("SYSTEM USERS AND TRADING ACCOUNTS MAPPING REPORT".center(80))
    print("="*80 + "\n")
    
    try:
        async with AsyncSessionLocal() as db:
            # Fetch users and their accounts
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("No users found in the system.")
                return

            for user in users:
                print(f"USER: {user.email} (System ID: {user.user_id})")
                print(f"|-- Name: {user.full_name}")
                print(f"|-- Active: {user.is_active}")
                
                # Fetch accounts for this user
                acc_result = await db.execute(select(Account).where(Account.owner_id == user.user_id))
                accounts = acc_result.scalars().all()
                
                if not accounts:
                    print("|   |-- NO TRADING ACCOUNTS linked to this user.")
                else:
                    for acc in accounts:
                        print(f"|   |-- TRADING ACCOUNT: {acc.broker_name}")
                        print(f"|       |-- ID: {acc.account_id}")
                        print(f"|       |-- Nickname: {acc.nickname or 'N/A'}")
                        print(f"|       |-- Broker ID: {acc.trading_login_id}")
                        print(f"|       |-- Enabled: {acc.is_enabled}")
                        print(f"|       |-- Validated: {acc.is_validated}")
                print("-" * 40)
                
    except Exception as e:
        print(f"ERROR GENERATING REPORT: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(generate_report())
