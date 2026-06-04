from uuid import uuid4

import structlog
from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from src.application.interfaces.ws.connection_manager import ConnectionManager
from src.presentation.ws.html_base import html


router = APIRouter(prefix="")


@router.get("/")
@inject
async def get(logger: FromDishka[structlog.BoundLogger], session_id: str | None = None):
    session_id = session_id or str(uuid4())

    logger.info(session_id)

    html_with_id = html.replace(
        'Your ID: <span id="ws-id"></span>',
        f'Your ID: <span id="ws-id">{session_id}</span>'
    )

    resp = HTMLResponse(html_with_id)

    resp.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,  # JS не может читать — защита от XSS
        samesite="strict",
    )

    return resp


@router.websocket("/ws")
@inject
async def websocket_endpoint(
        logger: FromDishka[structlog.BoundLogger],
        websocket: WebSocket,
        manager: FromDishka[ConnectionManager]
):
    logger.info(f"websocket.cookies.get(session_id) - {websocket.cookies.get("session_id")}")
    session_id = websocket.cookies.get("session_id")

    if not session_id:
        logger.info("close")
        await websocket.close(code=1008)
        return

    logger.info(session_id)

    logger.info(f"алоооо - {session_id}")

    await manager.connect(session_id, websocket)

    try:
        while True:
            data = await websocket.receive_text()

            logger.info(manager.active_connections)

            await manager.send_personal_message(session_id, f"You wrote: {data}")

    except WebSocketDisconnect:
        logger.info(f"Client #{session_id} left the chat")
        manager.disconnect(session_id, websocket)
