from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import settings
from app.models.entities import Base

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
        # SQLite schema auto-migration for newly added columns
        if "sqlite" in settings.DATABASE_URL:
            # Check publishing_history columns
            try:
                res = await conn.execute(text("PRAGMA table_info(publishing_history)"))
                columns = [row[1] for row in res.fetchall()]
                if columns and "provider" not in columns:
                    await conn.execute(text("ALTER TABLE publishing_history ADD COLUMN provider VARCHAR(50) DEFAULT 'mock'"))
            except Exception:
                pass
                
            # Check linkedin_connections columns
            try:
                res = await conn.execute(text("PRAGMA table_info(linkedin_connections)"))
                columns = [row[1] for row in res.fetchall()]
                if columns and "linkedin_member_urn" not in columns:
                    await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN linkedin_member_urn VARCHAR(191)"))
                if columns and "linkedin_member_id" not in columns:
                    await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN linkedin_member_id VARCHAR(191)"))
                if columns and "scopes" not in columns:
                    await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN scopes VARCHAR(255) DEFAULT 'openid profile email w_member_social'"))
                if columns and "provider" not in columns:
                    await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN provider VARCHAR(50) DEFAULT 'mock'"))
            except Exception:
                pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
