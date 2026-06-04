import os

from dotenv import load_dotenv

from src.infrastructure.config.config_storage import Config


def load_config_from_env() -> Config:
    load_dotenv()
    return _create_config()


def _create_config() -> Config:
    return Config(
        bot_token=os.environ["BOT_TOKEN"],
    )
