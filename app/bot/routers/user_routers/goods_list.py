from aiogram import Router,F
from aiogram.types import Message,CallbackQuery
from app.bot.common.messages import product_card_msg
from app.bot.keyboards.inline_kb import ChooseCategory, GoodsList,show_category_inl_kb, show_product_inl_kb
from app.bot.keyboards.markup_kb import MainKeyboard
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State,StatesGroup

from app.bot.utils.market_parsing import get_goods_count
from app.db.dao import GoodsDAO,GoodsCategoryDAO
from app.db.database import async_session_maker
from app.db.schemas import GoodsFilter,GoodsCategoryFilter

goods_list_router = Router()


@goods_list_router.message(F.text.in_([MainKeyboard.get_user_kb_texts().get("goods_list"),MainKeyboard.get_user_kb_texts().get('goods_not_in_cash')]))
async def cmd_goods_list(message:Message):
    async with async_session_maker() as session:
        category_list = await GoodsCategoryDAO.find_all(session, GoodsFilter())
    selected_product_sheet_type_dict= {
        MainKeyboard.get_user_kb_texts().get("goods_list"):1,
        MainKeyboard.get_user_kb_texts().get("goods_not_in_cash"):2
    }
    await message.answer('Выберите категорию',
                         reply_markup=show_category_inl_kb(category_list,selected_product_sheet_type = selected_product_sheet_type_dict.get(message.text)))


@goods_list_router.callback_query(ChooseCategory.filter())
async def take_category_callback(
    query: CallbackQuery, callback_data: ChooseCategory
):
    async with async_session_maker() as session:
        if callback_data.selected_product_sheet_type == 1:
            goods_list = await GoodsDAO.find_available_by_category(session,category_id=callback_data.category_id)
        if callback_data.selected_product_sheet_type == 2:
            goods_list = await GoodsDAO.find_unavailable_by_category(session,category_id=callback_data.category_id)
    if not goods_list:
        await query.answer('К сожалению категория пустая')
        return
    await query.message.delete()
    first_product = goods_list[0]
    if first_product.picture:
        await query.message.answer_photo(first_product.picture,
                                        product_card_msg(first_product),
                                        reply_markup=show_product_inl_kb(goods_list,
                                                                         product_id = first_product.id,
                                                                         category_id=callback_data.category_id,
                                                                         selected_product_sheet_type=callback_data.selected_product_sheet_type))
    else:
        await query.message.answer(product_card_msg(first_product),
                                        reply_markup=show_product_inl_kb(goods_list,
                                                                         product_id = first_product.id,
                                                                         category_id=callback_data.category_id,
                                                                         selected_product_sheet_type=callback_data.selected_product_sheet_type))


@goods_list_router.callback_query(GoodsList.filter(F.action == "Pagination"))
async def take_category_callback(
    query: CallbackQuery, callback_data: GoodsList
):
    async with async_session_maker() as session:
        if callback_data.selected_product_sheet_type == 1:
            goods_list = await GoodsDAO.find_available_by_category(session,category_id=callback_data.category_id)
        if callback_data.selected_product_sheet_type == 2:
            goods_list = await GoodsDAO.find_unavailable_by_category(session,category_id=callback_data.category_id)
    await query.message.delete()
    await query.message.answer_photo(goods_list[callback_data.page].picture,
                                    product_card_msg(goods_list[callback_data.page]),
                                    reply_markup=show_product_inl_kb(goods_list,
                                                                   category_id=goods_list[callback_data.page].category_id,
                                                                   product_id=goods_list[callback_data.page].id,
                                                                   page = callback_data.page,
                                                                   selected_product_sheet_type = callback_data.selected_product_sheet_type))
    

@goods_list_router.callback_query(GoodsList.filter(F.action == "Back"))
async def back_to_category_selection(query: CallbackQuery,callback_data: GoodsList):
    async with async_session_maker() as session:
        category_list = await GoodsCategoryDAO.find_all(session, GoodsFilter())
    await query.message.delete()
    await query.message.answer('Выберите категорию',
                         reply_markup=show_category_inl_kb(category_list,selected_product_sheet_type = callback_data.selected_product_sheet_type))

# @goods_list_router.callback_query(GoodsList.filter(F.action == "Buy"))
# async def buy_product(query: CallbackQuery, callback_data: GoodsList):
#     async with async_session_maker() as session:
#         print(callback_data.product_id)
#         product = await GoodsDAO.find_one_or_none(session,
#                                                   filters=GoodsFilter(id=callback_data.product_id))
    
#     if not product:
#         await query.answer("Товар не найден.")
#         return
#     product_count_upd = await get_goods_count(product.offerID)
#     if product_count_upd != product.count:
#         async with async_session_maker() as session:
#             product.count = product_count_upd
#             await GoodsDAO.update(session,filters=GoodsFilter(id=callback_data.product_id),
#                                   values=GoodsFilter.model_validate(product.to_dict()))

#     if not product.count or product.count <= 0:
#         await query.answer("К сожалению, товара нет в наличии.")
#     else:
#         await query.answer(f"Покупка успешна! Вы приобрели {product.name} за {product.price} руб.")