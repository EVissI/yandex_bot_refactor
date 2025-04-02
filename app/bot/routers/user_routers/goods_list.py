from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from app.bot.common.messages import product_card_msg
from app.bot.filters.get_user_info import GetUserInfoFilter
from app.bot.keyboards.inline_kb import (
    ChooseCategory,
    GoodsList,
    Invoice,
    invoce_butn,
    show_category_inl_kb,
    show_product_inl_kb,
)
from app.bot.keyboards.markup_kb import MainKeyboard, request_contact_kb
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from app.bot.utils.market_parsing import get_goods_count
from app.bot.utils.yookassa_func import create_payment
from app.db.dao import GoodsDAO, GoodsCategoryDAO, PaymentDAO, UserDAO
from app.db.database import async_session_maker
from app.db.models import User
from app.db.schemas import GoodsFilter, PaymentModel, TelegramIDModel,UserFilterModel
from app.config import bot, settings

goods_list_router = Router()


class W8_payment(StatesGroup):
    phone_number = State()
    payment = State()


@goods_list_router.message(
    F.text.in_(
        [
            MainKeyboard.get_user_kb_texts().get("goods_list"),
            MainKeyboard.get_user_kb_texts().get("goods_not_in_cash"),
        ]
    )
)
async def cmd_goods_list(message: Message):
    async with async_session_maker() as session:
        category_list = await GoodsCategoryDAO.find_all(session, GoodsFilter())
    selected_product_sheet_type_dict = {
        MainKeyboard.get_user_kb_texts().get("goods_list"): 1,
        MainKeyboard.get_user_kb_texts().get("goods_not_in_cash"): 2,
    }
    await message.answer(
        "Выберите категорию",
        reply_markup=show_category_inl_kb(
            category_list,
            selected_product_sheet_type=selected_product_sheet_type_dict.get(
                message.text
            ),
        ),
    )


@goods_list_router.callback_query(ChooseCategory.filter())
async def take_category_callback(query: CallbackQuery, callback_data: ChooseCategory):
    async with async_session_maker() as session:
        if callback_data.selected_product_sheet_type == 1:
            goods_list = await GoodsDAO.find_available_by_category(
                session, category_id=callback_data.category_id
            )
        if callback_data.selected_product_sheet_type == 2:
            goods_list = await GoodsDAO.find_unavailable_by_category(
                session, category_id=callback_data.category_id
            )
    if not goods_list:
        await query.answer("К сожалению категория пустая")
        return
    await query.message.delete()
    first_product = goods_list[0]
    if first_product.picture:
        await query.message.answer_photo(
            first_product.picture,
            product_card_msg(first_product),
            reply_markup=show_product_inl_kb(
                goods_list,
                product_id=first_product.id,
                category_id=callback_data.category_id,
                selected_product_sheet_type=callback_data.selected_product_sheet_type,
            ),
        )
    else:
        await query.message.answer(
            product_card_msg(first_product),
            reply_markup=show_product_inl_kb(
                goods_list,
                product_id=first_product.id,
                category_id=callback_data.category_id,
                selected_product_sheet_type=callback_data.selected_product_sheet_type,
            ),
        )


@goods_list_router.callback_query(GoodsList.filter(F.action == "Pagination"))
async def take_category_callback(query: CallbackQuery, callback_data: GoodsList):
    async with async_session_maker() as session:
        if callback_data.selected_product_sheet_type == 1:
            goods_list = await GoodsDAO.find_available_by_category(
                session, category_id=callback_data.category_id
            )
        if callback_data.selected_product_sheet_type == 2:
            goods_list = await GoodsDAO.find_unavailable_by_category(
                session, category_id=callback_data.category_id
            )
    await query.message.delete()
    await query.message.answer_photo(
        goods_list[callback_data.page].picture,
        product_card_msg(goods_list[callback_data.page]),
        reply_markup=show_product_inl_kb(
            goods_list,
            category_id=goods_list[callback_data.page].category_id,
            product_id=goods_list[callback_data.page].id,
            page=callback_data.page,
            selected_product_sheet_type=callback_data.selected_product_sheet_type,
        ),
    )


@goods_list_router.callback_query(GoodsList.filter(F.action == "Back"))
async def back_to_category_selection(query: CallbackQuery, callback_data: GoodsList):
    async with async_session_maker() as session:
        category_list = await GoodsCategoryDAO.find_all(session, GoodsFilter())
    await query.message.delete()
    await query.message.answer(
        "Выберите категорию",
        reply_markup=show_category_inl_kb(
            category_list,
            selected_product_sheet_type=callback_data.selected_product_sheet_type,
        ),
    )


