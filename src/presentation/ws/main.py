from collections import defaultdict

from dishka import make_async_container
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import HTMLResponse
from structlog import get_logger
from uuid import uuid4

from src.infrastructure.config.config_loader import load_config_from_env
from src.infrastructure.config.config_storage import Config
from src.infrastructure.ioc_container import LoggerProvider, WSProvider
from src.presentation.ws.router import router
from dishka.integrations.fastapi import setup_dishka


# manager = ConnectionManager()
# logger = get_logger()


# @app.get("/")
# async def get(response: Response, session_id: str | None = None):
#     session_id = session_id or str(uuid4())
#
#     logger.info(session_id)
#
#     html_with_id = html.replace(
#         "Your ID: <span id=\"ws-id\"></span>",
#         f'Your ID: <span id="ws-id">{session_id}</span>'
#     )
#
#     resp = HTMLResponse(html_with_id)
#
#     resp.set_cookie(
#         key="session_id",
#         value=session_id,
#         httponly=True,  # JS не может читать — защита от XSS
#         samesite="strict",
#     )
#
#     return resp

#
# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     logger.info(f"websocket.cookies.get(session_id) - {websocket.cookies.get("session_id")}")
#     session_id = websocket.cookies.get("session_id")
#
#     if not session_id:
#         logger.info("close")
#         await websocket.close(code=1008)
#         return
#
#     logger.info(session_id)
#
#     logger.info(f"алоооо - {session_id}")
#
#     await manager.connect(session_id, websocket)
#
#     try:
#         while True:
#             data = await websocket.receive_text()
#
#             logger.info(manager.active_connections)
#
#             await manager.send_personal_message(session_id, f"You wrote: {data}")
#
#     except WebSocketDisconnect:
#         logger.info(f"Client #{session_id} left the chat")
#         manager.disconnect(session_id, websocket)


def create_container(config: Config):
    return make_async_container(
        LoggerProvider(),
        WSProvider(),
        context={Config: config},
    )


def create_app() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    app.include_router(router)

    return app


def app_factory() -> FastAPI:
    config = load_config_from_env()
    app = create_app()
    container = create_container(config)

    setup_dishka(container=container, app=app)
    return app
