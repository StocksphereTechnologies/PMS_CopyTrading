
import asyncio
import asyncpg

async def check_db():
    conn_str = "postgresql://postgres:root@localhost:5432/trading_db"
    print(f"CONNECTING TO {conn_str}...")
    try:
        conn = await asyncpg.connect(conn_str)
        print("CONNECTED!")
        rows = await conn.fetch("SELECT user_id, email, is_active FROM users")
        print(f"FOUND {len(rows)} USERS:")
        for r in rows:
            print(f"- ID: {r['user_id']}, Email: {r['email']}, Active: {r['is_active']}")
        await conn.close()
    except Exception as e:
        print(f"DB ERROR: {str(e)}")

if __name__ == "__main__":
    asyncio.run(check_db())
