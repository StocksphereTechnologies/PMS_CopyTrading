"""
API dependencies
"""
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    async for session in get_db():
        yield session
