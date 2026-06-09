from redis.asyncio.client import Redis

from src.application.interfaces.redis.storage import RedisStorage
from src.domain.values import MessageId, UserId
from src.infrastructure.redis.errors import RedisKeyNotFoundError


class ImplRedisStorage(RedisStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: MessageId, value: UserId) -> None:
        await self.redis.set(str(key.value), str(value.value))

    async def get(self, key: MessageId) -> UserId:
        result = await self.redis.get(str(key.value))

        if result:
            return UserId(int(result))

        raise RedisKeyNotFoundError(f"Key {key.value} not found in Redis storage")
