from dataclasses import dataclass

from src.domain.values import MessageId, Text


@dataclass(slots=True, frozen=True)
class AdminMessage:
    text: Text
    client_message_id: MessageId


@dataclass(slots=True, frozen=True)
class AdminReply:
    text: str
    user_id: int
