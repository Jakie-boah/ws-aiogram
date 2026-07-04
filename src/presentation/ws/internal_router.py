import structlog
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from src.infrastructure.config.config_storage import Config
import secrets


@inject
def verify_internal_access(
        config: FromDishka[Config],
        x_internal_token: str = Header(...),
):
    if not secrets.compare_digest(x_internal_token, config.internal_token):
        raise HTTPException(status_code=403, detail="Forbidden")


router = APIRouter(
    prefix="/internal",
    include_in_schema=False,
    dependencies=[Depends(verify_internal_access)],
)


@router.post("/ws/notify/{user_id}")
@inject
async def notify_client(user_id: int, logger: FromDishka[structlog.BoundLogger], text: str = Body(embed=True)):
    logger.info(user_id)
    logger.info(text)

    return {"message": f"Notification sent to user {user_id} with text: {text}", "status": 200}
