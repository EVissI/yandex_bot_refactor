from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger

from app.bot.keyboards.markup_kb import MainKeyboard
from app.bot.utils.market_parsing import parsing_market

update_goods = Router()
@update_goods.message(
    F.text == MainKeyboard.get_admin_kb_texts().get("update_goods")
)
async def cmd_update_goods(message:Message):
    await message.answer('Запускаю обновление товаров')
    await parsing_market(message.from_user.id)
