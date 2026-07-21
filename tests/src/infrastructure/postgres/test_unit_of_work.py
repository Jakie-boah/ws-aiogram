import pytest

from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository


@pytest.mark.asyncio
async def test_instance(uow):
    assert isinstance(uow.message, PostgresMessageRepository)
    assert isinstance(uow.ticket, PostgresTicketRepository)

