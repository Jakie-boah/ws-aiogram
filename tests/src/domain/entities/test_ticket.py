import datetime

from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, TicketId
from faker import Faker

fake = Faker()


def test_ticket_open():
    client_id = ClientId(fake.pyint(min_value=1, max_value=1000))
    now = datetime.datetime.now(datetime.timezone.utc)
    ticket = Ticket.open(client_id=client_id, now=now)

    assert ticket.id is not None
    assert isinstance(ticket.id, TicketId)
    assert ticket.status.value == "open"
    assert ticket.client_id == client_id
    assert ticket.created_at == now
    assert ticket.last_activity_at == now

    assert ticket.closed_at is None
    assert ticket.admin_id is None
