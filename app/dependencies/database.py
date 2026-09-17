from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that injects an async database session.
    """
    async for session in get_async_db():
        yield session
