from src.application.interfaces.ws.gateway import WSGatewayAPI
import structlog
from aiohttp import ClientSession
from src.domain.values import UserId, Text


class ImplWSGatewayAPI(WSGatewayAPI):

    def __init__(
            self,
            *,
            internal_token: str,
            gateway: str,
            logger: structlog.BoundLogger,
            session: ClientSession,
    ):
        self.__url = gateway
        self.__token = internal_token
        self._logger = logger
        self._session = session

    @property
    def __headers(self):
        return {"X-Internal-Token": self.__token}

    async def notify_client(self, *, user_id: UserId, text: Text):
        url = self.__url + f"/notify/{user_id.value}"
        payload = {"text": text.value}

        async with await self._session.post(url, headers=self.__headers, json=payload) as response:
            response.raise_for_status()

            json_ = await response.json()

            self._logger.info(json_)

            return
