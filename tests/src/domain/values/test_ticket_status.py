import pytest

from src.domain.values.ticket_status import TicketStatus, TicketState
import src.domain.errors as errors


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
    # self-loop: уже ждём админа, второе сообщение клиента ничего не меняет
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    assert ts.on_client_message().value == TicketState.WAITING_ADMIN


def test_client_message_from_waiting_client_moves_to_waiting_admin():
    # реальный переход: мяч был у клиента, он ответил — теперь ждём админа
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    assert ts.on_client_message().value == TicketState.WAITING_ADMIN


def test_client_message_from_closed_raises():
    # closed терминальный — клетки нет, любое событие запрещено
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_client_message()


def test_on_client_message_returns_new_instance():
    # иммутабельность: исходный статус не мутируется, рождается новый инстанс
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    new_ts = ts.on_client_message()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_CLIENT


# --- on_admin_reply: событие "админ ответил" по всем клеткам матрицы ---


def test_admin_reply_from_open_waits_client():
    # реальный переход: админ впервые ответил на свежий тикет — мяч уходит к клиенту
    ts = TicketStatus(TicketState.OPEN)

    assert ts.on_admin_reply().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_waiting_admin_moves_to_waiting_client():
    # реальный переход: ждали админа, он ответил — теперь ждём клиента
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    assert ts.on_admin_reply().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_waiting_client_stays_waiting_client():
    # self-loop: мяч уже у клиента, второй ответ админа ничего не меняет
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    assert ts.on_admin_reply().value == TicketState.WAITING_CLIENT


def test_admin_reply_from_closed_raises():
    # closed терминальный — клетки нет, событие запрещено
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_admin_reply()


def test_on_admin_reply_returns_new_instance():
    # иммутабельность: исходный статус не мутируется
    ts = TicketStatus(TicketState.WAITING_ADMIN)

    new_ts = ts.on_admin_reply()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_ADMIN


# --- on_close: событие "закрыли" по всем клеткам матрицы ---


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
    # terminality: уже закрытый тикет закрыть повторно нельзя — не полутерминальный
    with pytest.raises(errors.IllegalTicketTransition):
        TicketStatus(TicketState.CLOSED).on_close()


def test_on_close_returns_new_instance():
    # иммутабельность: исходный статус не мутируется
    ts = TicketStatus(TicketState.WAITING_CLIENT)

    new_ts = ts.on_close()

    assert new_ts is not ts
    assert ts.value == TicketState.WAITING_CLIENT
