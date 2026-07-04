import pytest
import pytest_asyncio
from src.application.interfaces.ws.gateway import WSGatewayAPI
from src.domain.values import UserId, Text


@pytest_asyncio.fixture
async def gateway(container) -> WSGatewayAPI:
    return await container.get(WSGatewayAPI)


@pytest.mark.asyncio
async def test_notify_client(gateway):
    user_id, text = UserId(1), Text("Hello, World!")

    await gateway.notify_client(user_id=user_id, text=text)
