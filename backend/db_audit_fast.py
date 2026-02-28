
import asyncio
import asyncpg
import os

async def check_ownership():
    # Load DATABASE_URL from .env manually to be safe
    db_url = "postgresql://postgres:root@localhost:5432/trading_db"
    
    print("\n--- ACCOUNT OWNERSHIP AUDIT ---")
    try:
        conn = await asyncpg.connect(db_url)
        print(f"Connected to DB: {db_url}")
        
        query = """
        SELECT 
            u.user_id as system_user_id,
            u.email as system_user_email,
            a.account_id as trading_acc_internal_id,
            a.trading_login_id as broker_login_id,
            a.broker_name,
            a.nickname
        FROM users u
        LEFT JOIN accounts a ON u.user_id = a.owner_id
        ORDER BY u.user_id;
        """
        
        rows = await conn.fetch(query)
        
        if not rows:
            print("No users or accounts found.")
        else:
            current_user = None
            for r in rows:
                if r['system_user_email'] != current_user:
                    print(f"\nSYSTEM USER: {r['system_user_email']} (ID: {r['system_user_id']})")
                    current_user = r['system_user_email']
                
                if r['trading_acc_internal_id']:
                    print(f"  -> TRADING ACC: {r['broker_name']} | ID: {r['broker_login_id']} | Nickname: {r['nickname']}")
                else:
                    print(f"  -> NO TRADING ACCOUNTS")
        
        await conn.close()
    except Exception as e:
        print(f"DB AUDIT ERROR: {e}")
    print("\n-------------------------------\n")

if __name__ == "__main__":
    asyncio.run(check_ownership())
