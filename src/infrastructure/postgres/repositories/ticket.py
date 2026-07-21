from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.postgres.repositories.errors import ActiveTicketAlreadyExistsError, EntityNotFoundError
from src.application.interfaces.postgres.repositories.ticket_repository import PostgresTicketRepository
from src.domain.entities.ticket import Ticket
from src.domain.values import ClientId, TicketId, TicketState
from src.infrastructure.postgres.repositories.mapper import map_ticket_entity_from_db
from src.infrastructure.postgres.tables import tickets_table


class ImplPostgresTicketRepository(PostgresTicketRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entity: Ticket) -> None:
        stmt = pg_insert(tickets_table).values(
            id=entity.id.value,
            status=entity.status.value,
            client_id=entity.client_id.value,
            created_at=entity.created_at,
            last_activity_at=entity.last_activity_at,
            closed_at=entity.closed_at,
            close_reason=entity.close_reason.value if entity.close_reason else None,
            admin_id=entity.admin_id.value if entity.admin_id else None,
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "status": stmt.excluded.status,
                "last_activity_at": stmt.excluded.last_activity_at,
                "closed_at": stmt.excluded.closed_at,
                "close_reason": stmt.excluded.close_reason,
                "admin_id": stmt.excluded.admin_id,
            },
        )

        try:
            await self._session.execute(stmt)

        except IntegrityError as exc:
            if exc.orig.__cause__.constraint_name == "uq_tickets_active_per_client":
                raise ActiveTicketAlreadyExistsError(
                    field="ticket", message="Active ticket for this client already exists"
                )
            raise IntegrityError from exc

    async def get(self, uid: TicketId) -> Ticket:
        rows = await self._session.execute(
            select(tickets_table).where(tickets_table.c.id == uid.value)
        )
        result = rows.mappings().first()

        if result is None:
            raise EntityNotFoundError(
                field="id", message=f"Ticket with id {uid.value} not found"
            )

        return map_ticket_entity_from_db(result)

    async def find_active_by_client(self, client_id: ClientId) -> Ticket | None:
        rows = await self._session.execute(
            select(tickets_table).where(
                (tickets_table.c.client_id == client_id.value) &
                (tickets_table.c.status != TicketState.CLOSED)
            )
        )
        result = rows.mappings().one_or_none()
        return map_ticket_entity_from_db(result) if result else None
