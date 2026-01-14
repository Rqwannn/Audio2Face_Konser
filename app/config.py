"""
Application Configuration
Environment variables and settings
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore" 
    )

    SERVER_BUCKET_PROD: str = os.getenv("SERVER_BUCKET_PROD", "")
    ACCESS_KEY_BUCKET_PROD: str = os.getenv("ACCESS_KEY_BUCKET_PROD", "")
    PRIVATE_KEY_BUCKET_PROD: str = os.getenv("PRIVATE_KEY_BUCKET_PROD", "")
    REGION_BUCKET_PROD: str = os.getenv("REGION_BUCKET_PROD", "")
    S3_BUCKET_PROD: str = os.getenv("S3_BUCKET_PROD", "")
    AUTH_VERIFY_URL: str = os.getenv("AUTH_VERIFY_URL", "http://localhost:8000/verify-token")

settings = Settings()

class Database:
    def __init__(self):
        DB_HOST: str = os.getenv("DB_HOST_PROD")
        DB_DIALECT: str = os.getenv("DB_DIALECT_PROD")
        DB_USERNAME: str = os.getenv("DB_USERNAME_PROD")
        DB_PASSWORD: str = urllib.parse.quote(os.getenv("DB_PASSWORD_PROD"))
        DB_NAME: str = os.getenv("DB_NAME_PROD")
        DB_PORT: str = int(os.getenv("DB_PORT_PROD", 5432))
        
        self.DATABASE_URL: str = f"{DB_DIALECT}+asyncpg://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        self.engine = create_async_engine(
            self.DATABASE_URL,
            echo=True,  # Set False di production
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        self.Base = declarative_base()
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Dependency untuk mendapatkan database session"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.drop_all)
    
    async def close(self):
        """Close database connection"""
        await self.engine.dispose()

# Initialize database instance
database = Database()
Base = database.Base

# Dependency function
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in database.get_session():
        yield session

__all__ = ['settings']