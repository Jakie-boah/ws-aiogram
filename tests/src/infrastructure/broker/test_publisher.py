import pytest
import pytest_asyncio
from faker import Faker

from src.domain.entities.client_message import ClientMessage
from src.domain.entities.admin_message import AdminMessage

from src.application.interfaces.broker.publisher import BrokerPublisher
from src.domain.values import UserId, Text

fake = Faker()


@pytest_asyncio.fixture
async def broker_publisher(container) -> BrokerPublisher:
    return await container.get(BrokerPublisher)


@pytest.mark.asyncio
async def test_publish_client_message(broker_publisher, logger):
    payload = ClientMessage(
        user_id=UserId(fake.pyint(min_value=1, max_value=999999)),
        text=Text("Hello from publisher test"),
    )
    await broker_publisher.publish_client_message(payload)


@pytest.mark.asyncio
async def test_publish_admin_message(broker_publisher, logger):
    payload = AdminMessage(
        message_id=UserId(fake.pyint(min_value=1, max_value=999999)),
        text=Text("Hello from publisher test"),
    )
    await broker_publisher.publish_admin_message(payload)
