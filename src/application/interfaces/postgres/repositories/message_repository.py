from src.application.interfaces.postgres.repositories.base import Repository

from typing import Protocol
from src.domain.values import MessageId
from src.domain.entities.message import Message


class PostgresMessageRepository(Repository[Message, MessageId], Protocol):
    ...
