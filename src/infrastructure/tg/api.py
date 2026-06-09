from aiohttp import ClientSession

from src.application.interfaces.tg.api import TgAPI
from src.domain.values import Text, MessageId


class ImplTgAPI(TgAPI):
    url = "https://api.telegram.org/bot{bot_token}"

    def __init__(
            self, *,
            http_session: ClientSession,
            chat_id: int,
            bot_token: str
    ):
        self.http_session = http_session
        self.__chat_id = chat_id
        self.__bot_token = bot_token

    async def send_message(self, text: Text) -> MessageId:
        url = self.url.format(bot_token=self.__bot_token) + "/sendMessage"

        payload = {
            "chat_id": self.__chat_id,
            "text": text.value,
            "parse_mode": "HTML",
        }

        async with self.http_session.post(url, json=payload) as response:
            response.raise_for_status()
            response = await response.json()
            return MessageId(response["result"]["message_id"])
