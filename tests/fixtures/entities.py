from src.domain.entities.ticket import Ticket
from src.domain.entities.message import Message

import pytest

from faker import Faker
import datetime
from src.domain.values import ClientId, TicketStatus, TicketState, TicketId, UserId, SenderType, Text
from zoneinfo import ZoneInfo

fake = Faker()

MINUTE = datetime.timedelta(minutes=1)
DAY = datetime.timedelta(days=1)


@pytest.fixture
def ticket():
    def __get_ticket(**overrides):
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

    return __get_ticket


@pytest.fixture
def message():
    def __get_message(*, ticket, **overrides):
        defaults = dict(
            sender_id=UserId(fake.pyint(min_value=1, max_value=1_000_000)),
            sender_type=SenderType.CLIENT,
            text=Text(fake.text()),
            sent_at=fake.date_time(ZoneInfo("Europe/Moscow")),
        )

        return Message.new_message(
            **{**defaults, **overrides},
            ticket_id=ticket.id,
        )

    return __get_message
