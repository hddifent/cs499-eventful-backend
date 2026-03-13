from typing import AsyncGenerator

from sqlalchemy.engine import url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

DATABASE_URL = url.URL.create(
    drivername="postgresql+asyncpg",
    username=settings.DB_USER,
    password=settings.DB_PASS,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
)

engine = create_async_engine(
    DATABASE_URL, echo=(not settings.PRODUCTION), pool_size=10, max_overflow=20
)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
