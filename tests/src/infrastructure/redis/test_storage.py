from src.application.interfaces.redis.storage import RedisStorage
import pytest
import pytest_asyncio
from src.domain.values.numbers import MessageId, UserId
from faker import Faker
from src.infrastructure.redis.errors import RedisKeyNotFoundError

fake = Faker()


@pytest_asyncio.fixture
async def redis_storage(container) -> RedisStorage:
    return await container.get(RedisStorage)


@pytest.mark.asyncio
async def test_set_and_get(redis_storage, logger):
    message_id, user_id = MessageId(fake.pyint()), UserId(fake.pyint())
    await redis_storage.set(message_id, user_id)

    result = await redis_storage.get(message_id)
    assert result.value == user_id.value


@pytest.mark.asyncio
async def test_get_not_found(redis_storage):
    with pytest.raises(RedisKeyNotFoundError):
        await redis_storage.get(MessageId(fake.pyint()))
