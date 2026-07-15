from enum import StrEnum


class SenderType(StrEnum):
    CLIENT = "client"
    ADMIN = "admin"


class MessageType(StrEnum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"


class TicketCloseReason(StrEnum):
    RESOLVED = "resolved"
    EXPIRED = "expired"
