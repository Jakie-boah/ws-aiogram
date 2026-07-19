import datetime
import pytest
from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, TicketId, TicketCloseReason
from faker import Faker
from src.domain.values.ticket_status import TicketState
from src.domain.values import AdminId, TicketStatus
from src.domain.errors.entities.ticket import (
    AdminAlreadyAssignedError,
    AdminIsNotAssignedError,
    TicketIsClosedError,
    TicketTimelineError,
    TicketValidationError,
)

fake = Faker()

MINUTE = datetime.timedelta(minutes=1)
DAY = datetime.timedelta(days=1)

NOT_CLOSED_STATES = [TicketState.OPEN, TicketState.WAITING_ADMIN, TicketState.WAITING_CLIENT]


def make_ticket(**overrides) -> Ticket:
    """Регидрация через __init__. По умолчанию — валидный открытый тикет."""
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY
    defaults = dict(
        uid=TicketId.generate(),
        client_id=ClientId(fake.pyint(min_value=1, max_value=1000)),
        status=TicketStatus(TicketState.OPEN),
        created_at=created_at,
        last_activity_at=created_at + MINUTE,
        closed_at=None,
        close_reason=None,
    )
    return Ticket(**{**defaults, **overrides})


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


# --- регидрация: консистентность __init__ ---


def test_rehydrate_open_ticket(ticket):
    ticket = ticket()

    assert ticket.status.value == TicketState.OPEN
    assert ticket.closed_at is None
    assert ticket.close_reason is None


def test_rehydrate_created_equal_last_activity_is_allowed(ticket):
    now = datetime.datetime.now(datetime.timezone.utc)

    ticket = ticket(created_at=now, last_activity_at=now)

    assert ticket.created_at == ticket.last_activity_at


def test_rehydrate_closed_ticket_preserves_close_reason(ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY
    closed_at = created_at + MINUTE

    ticket = ticket(
        status=TicketStatus(TicketState.CLOSED),
        created_at=created_at,
        last_activity_at=closed_at,
        closed_at=closed_at,
        close_reason=TicketCloseReason.EXPIRED,
    )

    assert ticket.status.value == TicketState.CLOSED
    assert ticket.closed_at == closed_at
    assert ticket.close_reason == TicketCloseReason.EXPIRED


def test_rehydrate_closed_with_activity_before_closed_at_is_allowed(ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY
    closed_at = created_at + DAY

    ticket = ticket(
        status=TicketStatus(TicketState.CLOSED),
        created_at=created_at,
        last_activity_at=created_at + MINUTE,
        closed_at=closed_at,
        close_reason=TicketCloseReason.RESOLVED,
    )

    assert ticket.last_activity_at < ticket.closed_at


def test_rehydrate_last_activity_before_created_raises(ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc)

    with pytest.raises(TicketTimelineError):
        ticket(created_at=created_at, last_activity_at=created_at - MINUTE)


def test_rehydrate_closed_with_last_activity_before_created_raises(ticket):
    """Универсальная проверка created <= last_activity должна работать и в closed-ветке."""
    created_at = datetime.datetime.now(datetime.timezone.utc)
    closed_at = created_at + DAY

    with pytest.raises(TicketTimelineError):
        ticket(
            status=TicketStatus(TicketState.CLOSED),
            created_at=created_at,
            last_activity_at=created_at - MINUTE,
            closed_at=closed_at,
            close_reason=TicketCloseReason.RESOLVED,
        )


def test_rehydrate_closed_without_closed_at_raises(ticket):
    with pytest.raises(TicketValidationError):
        ticket(
            status=TicketStatus(TicketState.CLOSED),
            closed_at=None,
            close_reason=TicketCloseReason.RESOLVED,
        )


def test_rehydrate_closed_without_close_reason_raises(ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY

    with pytest.raises(TicketValidationError):
        ticket(
            status=TicketStatus(TicketState.CLOSED),
            created_at=created_at,
            last_activity_at=created_at + MINUTE,
            closed_at=created_at + DAY,
            close_reason=None,
        )


def test_rehydrate_closed_with_activity_after_closed_at_raises(ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY
    closed_at = created_at + MINUTE

    with pytest.raises(TicketTimelineError):
        ticket(
            status=TicketStatus(TicketState.CLOSED),
            created_at=created_at,
            last_activity_at=closed_at + MINUTE,
            closed_at=closed_at,
            close_reason=TicketCloseReason.RESOLVED,
        )


@pytest.mark.parametrize("state", NOT_CLOSED_STATES)
def test_rehydrate_not_closed_with_closed_at_raises(state, ticket):
    created_at = datetime.datetime.now(datetime.timezone.utc) - DAY

    with pytest.raises(TicketValidationError):
        ticket(
            status=TicketStatus(state),
            created_at=created_at,
            last_activity_at=created_at + MINUTE,
            closed_at=created_at + DAY,
            close_reason=None,
        )


@pytest.mark.parametrize("state", NOT_CLOSED_STATES)
def test_rehydrate_not_closed_with_close_reason_raises(state, ticket):
    with pytest.raises(TicketValidationError):
        ticket(
            status=TicketStatus(state),
            closed_at=None,
            close_reason=TicketCloseReason.RESOLVED,
        )


def test_closed_ticket_round_trips_through_rehydration(open_ticket):
    """Что произвёл close(), то __init__ обязан принять — фабрика и валидатор не должны расходиться."""
    now = datetime.datetime.now(datetime.timezone.utc)
    open_ticket.close(reason=TicketCloseReason.RESOLVED, now=now)

    rehydrated = Ticket(
        uid=open_ticket.id,
        client_id=open_ticket.client_id,
        status=open_ticket.status,
        assigned_admin_id=open_ticket.admin_id,
        created_at=open_ticket.created_at,
        last_activity_at=open_ticket.last_activity_at,
        closed_at=open_ticket.closed_at,
        close_reason=open_ticket.close_reason,
    )

    assert rehydrated.status.value == TicketState.CLOSED
    assert rehydrated.closed_at == now
    assert rehydrated.close_reason == TicketCloseReason.RESOLVED
    assert rehydrated.last_activity_at == now
