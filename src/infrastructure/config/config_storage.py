from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
    tg_chat_id: int
    redis: str
    rabbit: str
