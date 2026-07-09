from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        # Try to create tables, but ignore if they already exist
        # This prevents race condition when multiple workers start simultaneously
        try:
            await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            # Likely a duplicate key error from concurrent initialization
            # Tables already exist, so we can safely continue
            if "duplicate key" not in str(e) and "already exists" not in str(e):
                raise
