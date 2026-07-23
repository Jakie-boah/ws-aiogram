from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AdminMessageDTOV0:
    message_id: int
    text: str
