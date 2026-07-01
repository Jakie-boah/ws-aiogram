from src.domain.values import Text, UserId


class ClientMessage:

    def __init__(self, *, user_id: UserId, text: Text):
        self.user_id = user_id
        self.text = text

    def as_dict(self) -> dict:
        return {"user_id": self.user_id.value, "text": self.text.value}
