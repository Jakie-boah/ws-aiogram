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
from src.domain.values import MessageId, TicketId

MOSCOW = ZoneInfo("Europe/Moscow")
MINUTE = datetime.timedelta(minutes=1)
BASE_SENT_AT = datetime.datetime(2026, 1, 1, 12, 0, tzinfo=MOSCOW)


@pytest.fixture(name="repository")
def message_repository(session):
    return ImplPostgresMessageRepository(session)


@pytest_asyncio.fixture(name="insert_ticket")
async def insert_ticket_factory(ticket, session):
    async def __insert_ticket(**overrides):
        entity = ticket(**overrides)
        await ImplPostgresTicketRepository(session).save(entity)
        await session.commit()
        return entity

    return __insert_ticket


@pytest_asyncio.fixture()
async def inserted_ticket(insert_ticket):
    return await insert_ticket()


@pytest.mark.asyncio
async def test_save(inserted_ticket, message, session, repository):
    ticket = inserted_ticket
    message = message(ticket=ticket)
    await repository.save(message)
    await session.commit()
    rows = await session.execute(select(messages_table).where(messages_table.c.id == message.id.value))
    result = rows.mappings().one_or_none()
    assert result is not None
    assert result.ticket_id == ticket.id.value
    assert result.ticket_id == message.ticket_id.value
    assert_row_and_message(result, message)


@pytest.mark.asyncio
async def test_upsert(inserted_ticket, message, repository, session):
    ticket = inserted_ticket
    message = message(ticket=ticket)
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
async def test_get(inserted_ticket, message, session, repository):
    ticket = inserted_ticket

    message = message(ticket=ticket)
    await repository.save(message)
    await session.commit()

    loaded = await repository.get(uid=message.id)
    assert isinstance(loaded, Message)
    assert_same_message(loaded, message)


@pytest.mark.asyncio
async def test_find_undelivered_by_ticket(repository, inserted_ticket, message, session):
    ticket = inserted_ticket
    message = message(ticket=ticket)
    await repository.save(message)
    await session.commit()

    loaded = await repository.find_undelivered_by_ticket_id(ticket_id=ticket.id)
    assert isinstance(loaded, list)
    assert len(loaded) == 1
    assert isinstance(loaded[0], Message)
    assert_same_message(loaded[0], message)


@pytest.mark.asyncio
async def test_find_undelivered_by_ticket_sorted_by_sent_at(repository, inserted_ticket, message, session):
    ticket = inserted_ticket
    expected_order = [
        message(ticket=ticket, sent_at=BASE_SENT_AT + delta * MINUTE)
        for delta in (0, 1, 2, 3)
    ]
    for entity in (expected_order[2], expected_order[0], expected_order[3], expected_order[1]):
        await repository.save(entity)
    await session.commit()

    loaded = await repository.find_undelivered_by_ticket_id(ticket_id=ticket.id)

    assert [entity.id for entity in loaded] == [entity.id for entity in expected_order]
    assert [entity.sent_at for entity in loaded] == sorted(entity.sent_at for entity in expected_order)


@pytest.mark.asyncio
async def test_find_undelivered_by_ticket_skips_delivered_and_read(repository, inserted_ticket, message, session):
    ticket = inserted_ticket

    undelivered = message(ticket=ticket, sent_at=BASE_SENT_AT)

    delivered = message(ticket=ticket, sent_at=BASE_SENT_AT)
    delivered.mark_delivered_at(BASE_SENT_AT + MINUTE)

    read = message(ticket=ticket, sent_at=BASE_SENT_AT)
    read.mark_read_at(BASE_SENT_AT + MINUTE)

    for entity in (undelivered, delivered, read):
        await repository.save(entity)
    await session.commit()

    loaded = await repository.find_undelivered_by_ticket_id(ticket_id=ticket.id)

    assert [entity.id for entity in loaded] == [undelivered.id]
    assert_same_message(loaded[0], undelivered)


@pytest.mark.asyncio
async def test_find_undelivered_by_ticket_skips_other_tickets(repository, insert_ticket, message, session):
    ticket = await insert_ticket()
    other_ticket = await insert_ticket()

    mine = message(ticket=ticket, sent_at=BASE_SENT_AT)
    alien = message(ticket=other_ticket, sent_at=BASE_SENT_AT)

    for entity in (mine, alien):
        await repository.save(entity)
    await session.commit()

    loaded = await repository.find_undelivered_by_ticket_id(ticket_id=ticket.id)

    assert [entity.id for entity in loaded] == [mine.id]
    assert_same_message(loaded[0], mine)


@pytest.mark.asyncio
async def test_find_undelivered_by_ticket_returns_empty_when_all_delivered(
        repository, inserted_ticket, message, session
):
    ticket = inserted_ticket
    delivered = message(ticket=ticket, sent_at=BASE_SENT_AT)
    delivered.mark_delivered_at(BASE_SENT_AT + MINUTE)
    await repository.save(delivered)
    await session.commit()

    assert await repository.find_undelivered_by_ticket_id(ticket_id=ticket.id) == []


@pytest.mark.asyncio
async def test_find_undelivered_by_unknown_ticket_returns_empty(repository, inserted_ticket, message, session):
    # сообщения в базе есть, но у другого тикета — ни ошибки, ни строк
    await repository.save(message(ticket=inserted_ticket, sent_at=BASE_SENT_AT))
    await session.commit()

    assert await repository.find_undelivered_by_ticket_id(ticket_id=TicketId.generate()) == []


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
