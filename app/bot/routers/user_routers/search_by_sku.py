from aiogram import Router,F
from aiogram.types import Message
from app.bot.common.messages import product_card_msg
from app.bot.keyboards.markup_kb import MainKeyboard
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State,StatesGroup

from app.db.dao import GoodsDAO
from app.db.database import async_session_maker
from app.db.schemas import GoodsFilter
search_by_sku_router = Router()

class SearchBySKU(StatesGroup):
    waiting_for_sku = State()

@search_by_sku_router.message(F.text ==MainKeyboard.get_user_kb_texts().get("search_by_sku"))
async def ask_for_sku(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите артикул товара:")
    await state.set_state(SearchBySKU.waiting_for_sku)

@search_by_sku_router.message(StateFilter(SearchBySKU.waiting_for_sku), F.text)
async def return_product_card(message: Message, state: FSMContext):
    sku = message.text
    async with async_session_maker() as session:
        product = await GoodsDAO.find_one_or_none(session,filters=GoodsFilter(sku = sku))
    if product:
        msg = product_card_msg(product)
        if product.picture:
            await message.answer_photo(product.picture,
                                       caption=msg)
            return
        await message.answer(msg)
    else:
        await message.answer("Товар с таким артикулом не найден.")
    await state.clear()
