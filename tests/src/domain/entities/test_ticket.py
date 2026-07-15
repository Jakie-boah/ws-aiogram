import datetime
import pytest
from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, TicketId, TicketCloseReason
from faker import Faker
from src.domain.values.ticket_status import TicketState
from src.domain.values import AdminId, TicketStatus
from src.domain.errors.entities.ticket import AdminAlreadyAssignedError, TicketIsClosedError, AdminIsNotAssignedError

fake = Faker()


def test_ticket_open():
    client_id = ClientId(fake.pyint(min_value=1, max_value=1000))
    now = datetime.datetime.now(datetime.timezone.utc)
    ticket = Ticket.open(client_id=client_id, now=now)

    assert ticket.id is not None
    assert isinstance(ticket.id, TicketId)
    assert ticket.status.value == TicketState.OPEN
    assert ticket.client_id == client_id
    assert ticket.created_at == now
    assert ticket.last_activity_at == now

    assert ticket.closed_at is None
    assert ticket.close_reason is None
    assert ticket.admin_id is None


@pytest.fixture()
def open_ticket() -> Ticket:
    client_id = ClientId(fake.pyint(min_value=1, max_value=1000))
    now = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)

    return Ticket.open(
        client_id=client_id,
        now=now
    )


def test_register_client_message(open_ticket):
    now = datetime.datetime.now(datetime.timezone.utc)
    open_ticket.register_client_message(now)

    assert open_ticket.status.value == TicketState.OPEN
    assert open_ticket.last_activity_at is not None
    assert open_ticket.last_activity_at == now


def test_register_client_message_when_closed(open_ticket):
    open_ticket._status = TicketStatus(TicketState.CLOSED)

    with pytest.raises(TicketIsClosedError):
        now = datetime.datetime.now(datetime.timezone.utc)
        open_ticket.register_client_message(now)


def test_assign_admin(open_ticket):
    admin_id = AdminId(fake.pyint(min_value=1, max_value=1000))

    open_ticket.assign_admin(admin_id)
    assert open_ticket.admin_id == admin_id

    with pytest.raises(AdminAlreadyAssignedError):
        open_ticket.assign_admin(admin_id)


def test_assign_admin_when_closed(open_ticket):
    open_ticket._status = TicketStatus(TicketState.CLOSED)
    with pytest.raises(TicketIsClosedError):
        admin_id = AdminId(fake.pyint(min_value=1, max_value=1000))
        open_ticket.assign_admin(admin_id)


def test_register_admin_message_when_closed(open_ticket):
    open_ticket._status = TicketStatus(TicketState.CLOSED)

    with pytest.raises(TicketIsClosedError):
        now = datetime.datetime.now(datetime.timezone.utc)
        open_ticket.register_admin_message(now)


def test_register_admin_message(open_ticket):
    now = datetime.datetime.now(datetime.timezone.utc)

    with pytest.raises(AdminIsNotAssignedError):
        open_ticket.register_admin_message(now)

    admin_id = AdminId(fake.pyint(min_value=1, max_value=1000))
    open_ticket.assign_admin(admin_id)

    open_ticket.register_admin_message(now)


def test_close(open_ticket):
    now = datetime.datetime.now(datetime.timezone.utc)

    open_ticket.close(
        reason=TicketCloseReason.RESOLVED, now=now
    )

    assert open_ticket.status.value == TicketState.CLOSED
    assert open_ticket.closed_at == now
    assert open_ticket.close_reason.value == TicketCloseReason.RESOLVED.value
    assert open_ticket.last_activity_at == now


def test_close_when_closed(open_ticket):
    open_ticket._status = TicketStatus(TicketState.CLOSED)

    with pytest.raises(TicketIsClosedError):
        open_ticket.close(reason=TicketCloseReason.RESOLVED, now=datetime.datetime.now(datetime.timezone.utc))
