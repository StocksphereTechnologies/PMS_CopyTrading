
import asyncio
import os
import sys

# Add current dir to sys.path
sys.path.append(os.getcwd())

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine
from app.models.user import User
from app.core.security import create_access_token, decode_access_token

async def diagnostic():
    print("STARTING DIAGNOSTIC...", flush=True)
    try:
        async with AsyncSessionLocal() as db:
            print("DB SESSION OPENED", flush=True)
            # Check user
            email = "user@example.com"
            print(f"Searching for user: {email}", flush=True)
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"User {email} not found!", flush=True)
                # Let's list all users
                result = await db.execute(select(User))
                users = result.scalars().all()
                print(f"Total users in DB: {len(users)}", flush=True)
                for u in users:
                    print(f"- {u.email} (ID: {u.user_id})", flush=True)
                return
                
            print(f"User found: ID={user.user_id}, Email={user.email}, Active={user.is_active}", flush=True)
            
            # Test token
            data = {"user_id": user.user_id, "email": user.email}
            token = create_access_token(data)
            print(f"Generated token: {token}", flush=True)
            
            decoded = decode_access_token(token)
            print(f"Decoded token: {decoded}", flush=True)
            
            if decoded and decoded.get("user_id") == user.user_id:
                print("Token logic is CORRECT", flush=True)
            else:
                print("Token logic is INCORRECT", flush=True)
    except Exception as e:
        print(f"DIAGNOSTIC ERROR: {type(e).__name__}: {str(e)}", flush=True)
    finally:
        await engine.dispose()
        print("ENGINE DISPOSED", flush=True)

if __name__ == "__main__":
    asyncio.run(diagnostic())
