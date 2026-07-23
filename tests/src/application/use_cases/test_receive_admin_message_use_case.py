import datetime

import pytest
import pytest_asyncio
from src.domain.values import MessageType

from src.application.use_cases.receive_admin_message_use_case import ReceiveAdminMessageUseCase
from src.application.dto.message import AdminMessageDTO
from faker import Faker
from src.application.interfaces.postgres.uow import UnitOfWork
from src.domain.entities.ticket import Ticket
from src.infrastructure.postgres.tables import messages_table
from sqlalchemy import select
from src.domain.values import TicketId, TicketStatus, TicketState, AdminId
from zoneinfo import ZoneInfo
from src.application.interfaces.use_cases.base import AnotherAdminAlreadyAssignedError

fake = Faker()


@pytest_asyncio.fixture
async def use_case(container):
    return await container.get(ReceiveAdminMessageUseCase)


@pytest_asyncio.fixture
async def inserted_ticket(uow: UnitOfWork, ticket) -> Ticket:
    ticket = ticket()
    await uow.ticket.save(ticket)
    await uow.commit()
    return ticket


@pytest.fixture
def dto(inserted_ticket) -> AdminMessageDTO:
    return AdminMessageDTO(
        user_id=fake.pyint(min_value=1, max_value=100000),
        text=fake.text(max_nb_chars=200),
        sent_at=datetime.datetime.now(ZoneInfo("UTC")),
        message_type=MessageType.TEXT,
        ticket_id=inserted_ticket.id.value
    )


@pytest.mark.asyncio
async def test_use_case(use_case, dto, uow, session):
    await use_case(dto)

    rows = await session.execute(select(messages_table).where(messages_table.c.ticket_id == dto.ticket_id))
    msg = rows.mappings().one_or_none()

    assert msg is not None
    assert msg.sender_id == dto.user_id
    assert msg.text == dto.text
    assert msg.message_type == dto.message_type.value

    ticket = await uow.ticket.get(TicketId(dto.ticket_id))

    assert ticket.admin_id is not None
    assert ticket.status == TicketStatus(TicketState.WAITING_CLIENT)
    assert ticket.last_activity_at == dto.sent_at


@pytest.mark.asyncio
async def test_use_case_another_admin_already_assigned(use_case, dto, uow):
    ticket = await uow.ticket.get(TicketId(dto.ticket_id))
    ticket.assign_admin(AdminId(dto.user_id + 1))
    await uow.ticket.save(ticket)
    await uow.commit()

    with pytest.raises(AnotherAdminAlreadyAssignedError):
        await use_case(dto)
