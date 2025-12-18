from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# Get DB URL from env, default to logic for dev (User must set ENV)
# For asyncpg, the driver is postgresql+asyncpg://
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/eduparty")

if not "asyncpg" in DATABASE_URL:
    # Auto-fix to ensure async driver if user creates URL without it
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create Async Engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Log SQL for debug
)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base Class for ORM
class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