@goods_list_router.callback_query(
    GoodsList.filter(F.action == "Buy"), GetUserInfoFilter()
)
async def buy_product(
    query: CallbackQuery, callback_data: GoodsList, state: FSMContext, user_info: User
):
    async with async_session_maker() as session:
        product = await GoodsDAO.find_one_or_none(
            session, filters=GoodsFilter(id=callback_data.product_id)
        )

    await state.set_data(
            {
                "product_id": product.id,
                "selected_product_sheet_type": callback_data.selected_product_sheet_type,
                "product_name":product.name,
                "product_price":product.price
            }
        )
    
    if user_info.phone_number is None:
        await query.message.delete()
        await query.message.answer(
            "Для того чтобы продолжить оформление заказа, поделитесь своим номером",
            reply_markup=request_contact_kb(),
        )
        await state.set_state(W8_payment.phone_number)
        return
    await process_invoice(query, callback_data=Invoice(product_id=product.id), state=state)

@goods_list_router.message(
    StateFilter(W8_payment.phone_number), F.contact, GetUserInfoFilter()
)
async def func_contact(message: Message, state: FSMContext, user_info: User):
    data = await state.get_data()
    logger.info(message.contact.phone_number)
    async with async_session_maker() as session:
        user_info_upd = user_info
        user_info_upd.phone_number = message.contact.phone_number
        await UserDAO.update(
            session,
            filters=UserFilterModel(telegram_id=user_info.telegram_id),
            values=UserFilterModel.model_validate(user_info_upd.to_dict()),
        )
    await message.answer(
        "Контактный телефон обновлен, спасибо! Оплачивайте заказ и с вами свяжется наш менеджер",
        reply_markup=invoce_butn(data.get("product_id")),
    )


@goods_list_router.callback_query(Invoice.filter())
async def process_invoice(
    query: CallbackQuery, callback_data: Invoice, state: FSMContext
):
    await query.message.delete()
    state_data = await state.get_data()
    await bot.send_invoice(
        chat_id=query.from_user.id,
        title="Оплата товара",
        description=f"Оплата товара '{state_data.get('product_name')}'",
        payload=f"product_{state_data.get('product_id')}_payment",
        provider_token=settings.YOOKASSA_API_KEY.get_secret_value(),
        currency="RUB",
        prices=[{"label": "Руб", "amount": int(float(state_data.get('product_price')) * 100)}],
    )


@goods_list_router.pre_checkout_query()
async def process_pre_check_out_query(
    pre_checkout_query: PreCheckoutQuery, state: FSMContext
):
    state_data = await state.get_data()
    selected_product_sheet_type = state_data.get("selected_product_sheet_type")
    if selected_product_sheet_type == 1:
        async with async_session_maker() as session:
            product = await GoodsDAO.find_one_or_none_by_id(
                state_data.get("product_id"), session
            )
        product_count_upd = await get_goods_count(product.offerID)
        if product_count_upd != product.count:
            async with async_session_maker() as session:
                product.count = product_count_upd
                await GoodsDAO.update(
                    session,
                    filters=GoodsFilter(id=product.id),
                    values=GoodsFilter.model_validate(product.to_dict()),
                )
        if not product.count or product.count <= 0:
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=False,error_message='Товар недоступен')
        else:
            await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    if selected_product_sheet_type == 2:
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@goods_list_router.message(F.successful_payment)
async def process_successful_payment(message: Message, state: FSMContext):
    await message.reply(
        f"Платеж на сумму {message.successful_payment.total_amount // 100} "
        f"{message.successful_payment.currency} прошел успешно!"
    )
    logger.info(f"Получен платеж от {message.from_user.id}")
    current_state = await state.get_state()
    state_data = await state.get_data()
    async with async_session_maker() as session:
        await PaymentDAO.add(
            session,
            PaymentModel(
                payment_id=message.successful_payment.provider_payment_charge_id,
                user_telegram_id=message.from_user.id,
                goods_id=state_data.get('product_id'),
                amount=message.successful_payment.total_amount,
                description=f"Оплата товара '{state_data.get('product_name')}'",
                status='succeeded'
            ),
        )
    if current_state is not None:
        await state.clear()
