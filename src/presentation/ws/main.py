from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from src.infrastructure.config.config_loader import load_config_from_env
from src.presentation.dependency_container import create_container
from src.presentation.ws.router import router


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
