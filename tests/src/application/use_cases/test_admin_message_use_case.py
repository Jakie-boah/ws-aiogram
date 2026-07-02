import pytest
import pytest_asyncio
from src.application.use_cases.admin_message_use_case import AdminMessageUseCase
from src.application.dto.admin_message import AdminMessageDTO
from faker import Faker
from src.application.interfaces.redis.storage import RedisStorage
from src.domain.values import MessageId, UserId

fake = Faker()


@pytest_asyncio.fixture
async def use_case(container):
    return await container.get(AdminMessageUseCase)


@pytest_asyncio.fixture
async def redis_storage(container):
    return await container.get(RedisStorage)


@pytest.mark.asyncio
async def test_admin_message_use_case(use_case, redis_storage):
    message_id = fake.pyint(min_value=1, max_value=10000)

    await redis_storage.set(
        MessageId(message_id),
        UserId(fake.pyint(min_value=1, max_value=10000))
    )

    payload = AdminMessageDTO(
        message_id=message_id,
        text=fake.text(max_nb_chars=200)
    )
    await use_case(payload)
