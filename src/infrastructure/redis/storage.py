from redis.asyncio.client import Redis

from src.application.interfaces.redis.storage import RedisStorage
from src.domain.values import MessageId, UserId


class ImplRedisStorage(RedisStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set(self, key: MessageId, value: UserId) -> None:
        await self.redis.set(str(key.value), str(value.value))
    