from src.application.use_cases.client_message_use_case import ClientMessageUseCase

import pytest
import pytest_asyncio
from src.application.dto.client_message import ClientMessage


@pytest_asyncio.fixture
async def use_case(container) -> ClientMessageUseCase:
    return await container.get(ClientMessageUseCase)


@pytest.mark.asyncio
async def test_client_message_use_case(use_case, logger):
    payload = ClientMessage(
        user_id=123,
        text="Hello, from test"
    )
    await use_case(payload)
