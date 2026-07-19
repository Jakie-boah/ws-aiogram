from src.domain.entities.ticket import Ticket
from src.domain.entities.message import Message
from sqlalchemy import RowMapping
from src.domain.values import MessageId, UserId, AdminId, ClientId, TicketCloseReason, TicketId, TicketStatus, \
    TicketState, SenderType, Text, MessageType


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


def map_message_entity_from_db(row: RowMapping) -> Message:
    return Message(
        uid=MessageId(row.id),
        ticket_id=TicketId(row.ticket_id),
        sender_id=UserId(row.sender_id),
        sender_type=SenderType(row.sender_type),
        message_type=MessageType(row.message_type),
        text=Text(row.text) if row.text else None,
        sent_at=row.sent_at,
        delivered_at=row.delivered_at,
        read_at=row.read_at,
    )
