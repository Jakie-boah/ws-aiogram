from dataclasses import dataclass
from src.domain.values import UserId, Text


@dataclass(slots=True, frozen=True)
class ClientMessageDTO:
    user_id: int
    text: str


@dataclass(slots=True, frozen=True)
class ClientMessage:
    user_id: UserId
    text: Text

    @classmethod
    def from_dto(cls, dto: ClientMessageDTO) -> "ClientMessage":
        return ClientMessage(
            user_id=UserId(dto.user_id),
            text=Text(dto.text),
        )

    def as_dict(self) -> dict:
        return {"user_id": self.user_id.value, "text": self.text.value}
