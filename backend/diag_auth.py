
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password

async def diagnostic():
    async with AsyncSessionLocal() as db:
        # Check user
        email = "user@example.com"
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"User {email} not found!")
            return
            
        print(f"User found: ID={user.user_id}, Email={user.email}, Active={user.is_active}")
        
        # Test token
        data = {"user_id": user.user_id, "email": user.email}
        token = create_access_token(data)
        print(f"Generated token: {token}")
        
        decoded = decode_access_token(token)
        print(f"Decoded token: {decoded}")
        
        if decoded and decoded.get("user_id") == user.user_id:
            print("Token logic is CORRECT")
        else:
            print("Token logic is INCORRECT")

if __name__ == "__main__":
    asyncio.run(diagnostic())
