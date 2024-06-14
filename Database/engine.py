import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from Database.models import Base


async_engine = create_async_engine(os.getenv("DB_LITE"))

session_maker = async_sessionmaker(bind = async_engine, class_ = AsyncSession, expire_on_commit = False)


async def as_create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def as_drop_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)