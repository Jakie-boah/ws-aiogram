from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Config:
    bot_token: str
