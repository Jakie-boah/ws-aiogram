from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ClientMessage:
    user_id: int
    text: str
