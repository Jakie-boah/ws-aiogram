import pytest
import pytest_asyncio
from src.application.use_cases.admin_message_use_case import AdminMessageUseCase

from src.application.interfaces.redis.storage import RedisStorage
from src.domain.values import MessageId, UserId, Text

from src.application.dto.admin_message import AdminMessage


@pytest_asyncio.fixture
async def redis_storage(container) -> RedisStorage:
    return await container.get(RedisStorage)


@pytest_asyncio.fixture
async def use_case(container):
    return await container.get(AdminMessageUseCase)


@pytest.mark.asyncio
async def test_admin_response(redis_storage, use_case):
    message_id, user_id = MessageId(1212), UserId(12121)
    await redis_storage.set(message_id, user_id)

    payload = AdminMessage(
        text=Text("hello"),
        client_message_id=message_id
    )

    await use_case(payload)
