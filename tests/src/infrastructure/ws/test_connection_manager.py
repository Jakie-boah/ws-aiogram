from dataclasses import dataclass
from unittest.mock import AsyncMock

import pytest

from src.infrastructure.ws.connection import ImplConnectionManager


@dataclass(slots=True)
class Case:
    will_pass: bool
    value: str | int


@pytest.fixture
def manager() -> ImplConnectionManager:
    return ImplConnectionManager()


def make_ws() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_connect_adds_websocket(manager):
    ws = make_ws()
    await manager.connect(client_id=1, websocket=ws)

    assert ws in manager.active_connections[1]
    ws.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_connect_multiple_websockets_same_client(manager):
    ws1, ws2 = make_ws(), make_ws()
    await manager.connect(1, ws1)
    await manager.connect(1, ws2)

    assert manager.active_connections[1] == {ws1, ws2}


@pytest.mark.asyncio
async def test_disconnect_removes_last_websocket(manager):
    ws = make_ws()
    await manager.connect(1, ws)
    manager.disconnect(1, ws)

    assert 1 not in manager.active_connections


@pytest.mark.asyncio
async def test_disconnect_keeps_remaining_websockets(manager):
    ws1, ws2 = make_ws(), make_ws()
    await manager.connect(1, ws1)
    await manager.connect(1, ws2)
    manager.disconnect(1, ws1)

    assert manager.active_connections[1] == {ws2}


@pytest.mark.asyncio
async def test_disconnect_nonexistent_websocket_does_not_raise(manager):
    ws = make_ws()
    await manager.connect(1, ws)
    unknown_ws = make_ws()

    manager.disconnect(1, unknown_ws)

    assert ws in manager.active_connections[1]


@pytest.mark.asyncio
async def test_send_personal_message_reaches_all_connections(manager):
    ws1, ws2 = make_ws(), make_ws()
    await manager.connect(1, ws1)
    await manager.connect(1, ws2)

    await manager.send_personal_message(1, "hello")

    ws1.send_text.assert_awaited_once_with("hello")
    ws2.send_text.assert_awaited_once_with("hello")


@pytest.mark.asyncio
async def test_send_personal_message_does_not_reach_other_clients(manager):
    ws1, ws2 = make_ws(), make_ws()
    await manager.connect(1, ws1)
    await manager.connect(2, ws2)

    await manager.send_personal_message(1, "only for client 1")

    ws1.send_text.assert_awaited_once_with("only for client 1")
    ws2.send_text.assert_not_awaited()
