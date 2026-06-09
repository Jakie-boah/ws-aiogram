from typing import Protocol

from src.domain.values.numbers import MessageId, UserId


class RedisStorage(Protocol):
    async def set(self, key: MessageId, value: UserId) -> None:
        pass

    async def get(self, key: MessageId) -> UserId:
        pass
