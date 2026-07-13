from typing import Protocol

from src.domain.values.numbers import MessageIdInt, UserId


class RedisStorage(Protocol):
    async def set(self, key: MessageIdInt, value: UserId) -> None:
        pass

    async def get(self, key: MessageIdInt) -> UserId:
        pass
