import os

from dotenv import load_dotenv

from src.infrastructure.config.config_storage import Config


def load_config_from_env() -> Config:
    load_dotenv()
    return _create_config()


def _create_config() -> Config:
    return Config(
        bot_token=os.environ["BOT_TOKEN"],
        tg_chat_id=int(os.environ["TG_CHAT_ID"]),
        redis=os.environ["REDIS"],
        rabbit=os.environ["RABBIT"],
        internal_token=os.environ["INTERNAL_TOKEN"],
        ws_host=os.environ["WS_HOST"],
        ws_port=int(os.environ["WS_PORT"]),
    )
