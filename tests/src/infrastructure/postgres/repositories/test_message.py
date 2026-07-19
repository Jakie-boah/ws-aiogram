import pytest
import pytest_asyncio

from src.infrastructure.postgres.repositories.message import ImplPostgresMessageRepository
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from src.infrastructure.postgres.tables import messages_table
from sqlalchemy import select
from src.domain.entities.message import Message


@pytest.fixture(name="repository")
def message_repository(session):
    return ImplPostgresMessageRepository(session)


@pytest_asyncio.fixture()
async def insert_ticket(ticket, session):
    ticket = ticket()
    await ImplPostgresTicketRepository(session).save(ticket)
    await session.commit()
    return ticket


@pytest.mark.asyncio
async def test_save(insert_ticket, message, session, repository):
    ticket = insert_ticket
    message = message()
    await repository.save(message)
    await session.commit()
    rows = await session.execute(select(messages_table).where(messages_table.c.id == message.id.value))
    result = rows.mappings().one_or_none()
    assert result is not None
    assert result.ticket_id == ticket.id.value


@pytest.mark.asyncio
async def test_get(insert_ticket, message, session, repository):
    ticket = insert_ticket
    message = message()
    await repository.save(message)
    await session.commit()

    loaded = await repository.get(uid=message.id)
    assert isinstance(loaded, Message)
