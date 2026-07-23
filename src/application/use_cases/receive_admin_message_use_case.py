import structlog
from src.application.dto.message import AdminMessageDTO
from src.application.interfaces.postgres.uow import UnitOfWork
from src.domain.values import TicketId, AdminId, SenderType, Text
from src.domain.entities.message import Message
from src.application.interfaces.use_cases.base import AnotherAdminAlreadyAssignedError
from src.application.interfaces.broker.publisher import BrokerPublisher


class ReceiveAdminMessageUseCase:
    def __init__(self, logger: structlog.BoundLogger, uow: UnitOfWork, publisher: BrokerPublisher):
        self._logger = logger
        self._uow = uow
        self._publisher = publisher

    async def __call__(self, payload: AdminMessageDTO):
        ticket_id = TicketId(payload.ticket_id)
        admin_id = AdminId(payload.user_id)
        text = Text(payload.text)

        ticket = await self._uow.ticket.get(uid=ticket_id)

        if ticket.admin_id is None:
            ticket.assign_admin(admin_id)

        else:
            if ticket.admin_id != admin_id:
                raise AnotherAdminAlreadyAssignedError(
                    field="Another admin already assigned to this ticket",
                    message=f"This ticket is already assigned to another admin: {ticket.admin_id}",
                )

        ticket.register_admin_message(payload.sent_at)

        await self._uow.ticket.save(ticket)

        msg = Message.new_message(
            ticket_id=ticket_id,
            sender_id=admin_id,
            sender_type=SenderType.ADMIN,
            text=text,
            sent_at=payload.sent_at,
            message_type=payload.message_type,
        )

        await self._uow.message.save(msg)

        await self._uow.commit()
