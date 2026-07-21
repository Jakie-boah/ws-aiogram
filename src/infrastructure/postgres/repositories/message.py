from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.postgres.repositories.errors import EntityNotFoundError
from src.application.interfaces.postgres.repositories.message_repository import PostgresMessageRepository
from src.domain.entities.message import Message
from src.domain.values import MessageId, TicketId
from src.infrastructure.postgres.repositories.mapper import map_message_entity_from_db
from src.infrastructure.postgres.tables import messages_table


class ImplPostgresMessageRepository(PostgresMessageRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: Message) -> None:
        stmt = pg_insert(messages_table).values(
            id=entity.id.value,
            ticket_id=entity.ticket_id.value,
            sender_id=entity.sender_id.value,
            sender_type=entity.sender_type.value,
            message_type=entity.message_type.value,
            text=entity.text.value if entity.text else None,
            sent_at=entity.sent_at,
            delivered_at=entity.delivered_at,
            read_at=entity.read_at
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "text": stmt.excluded.text,
                "delivered_at": stmt.excluded.delivered_at,
                "read_at": stmt.excluded.read_at,
            }
        )
        await self._session.execute(stmt)

    async def get(self, uid: MessageId) -> Message:
        rows = await self._session.execute(
            select(messages_table).where(messages_table.c.id == uid.value)
        )
        result = rows.mappings().one_or_none()

        if result is None:
            raise EntityNotFoundError(
                field="message_id",
                message=f"Message with id {uid.value} not found"
            )

        return map_message_entity_from_db(result)

    async def find_undelivered_by_ticket_id(self, *, ticket_id: TicketId) -> list[Message]:
        stmt = select(messages_table).where(
            (messages_table.c.ticket_id == ticket_id.value) &
            (messages_table.c.delivered_at.is_(None))
        ).order_by(messages_table.c.sent_at.asc())

        rows = await self._session.execute(stmt)
        result = rows.mappings().all()
        return [map_message_entity_from_db(row) for row in result] if result else []
