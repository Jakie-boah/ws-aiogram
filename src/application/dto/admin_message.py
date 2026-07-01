from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdminMessageDTO:
    message_id: int
    text: str
