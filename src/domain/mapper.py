from src.application.dto.client_message import ClientMessageDTO
from src.domain.entities.client_message import ClientMessage
from src.domain.values import Text, UserId


def map_client_message_from_dto(payload: ClientMessageDTO) -> ClientMessage:
    return ClientMessage(
        user_id=UserId(payload.user_id),
        text=Text(payload.text),
    )
