import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://eval2:eval2@localhost:5432/eval2db")
options = {"echo": False, "pool_pre_ping": True}
if os.getenv("TESTING") == "1":
    options["poolclass"] = NullPool
engine = create_async_engine(DATABASE_URL, **options)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with SessionLocal() as session:
        yield session
