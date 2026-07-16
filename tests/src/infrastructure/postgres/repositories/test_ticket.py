import pytest
import pytest_asyncio
from src.infrastructure.postgres.repositories.ticket import ImplPostgresTicketRepository
from sqlalchemy import select
from src.infrastructure.postgres.tables import tickets_table
from src.domain.values import AdminId


@pytest_asyncio.fixture(name="repository")
async def ticket_repository(session):
    return ImplPostgresTicketRepository(session)


@pytest.mark.asyncio
async def test_save(repository, session, ticket):
    ticket = ticket()

    await repository.save(ticket)
    await session.commit()

    rows = await session.execute(select(tickets_table).where(
        tickets_table.c.id == ticket.id.value
    ))

    result = rows.mappings().first()
    assert result is not None
    assert result["client_id"] == ticket.client_id.value


@pytest.mark.asyncio
async def test_upsert(repository, session, ticket):
    ticket = ticket()

    await repository.save(ticket)
    await session.commit()

    admin_id = AdminId(1212)

    ticket.assign_admin(admin_id=admin_id)
    await repository.save(ticket)
    await session.commit()

    rows = await session.execute(select(tickets_table).where(
        tickets_table.c.id == ticket.id.value
    ))
    result = rows.mappings().first()

    assert result["admin_id"] == ticket.admin_id.value


@pytest.mark.asyncio
async def test_get(repository):
    raise NotImplementedError
