from src.domain.entities.ticket import Ticket
from sqlalchemy import RowMapping
from src.domain.values import AdminId, ClientId, TicketCloseReason, TicketId, TicketStatus, TicketState


def map_ticket_entity_from_db(row: RowMapping) -> Ticket:
    return Ticket(
        uid=TicketId(row.id),
        client_id=ClientId(row.client_id),
        status=TicketStatus(TicketState(row.status)),
        assigned_admin_id=AdminId(row.admin_id) if row.admin_id else None,
        created_at=row.created_at,
        last_activity_at=row.last_activity_at,
        closed_at=row.closed_at,
        close_reason=TicketCloseReason(row.close_reason) if row.close_reason else None,
    )
