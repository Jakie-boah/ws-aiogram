import datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.domain.entities.ticket import Ticket
from src.domain.values import AdminId, ClientId, TicketCloseReason, TicketId, TicketState, TicketStatus
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from src.infrastructure.postgres.tables import tickets_table
from src.application.interfaces.postgres.repositories.errors import EntityNotFoundError

ADMIN_ID = AdminId(1212)
CLIENT_A = ClientId(101)
CLIENT_B = ClientId(202)

ACTIVE_STATES = [
    TicketState.OPEN,
    TicketState.WAITING_ADMIN,
    TicketState.WAITING_CLIENT,
]


@pytest_asyncio.fixture(name="repository")
async def ticket_repository(session):
    return ImplPostgresTicketRepository(session)


def active_ticket(ticket, client_id, state=TicketState.OPEN):
    return ticket(
        uid=TicketId.generate(),
        client_id=client_id,
        status=TicketStatus(state),
    )


def closed_ticket(ticket, **overrides):
    entity = ticket(**{"uid": TicketId.generate(), **overrides})
    entity.assign_admin(admin_id=ADMIN_ID)
    entity.close(
        reason=TicketCloseReason.RESOLVED,
        now=datetime.datetime.now(datetime.timezone.utc),
    )
    return entity


async def fetch_rows(session, entity: Ticket):
    rows = await session.execute(
        select(tickets_table).where(tickets_table.c.id == entity.id.value)
    )
    return rows.mappings().all()


def assert_row_matches(row, entity: Ticket):
    assert row["id"] == entity.id.value
    assert row["client_id"] == entity.client_id.value
    assert row["status"] == entity.status.value
    assert row["created_at"] == entity.created_at
    assert row["last_activity_at"] == entity.last_activity_at
    assert row["closed_at"] == entity.closed_at
    assert row["close_reason"] == (
        entity.close_reason.value if entity.close_reason is not None else None
    )
    assert row["admin_id"] == (
        entity.admin_id.value if entity.admin_id is not None else None
    )


def assert_same_ticket(actual: Ticket, expected: Ticket):
    assert actual.id == expected.id
    assert actual.client_id == expected.client_id
    assert actual.status == expected.status
    assert actual.admin_id == expected.admin_id
    assert actual.created_at == expected.created_at
    assert actual.last_activity_at == expected.last_activity_at
    assert actual.closed_at == expected.closed_at
    assert actual.close_reason == expected.close_reason


@pytest.mark.asyncio
async def test_save_persists_every_column(repository, session, ticket):
    entity = ticket()

    await repository.save(entity)
    await session.commit()

    rows = await fetch_rows(session, entity)
    assert len(rows) == 1
    assert_row_matches(rows[0], entity)


@pytest.mark.asyncio
async def test_save_persists_closed_ticket_nullable_columns(repository, session, ticket):
    entity = closed_ticket(ticket)

    await repository.save(entity)
    await session.commit()

    rows = await fetch_rows(session, entity)
    assert len(rows) == 1
    assert_row_matches(rows[0], entity)


@pytest.mark.asyncio
async def test_upsert_updates_mutable_columns_in_place(repository, session, ticket):
    entity = ticket()
    await repository.save(entity)
    await session.commit()

    entity.assign_admin(admin_id=ADMIN_ID)
    entity.register_admin_message(now=datetime.datetime.now(datetime.timezone.utc))
    await repository.save(entity)
    await session.commit()

    rows = await fetch_rows(session, entity)
    assert len(rows) == 1
    assert rows[0]["admin_id"] == ADMIN_ID.value
    assert rows[0]["status"] == TicketState.WAITING_CLIENT
    assert rows[0]["last_activity_at"] == entity.last_activity_at


@pytest.mark.asyncio
async def test_upsert_fills_columns_that_were_null_on_insert(repository, session, ticket):
    entity = ticket()
    await repository.save(entity)
    await session.commit()

    entity.close(
        reason=TicketCloseReason.EXPIRED,
        now=datetime.datetime.now(datetime.timezone.utc),
    )
    await repository.save(entity)
    await session.commit()

    rows = await fetch_rows(session, entity)
    assert len(rows) == 1
    assert_row_matches(rows[0], entity)


@pytest.mark.asyncio
async def test_get_round_trips_open_ticket(repository, session, ticket):
    entity = ticket()
    await repository.save(entity)
    await session.commit()

    loaded = await repository.get(entity.id)

    assert isinstance(loaded, Ticket)
    assert_same_ticket(loaded, entity)


