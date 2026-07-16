import pytest
import pytest_asyncio
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository


@pytest_asyncio.fixture(name="repository")
async def ticket_repository(session):
    return ImplPostgresTicketRepository(session)


@pytest.mark.asyncio
async def test_save(repository):
    raise NotImplementedError


@pytest.mark.asyncio
async def test_get(repository):
    raise NotImplementedError
