import os
import vk_api
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from pydantic import SecretStr,PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    FORMAT_LOG: str = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"
    LOG_ROTATION: str = "10 MB"

    BOT_TOKEN: SecretStr 
    ROOT_ADMIN_IDS: List[int] 
    CHAT_FOR_NOTIFICATION: str

    YOOKASSA_SHOP_ID: int
    YOOKASSA_API_KEY:SecretStr

    YA_API_KEY: str
    YA_CAMPAIGN_ID:int

    VK_API_KEY:SecretStr
    VK_ID_GROUP:int

    DB_URL:PostgresDsn

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )

settings = Settings()


def setup_logger(app_name: str):
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
    os.makedirs(log_dir, exist_ok=True)
    logger.add(
        os.path.join(log_dir, f"log_{app_name}.txt"),
        format=settings.FORMAT_LOG,
        level="INFO",
        rotation=settings.LOG_ROTATION
    )
    logger.add(
        os.path.join(log_dir, f"log_{app_name}_error.txt"),
        format=settings.FORMAT_LOG,
        level="ERROR",
        rotation=settings.LOG_ROTATION
    )

bot = Bot(token=settings.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

vk_session = vk_api.VkApi(token=settings.VK_API_KEY.get_secret_value())
admins = settings.ROOT_ADMIN_IDS