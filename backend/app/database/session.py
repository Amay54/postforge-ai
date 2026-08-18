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
                cols = [row[1] for row in res.fetchall()]
                if cols:
                    if "provider" not in cols:
                        await conn.execute(text("ALTER TABLE publishing_history ADD COLUMN provider VARCHAR(50) DEFAULT 'mock'"))
                    if "is_mock" not in cols:
                        await conn.execute(text("ALTER TABLE publishing_history ADD COLUMN is_mock BOOLEAN DEFAULT 1"))
            except Exception:
                pass
                
            # Check linkedin_connections columns
            try:
                res = await conn.execute(text("PRAGMA table_info(linkedin_connections)"))
                cols = [row[1] for row in res.fetchall()]
                if cols:
                    if "profile_name" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN profile_name VARCHAR(150)"))
                    if "profile_url" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN profile_url VARCHAR(255)"))
                    if "linkedin_member_urn" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN linkedin_member_urn VARCHAR(191)"))
                    if "linkedin_member_id" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN linkedin_member_id VARCHAR(191)"))
                    if "scopes" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN scopes VARCHAR(255) DEFAULT 'openid profile email w_member_social'"))
                    if "provider" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN provider VARCHAR(50) DEFAULT 'mock'"))
                    if "connected_at" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN connected_at DATETIME"))
                    if "updated_at" not in cols:
                        await conn.execute(text("ALTER TABLE linkedin_connections ADD COLUMN updated_at DATETIME"))
            except Exception:
                pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
