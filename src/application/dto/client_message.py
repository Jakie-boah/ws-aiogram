from dataclasses import dataclass
from src.domain.values import MessageType
from datetime import datetime


@dataclass(slots=True, frozen=True)
class ClientMessageDTO:
    user_id: int
    text: str


@dataclass(slots=True, frozen=True)
class ReceiveClientMessage:
    user_id: int
    text: str
    sent_at: datetime
    message_type: MessageType
