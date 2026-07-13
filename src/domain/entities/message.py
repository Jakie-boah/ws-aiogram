from src.domain.values import MessageId, Text, UserId, SenderType, MessageType

from datetime import datetime


class Message:
    def __init__(
            self,
            *,
            uid: MessageId,
            sender_id: UserId,
            sender_type: SenderType,
            message_type: MessageType,
            text: Text,
            sent_at: datetime,
            delivered_at: datetime | None = None,
            read_at: datetime | None = None
    ):
        self._uid = uid
        self._sender_id = sender_id
        self._sender_type = sender_type
        self._message_type = message_type
        self._text = text
        self._sent_at = sent_at
        self._delivered_at = delivered_at
        self._read_at = read_at

    @property
    def id(self) -> MessageId:
        return self._uid

    @property
    def sender_id(self) -> UserId:
        return self._sender_id

    @property
    def sender_type(self) -> SenderType:
        return self._sender_type

    @property
    def text(self) -> Text:
        return self._text

    @property
    def sent_at(self) -> datetime:
        return self._sent_at

    @property
    def msg_type(self) -> MessageType:
        return self._message_type

    @property
    def delivered_at(self) -> datetime | None:
        return self._delivered_at

    @property
    def read_at(self) -> datetime | None:
        return self._read_at

    @classmethod
    def new_message(
            cls,
            *,
            sender_id: UserId,
            sender_type: SenderType,
            text: Text,
            sent_at: datetime,
            message_type: MessageType = MessageType.TEXT,

    ) -> "Message":
        return cls(
            uid=MessageId.generate(),
            sender_id=sender_id,
            sender_type=sender_type,
            text=text,
            sent_at=sent_at,
            message_type=message_type
        )
