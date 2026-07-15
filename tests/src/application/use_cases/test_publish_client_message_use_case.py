import pytest
import pytest_asyncio
from faker import Faker

from src.application.use_cases.publish_client_message_use_case import PublishClientMessageUseCase
from src.domain.entities.client_message import ClientMessage
from src.domain.values import UserId, Text

fake = Faker()


@pytest_asyncio.fixture
async def use_case(container) -> PublishClientMessageUseCase:
    return await container.get(PublishClientMessageUseCase)


@pytest.mark.asyncio
@pytest.mark.skip
async def test_use_case(use_case):
    client_msg = ClientMessage(
        user_id=UserId(fake.pyint(min_value=1, max_value=999999)),
        text=Text(fake.text())
    )

    await use_case(client_msg)
