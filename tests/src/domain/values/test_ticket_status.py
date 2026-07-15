import pytest

from src.domain.values.ticket_status import (
    TicketStatus,
    TicketState,
)
from src.domain.errors import values as errors


def test_initial():
    ts = TicketStatus.initial()

    assert ts.value == TicketState.OPEN


def test_validation_raise():
    with pytest.raises(errors.TicketStatusValidationError):
        TicketStatus("INVALID_STATUS")


def test_client_message_from_open_stays_open():
    ts = TicketStatus(TicketState.OPEN)

    assert ts.on_client_message().value == TicketState.OPEN


def test_client_message_from_waiting_admin_stays_waiting_admin():
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    assert ts.on_client_message().value == TicketState.WAITING_ADMIN


def test_client_message_from_waiting_client_moves_to_waiting_admin():
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    assert ts.on_client_message().value == TicketState.WAITING_ADMIN


def test_client_message_from_closed_raises():
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_client_message()


def test_on_client_message_returns_new_instance():
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    new_ts = ts.on_client_message()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_CLIENT


def test_admin_reply_from_open_waits_client():
    ts = TicketStatus(TicketState.OPEN)

    assert ts.on_admin_message().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_waiting_admin_moves_to_waiting_client():
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    assert ts.on_admin_message().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_waiting_client_stays_waiting_client():
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    assert ts.on_admin_message().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_closed_raises():
    # closed терминальный — клетки нет, событие запрещено
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_admin_message()


def test_on_admin_reply_returns_new_instance():
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    new_ts = ts.on_admin_message()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_ADMIN


def test_close_from_open_moves_to_closed():
    # закрыть можно из любого живого статуса
    ts = TicketStatus(TicketState.OPEN)

    assert ts.on_close().value == TicketState.CLOSED


def test_close_from_waiting_admin_moves_to_closed():
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    assert ts.on_close().value == TicketState.CLOSED


def test_close_from_waiting_client_moves_to_closed():
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    assert ts.on_close().value == TicketState.CLOSED


def test_close_from_closed_raises():
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_close()


def test_on_close_returns_new_instance():
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    new_ts = ts.on_close()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_CLIENT
