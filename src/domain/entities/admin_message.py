from src.domain.values import MessageId, Text


class AdminMessage:
    def __init__(self, *, message_id: MessageId, text: Text):
        self.message_id = message_id
        self.text = text

    def as_dict(self):
        return {
            "message_id": self.message_id.value,
            "text": self.text.value
        }
