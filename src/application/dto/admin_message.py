from dataclasses import dataclass

from src.domain.values import MessageId, Text


@dataclass(frozen=True, slots=True)
class AdminMessageDTO:
    message_id: int
    text: str


@dataclass(frozen=True, slots=True)
class AdminMessage:
    message_id: MessageId
    text: Text

    @classmethod
    def from_dto(cls, dto: AdminMessageDTO) -> "AdminMessage":
        return AdminMessage(
            message_id=MessageId(dto.message_id),
            text=Text(dto.text)
        )


