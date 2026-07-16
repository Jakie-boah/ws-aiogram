import datetime

import pytest
from faker import Faker
from zoneinfo import ZoneInfo

from src.domain.entities.message import Message
from src.domain.values import UserId, SenderType, Text, MessageType, TicketId
from src.domain.errors.entities import MessageAlreadyDeliveredError, MessageTimelineError, MessageValidationError

fake = Faker()

SECOND = datetime.timedelta(seconds=1)
MINUTE = datetime.timedelta(minutes=1)
DAY = datetime.timedelta(days=1)


@pytest.fixture
def message() -> Message:
    return Message.new_message(
        sender_id=UserId(fake.pyint(min_value=1, max_value=1_000_000)),
        sender_type=SenderType.CLIENT,
        text=Text(fake.text()),
        sent_at=fake.date_time(ZoneInfo("Europe/Moscow")),
        ticket_id=TicketId.generate(),
    )


def test_new_message_creates_pending_message():
    user_id = UserId(fake.pyint(min_value=1, max_value=1_000_000))
    text = Text(fake.text())
    now = fake.date_time(ZoneInfo("Europe/Moscow"))
    ticket_id = TicketId.generate()

    message = Message.new_message(
        sender_id=user_id,
        sender_type=SenderType.CLIENT,
        text=text,
        sent_at=now,
        ticket_id=ticket_id,
    )

    assert message.id is not None
    assert message.ticket_id == ticket_id
    assert message.sender_id == user_id
    assert message.sender_type == SenderType.CLIENT
    assert message.text == text
    assert message.sent_at == now
    assert message.message_type == MessageType.TEXT

    assert message.delivered_at is None
    assert message.read_at is None


def test_mark_delivered_after_sent(message):
    delivered_at = message.sent_at + MINUTE

    message.mark_delivered_at(delivered_at)

    assert message.delivered_at == delivered_at


def test_mark_delivered_equal_to_sent_is_not_allowed(message):
    delivered_at = message.sent_at
    with pytest.raises(MessageTimelineError):
        message.mark_delivered_at(delivered_at)


def test_mark_delivered_before_sent_raises(message):
    delivered_at = message.sent_at - DAY

    with pytest.raises(MessageTimelineError):
        message.mark_delivered_at(delivered_at)

    assert message.delivered_at is None


def test_mark_delivered_twice_raises(message):
    delivered_at = message.sent_at + MINUTE
    message.mark_delivered_at(delivered_at)

    with pytest.raises(MessageAlreadyDeliveredError):
        message.mark_delivered_at(delivered_at + MINUTE)

    assert message.delivered_at == delivered_at


def test_mark_read_when_already_delivered(message):
    delivered_at = message.sent_at + MINUTE
    read_at = delivered_at + MINUTE
    message.mark_delivered_at(delivered_at)

    message.mark_read_at(read_at)

    assert message.read_at == read_at
    assert message.delivered_at == delivered_at


def test_mark_read_auto_delivers_when_not_delivered(message):
    read_at = message.sent_at + MINUTE

    message.mark_read_at(read_at)

    assert message.read_at == read_at
    assert message.delivered_at == read_at


def test_mark_read_equal_to_delivered_is_allowed(message):
    delivered_at = message.sent_at + MINUTE
    message.mark_delivered_at(delivered_at)

    message.mark_read_at(delivered_at)

    assert message.read_at == delivered_at


def test_mark_read_before_delivered_raises(message):
    delivered_at = message.sent_at + MINUTE
    message.mark_delivered_at(delivered_at)

    with pytest.raises(MessageTimelineError):
        message.mark_read_at(delivered_at - SECOND)

    assert message.read_at is None


def test_mark_read_before_sent_raises_and_leaves_marks_none(message):
    read_at = message.sent_at - DAY

    with pytest.raises(MessageTimelineError):
        message.mark_read_at(read_at)

    assert message.delivered_at is None
    assert message.read_at is None


def test_mark_read_is_idempotent(message):
    first_read = message.sent_at + MINUTE
    message.mark_read_at(first_read)

    message.mark_read_at(first_read + DAY)

    assert message.read_at == first_read
    assert message.delivered_at == first_read


def test_message_validate_raise_error_no_text():
    with pytest.raises(MessageValidationError):
        Message.new_message(
            sender_id=UserId(fake.pyint(min_value=1, max_value=1_000_000)),
            sender_type=SenderType.CLIENT,
            text=None,
            sent_at=fake.date_time(ZoneInfo("Europe/Moscow")),
            ticket_id=TicketId.generate(),
        )
