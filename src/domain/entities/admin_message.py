from src.domain.values import MessageIdInt, Text


class AdminMessage:
    def __init__(self, *, message_id: MessageIdInt, text: Text):
        self.message_id = message_id
        self.text = text

    def as_dict(self):
        return {
            "message_id": self.message_id.value,
            "text": self.text.value
        }
