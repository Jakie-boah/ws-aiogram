import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from src.infrastructure.postgres.tables import metadata


# from src.application.interfaces.postgres.uow import UnitOfWork

@pytest_asyncio.fixture(scope="session")
async def engine(container_app):
    return await container_app.get(AsyncEngine)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session(engine, container):
    yield await container.get(AsyncSession)

# @pytest_asyncio.fixture
# async def uow(container):
#     return await container.get(UnitOfWork)
