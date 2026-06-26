import pytest
import pytest_asyncio
from faker import Faker

from src.application.dto.client_message import ClientMessage
from src.application.interfaces.broker.publisher import BrokerPublisher

fake = Faker()


@pytest_asyncio.fixture
async def broker_publisher(container) -> BrokerPublisher:
    return await container.get(BrokerPublisher)


@pytest.mark.asyncio
async def test_publish_client_message(broker_publisher, logger):
    payload = ClientMessage(
        user_id=fake.pyint(min_value=1, max_value=999999),
        text="Hello from publisher test",
    )
    await broker_publisher.publish_client_message(payload)
