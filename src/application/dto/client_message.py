from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ClientMessageDTO:
    user_id: int
    text: str


