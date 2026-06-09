import pytest
import pytest_asyncio
from src.application.interfaces.tg.api import TgAPI
from src.domain.values import Text
from src.domain.values import MessageId


@pytest_asyncio.fixture
async def tg_api(container) -> TgAPI:
    return await container.get(TgAPI)


@pytest.mark.asyncio
async def test_send_message(tg_api, logger):
    result = await tg_api.send_message(text=Text("Hello, from text"))
    assert isinstance(result, MessageId)
