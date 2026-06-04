import pytest_asyncio

from src.presentation.dependency_container import create_container


@pytest_asyncio.fixture(scope="session")
async def container_app(config):
    container_ = create_container(config)
    yield container_
    await container_.close()


@pytest_asyncio.fixture(name="container", scope="function")
async def request_container(container_app):
    async with container_app() as c:
        yield c
