import pytest
import pytest_asyncio

from src.application.use_cases.publish_admin_message_use_case import PublishAdminMessageUseCase
from src.domain.entities.admin_message import AdminMessage
from src.domain.values import MessageId, Text


@pytest_asyncio.fixture
async def use_case(container) -> PublishAdminMessageUseCase:
    return await container.get(PublishAdminMessageUseCase)


@pytest.mark.asyncio
async def test_use_case(use_case, mocker):
    admin_msg = AdminMessage(
        message_id=MessageId(1),
        text=Text("text")
    )
    await use_case(admin_msg)
