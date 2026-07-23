from dataclasses import dataclass
from datetime import datetime
from src.domain.values import MessageType
from uuid import UUID


@dataclass(slots=True, frozen=True)
class MessageDTO:
    user_id: int
    text: str
    sent_at: datetime
    message_type: MessageType


@dataclass(slots=True, frozen=True)
class AdminMessageDTO(MessageDTO):
    ticket_id: UUID