@pytest.mark.asyncio
async def test_get_round_trips_closed_ticket(repository, session, ticket):
    entity = closed_ticket(ticket)
    await repository.save(entity)
    await session.commit()

    loaded = await repository.get(entity.id)

    assert_same_ticket(loaded, entity)
    assert loaded.admin_id == ADMIN_ID
    assert loaded.close_reason == TicketCloseReason.RESOLVED
    assert loaded.closed_at is not None


@pytest.mark.asyncio
async def test_get_returns_utc_aware_datetimes(repository, session, ticket):
    entity = closed_ticket(ticket)
    await repository.save(entity)
    await session.commit()

    loaded = await repository.get(entity.id)

    for value in (loaded.created_at, loaded.last_activity_at, loaded.closed_at):
        assert value is not None
        assert value.utcoffset() == datetime.timedelta(0)


@pytest.mark.asyncio
async def test_get_returns_reusable_aggregate(repository, session, ticket):
    entity = ticket()
    await repository.save(entity)
    await session.commit()

    loaded = await repository.get(entity.id)
    loaded.assign_admin(admin_id=ADMIN_ID)
    loaded.register_admin_message(now=datetime.datetime.now(datetime.timezone.utc))
    await repository.save(loaded)
    await session.commit()

    reloaded = await repository.get(entity.id)
    assert_same_ticket(reloaded, loaded)


@pytest.mark.asyncio
async def test_get_raises_when_ticket_not_found(repository):
    with pytest.raises(EntityNotFoundError):
        await repository.get(TicketId.generate())


@pytest.mark.asyncio
async def test_find_active_returns_none_when_client_has_no_tickets(repository):
    assert await repository.find_active_by_client(CLIENT_A) is None


@pytest.mark.asyncio
async def test_find_active_round_trips_the_active_ticket(repository, session, ticket):
    entity = active_ticket(ticket, CLIENT_A)
    await repository.save(entity)
    await session.commit()

    found = await repository.find_active_by_client(CLIENT_A)

    assert found is not None
    assert_same_ticket(found, entity)


@pytest.mark.asyncio
@pytest.mark.parametrize("state", ACTIVE_STATES)
async def test_find_active_treats_every_non_closed_state_as_active(
    repository, session, ticket, state
):
    entity = active_ticket(ticket, CLIENT_A, state=state)
    await repository.save(entity)
    await session.commit()

    found = await repository.find_active_by_client(CLIENT_A)

    assert found is not None
    assert found.id == entity.id
    assert found.status == TicketStatus(state)


@pytest.mark.asyncio
async def test_find_active_ignores_closed_ticket(repository, session, ticket):
    await repository.save(closed_ticket(ticket, client_id=CLIENT_A))
    await session.commit()

    assert await repository.find_active_by_client(CLIENT_A) is None


@pytest.mark.asyncio
async def test_find_active_skips_history_and_returns_the_open_one(
    repository, session, ticket
):
    await repository.save(closed_ticket(ticket, client_id=CLIENT_A))
    await repository.save(closed_ticket(ticket, client_id=CLIENT_A))
    current = active_ticket(ticket, CLIENT_A)
    await repository.save(current)
    await session.commit()

    found = await repository.find_active_by_client(CLIENT_A)

    assert found is not None
    assert found.id == current.id


@pytest.mark.asyncio
async def test_find_active_tolerates_many_closed_tickets_for_one_client(
    repository, session, ticket
):
    for _ in range(3):
        await repository.save(closed_ticket(ticket, client_id=CLIENT_A))
    await session.commit()

    assert await repository.find_active_by_client(CLIENT_A) is None


@pytest.mark.asyncio
async def test_find_active_isolates_clients(repository, session, ticket):
    mine = active_ticket(ticket, CLIENT_A)
    theirs = active_ticket(ticket, CLIENT_B)
    await repository.save(mine)
    await repository.save(theirs)
    await session.commit()

    assert (await repository.find_active_by_client(CLIENT_A)).id == mine.id
    assert (await repository.find_active_by_client(CLIENT_B)).id == theirs.id


@pytest.mark.asyncio
async def test_second_active_ticket_for_one_client_is_rejected(
    repository, session, ticket
):
    await repository.save(active_ticket(ticket, CLIENT_A))
    await session.commit()

    with pytest.raises(IntegrityError):
        await repository.save(active_ticket(ticket, CLIENT_A))

    await session.rollback()


@pytest.mark.asyncio
async def test_find_active_ticket_by_client(repository, ticket, session):
    entity = ticket()
    await repository.save(entity)
    await session.commit()

    loaded = await repository.find_active_by_client(entity.client_id)
    assert loaded is not None

