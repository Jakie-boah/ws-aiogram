from typing import Protocol
from src.domain.values import Text


class TgAPI(Protocol):

    async def send_message(self, text: Text):
        pass
