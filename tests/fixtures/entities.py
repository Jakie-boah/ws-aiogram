from src.domain.entities.ticket import Ticket

import pytest

from faker import Faker
import datetime
from src.domain.values import ClientId, TicketStatus, TicketState, TicketId

fake = Faker()

MINUTE = datetime.timedelta(minutes=1)
DAY = datetime.timedelta(days=1)


@pytest.fixture
def ticket():
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

    def __get_ticket(**overrides):
        return Ticket(**{**defaults, **overrides})

    return __get_ticket
