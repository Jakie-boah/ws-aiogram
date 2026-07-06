import secrets

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, Depends, Header, HTTPException
from fastapi.responses import JSONResponse as JsonResponse

from src.application.interfaces.ws.connection_manager import ConnectionManager
from src.infrastructure.config.config_storage import Config


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
async def notify_client(
        user_id: int,
        connection_manager: FromDishka[ConnectionManager],
        text: str = Body(embed=True),

):
    await connection_manager.send_personal_message(user_id, text)

    return JsonResponse(content={"message": "Notification sent"}, status_code=200)
