from sqlalchemy import (
    TIMESTAMP,
    UUID,
    BigInteger,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    text,
)

from src.domain.values import MessageType, SenderType, TicketCloseReason, TicketState


metadata = MetaData()


def _enum_values(enum_cls) -> str:
    return "(" + ", ".join(f"'{m.value}'" for m in enum_cls) + ")"


tickets_table = Table(
    "tickets", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("status", String(20), nullable=False),
    Column("client_id", BigInteger, nullable=False),
    Column("created_at", TIMESTAMP(timezone=True), nullable=False),
    Column("last_activity_at", TIMESTAMP(timezone=True), nullable=False),
    Column("closed_at", TIMESTAMP(timezone=True), nullable=True),
    Column("close_reason", String(20), nullable=True),
    Column("admin_id", BigInteger, nullable=True),

    Index(
        "uq_tickets_active_per_client",
        "client_id",
        unique=True,
        postgresql_where=text("status <> 'closed'")
    ),

    CheckConstraint(f"status IN {_enum_values(TicketState)}", name="status_check"),
    CheckConstraint(f"close_reason IN {_enum_values(TicketCloseReason)}", name="close_reason_check"),
    CheckConstraint(
        "created_at <= last_activity_at",
        name="timeline",
    ),
    CheckConstraint(
        "closed_at IS NULL OR last_activity_at <= closed_at",
        name="closed_timeline",
    ),
    CheckConstraint(
        "(status = 'closed') = (closed_at IS NOT NULL)",
        name="closed_at_consistency",
    ),
    CheckConstraint(
        "(status = 'closed') = (close_reason IS NOT NULL)",
        name="close_reason_consistency",
    ),
)

messages_table = Table(
    "messages", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("ticket_id", ForeignKey("tickets.id"), nullable=False),
    Column("sender_id", BigInteger, nullable=False),
    Column("sender_type", String(20), nullable=False),
    Column("message_type", String(20), nullable=False),
    Column("text", String, nullable=True),

    Column("sent_at", TIMESTAMP(timezone=True), nullable=False),
    Column("delivered_at", TIMESTAMP(timezone=True), nullable=True),
    Column("read_at", TIMESTAMP(timezone=True), nullable=True),

    CheckConstraint(f"sender_type IN {_enum_values(SenderType)}", name="sender_check"),
    CheckConstraint(f"message_type IN {_enum_values(MessageType)}", name="message_type_check"),

    CheckConstraint(
        "delivered_at IS NULL OR sent_at < delivered_at",
        name="delivered_at_consistency",
    ),

    CheckConstraint(
        "read_at IS NULL OR delivered_at <= read_at",
        name="read_at_consistency",
    ),

    Index(
        "ix_messages_undelivered",
        "ticket_id",
        postgresql_where=text("delivered_at IS NULL"),
    )

)
