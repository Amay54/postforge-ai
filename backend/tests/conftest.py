import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.entities import Base, User
from app.services.security import get_password_hash, create_access_token
from app.database.session import get_db
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(test_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_user(db_session: AsyncSession):
    user = User(
        email="test_user@postforge.ai",
        name="Test Engineer",
        hashed_password=get_password_hash("password123")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user: User):
    token = create_access_token({"sub": test_user.id, "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
