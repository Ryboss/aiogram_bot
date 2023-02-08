from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, future=True, pool_pre_ping=True, poolclass=NullPool)


async def init_db() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,  # type: ignore
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
