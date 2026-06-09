from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as redis
from dishka import Provider, Scope, from_context, provide

from src.application.interfaces.redis.storage import RedisStorage
from src.infrastructure.config.config_storage import Config
from src.infrastructure.redis.storage import ImplRedisStorage


class RedisProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_redis_client(self, config: Config) -> AsyncGenerator[redis.Redis, Any]:
        client = redis.from_url(config.redis)
        yield client
        await client.aclose()

    @provide(scope=Scope.APP)
    async def get_redis_storage(self, client: redis.Redis) -> RedisStorage:
        return ImplRedisStorage(redis=client)
