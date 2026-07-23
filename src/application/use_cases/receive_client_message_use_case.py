import structlog
from src.application.interfaces.postgres.uow import UnitOfWork
from src.application.dto.client_message import ReceiveClientMessage
from src.domain.values import ClientId, SenderType, Text
from src.domain.entities.ticket import Ticket
from src.domain.entities.message import Message
from datetime import datetime
from src.application.interfaces.postgres.repositories.errors import ActiveTicketAlreadyExistsError


class ReceiveClientMessageUseCase:
    def __init__(self, logger: structlog.BoundLogger, uow: UnitOfWork):
        self._logger = logger
        self._uow = uow

    async def __call__(self, payload: ReceiveClientMessage):
        client_id = ClientId(payload.user_id)
        now = payload.sent_at
        text = Text(payload.text)

        active_ticket = await self._resolve_ticket(client_id=client_id, now=now)
        active_ticket.register_client_message(now)

        await self._uow.ticket.save(active_ticket)

        msg = Message.new_message(
            ticket_id=active_ticket.id,
            sender_id=client_id,
            sender_type=SenderType.CLIENT,
            text=text,
            sent_at=now,
            message_type=payload.message_type
        )
        await self._uow.message.save(msg)

        await self._uow.commit()

    async def _resolve_ticket(self, *, client_id: ClientId, now: datetime):
        existing = await self._uow.ticket.find_active_by_client(client_id)

        if existing is not None:
            return existing

        new_ticket = Ticket.open(client_id=client_id, now=now)

        try:
            async with self._uow.savepoint():
                await self._uow.ticket.save(new_ticket)

        except ActiveTicketAlreadyExistsError:
            winner = await self._uow.ticket.find_active_by_client(client_id)
            if winner is None:
                raise

            self._logger.info(f"ticket race lost, joined existing ticket client_id = {client_id.value}")
            return winner

        return new_ticket
