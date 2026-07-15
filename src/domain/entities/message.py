from src.domain.values import MessageId, Text, UserId, SenderType, MessageType, TicketId

from datetime import datetime
from src.domain.errors.entities import MessageAlreadyDeliveredError, MessageTimelineError, MessageValidationError


class Message:
    def __init__(
            self,
            *,
            uid: MessageId,
            ticket_id: TicketId,
            sender_id: UserId,
            sender_type: SenderType,
            message_type: MessageType,
            text: Text,
            sent_at: datetime,
            delivered_at: datetime | None = None,
            read_at: datetime | None = None
    ):
        self._uid = uid
        self._ticket_id = ticket_id
        self._sender_id = sender_id
        self._sender_type = sender_type

        self._message_type = message_type
        self._text = text
        self._validate_msg()

        self._sent_at = sent_at
        self._delivered_at = delivered_at
        self._read_at = read_at
        self._validate_dates()

    @property
    def id(self) -> MessageId:
        return self._uid

    @property
    def ticket_id(self) -> TicketId:
        return self._ticket_id

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

    def mark_delivered_at(self, now: datetime):
        if self._delivered_at is not None:
            raise MessageAlreadyDeliveredError(
                field="delivered_at",
                message="Message already delivered. Cannot set delivered_at again."
            )

        if now <= self._sent_at:
            raise MessageTimelineError(
                field="delivered_at",
                message=f"Cannot set delivered_at. delivered_at < sent_at - {now} < {self._sent_at}"
            )

        self._delivered_at = now

    def mark_read_at(self, now: datetime):
        if self._read_at is not None:
            return

        if self._delivered_at is None:
            self.mark_delivered_at(now)

        if now < self._delivered_at:
            raise MessageTimelineError(
                field="read_at",
                message=f"Cannot set read_at. read_at < delivered_at - {now} < {self._delivered_at}"
            )

        self._read_at = now

    @classmethod
    def new_message(
            cls,
            *,
            ticket_id: TicketId,
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
            message_type=message_type,
            ticket_id=ticket_id
        )

    def _validate_msg(self):
        if self._message_type == MessageType.TEXT and self._text is None:
            raise MessageValidationError(field="text", message="Text cannot be empty, when message type is TEXT.")

    def _validate_dates(self):
        if self._sent_at is None:
            raise MessageValidationError(field="sent_at", message="sent_at cannot be None.")

        if self._delivered_at is None:
            if self._read_at is not None:
                raise MessageValidationError(
                    field="delivered_at",
                    message="delivered_at cannot be None when read_at is set.",
                )
            return

        if self._read_at is None:
            if self._sent_at <= self._delivered_at:
                return

            raise MessageTimelineError(
                field="msg_timeline",
                message=f"Wrong timeline: sent_at <= delivered_at. "
                        f"{self._sent_at} <= {self._delivered_at}",
            )

        if self._sent_at < self._delivered_at <= self._read_at:
            return

        raise MessageTimelineError(
                field="msg_timeline",
                message=f"Wrong timeline. sent_at <= delivered_at <= read_at. "
                        f"{self._sent_at} < {self._delivered_at} <= {self._read_at}"
            )
