import datetime

import pytest
import pytest_asyncio
from zoneinfo import ZoneInfo
from src.application.interfaces.postgres.repositories.errors import EntityNotFoundError
from src.infrastructure.postgres.repositories.message import ImplPostgresMessageRepository
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from src.infrastructure.postgres.tables import messages_table
from sqlalchemy import select, RowMapping
from src.domain.entities.message import Message
from src.domain.values import MessageId


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
    assert result.ticket_id == message.ticket_id.value
    assert_row_and_message(result, message)


@pytest.mark.asyncio
async def test_upsert(insert_ticket, message, repository, session):
    message = message()
    await repository.save(message)
    await session.commit()
    assert message.delivered_at is None
    assert message.read_at is None
    delivered_at = datetime.datetime.now(ZoneInfo("Europe/Moscow"))
    read_at = datetime.datetime.now(ZoneInfo("Europe/Moscow")) + datetime.timedelta(seconds=1)

    message.mark_delivered_at(delivered_at)
    message.mark_read_at(read_at)

    await repository.save(message)
    await session.commit()

    assert message.delivered_at == delivered_at
    assert message.read_at == read_at

    rows = await session.execute(select(messages_table).where(messages_table.c.id == message.id.value))
    result = rows.mappings().one()

    assert result.delivered_at == delivered_at
    assert result.read_at == read_at


@pytest.mark.asyncio
async def test_get(insert_ticket, message, session, repository):
    message = message()
    await repository.save(message)
    await session.commit()

    loaded = await repository.get(uid=message.id)
    assert isinstance(loaded, Message)
    assert_same_message(loaded, message)


def assert_same_message(actual: Message, expected: Message):
    assert actual.id == expected.id
    assert actual.ticket_id == expected.ticket_id
    assert actual.sender_id == expected.sender_id
    assert actual.sender_type == expected.sender_type
    assert actual.message_type == expected.message_type
    assert actual.text == expected.text if expected.text is not None else None
    assert actual.sent_at == expected.sent_at
    assert actual.delivered_at == expected.delivered_at
    assert actual.read_at == expected.read_at


def assert_row_and_message(row: RowMapping, message: Message):
    assert row.id == message.id.value
    assert row.ticket_id == message.ticket_id.value
    assert row.sender_id == message.sender_id.value
    assert row.sender_type == message.sender_type.value
    assert row.message_type == message.message_type.value
    assert row.text == message.text.value if message.text is not None else None
    assert row.sent_at == message.sent_at
    assert row.delivered_at == message.delivered_at
    assert row.read_at == message.read_at


@pytest.mark.asyncio
async def test_get_raise_entity_not_found(repository):
    with pytest.raises(EntityNotFoundError):
        await repository.get(uid=MessageId.generate())
