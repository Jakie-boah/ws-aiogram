from src.application.dto.client_message import ClientMessageDTO
from src.domain.entities.client_message import ClientMessage
from src.domain.entities.admin_message import AdminMessage
from src.application.dto.admin_message import AdminMessageDTO
from src.domain.values import Text, UserId, MessageId


def map_client_message_from_dto(payload: ClientMessageDTO) -> ClientMessage:
    return ClientMessage(
        user_id=UserId(payload.user_id),
        text=Text(payload.text),
    )


def map_admin_message_from_dto(payload: AdminMessageDTO):
    return AdminMessage(
        message_id=MessageId(payload.message_id),
        text=Text(payload.text)
    )
