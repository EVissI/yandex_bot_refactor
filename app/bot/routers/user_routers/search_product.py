from aiogram import Router, F
from aiogram.types import Message,PreCheckoutQuery
from app.bot.common.messages import product_card_msg
from app.bot.filters.get_user_info import GetUserInfoFilter
from app.bot.keyboards.inline_kb import Invoice, invoce_butn
from app.bot.keyboards.markup_kb import MainKeyboard, SearchProductKeyboard, request_contact_kb
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger


from app.bot.routers.user_routers.goods_list import W8_payment
from app.bot.utils.market_parsing import get_goods_count
from app.db.dao import GoodsDAO, PaymentDAO
from app.db.database import async_session_maker
from app.db.models import User
from app.db.schemas import GoodsFilter, PaymentModel
from app.config import bot,settings

search_by_sku_router = Router()


class SearchPanel(StatesGroup):
    search_panel = State()


class SearchBySKU(StatesGroup):
    waiting_for_sku = State()


class SearchByName(StatesGroup):
    waiting_for_name = State()


@search_by_sku_router.message(
    F.text == MainKeyboard.get_user_kb_texts("search_product")
)
async def cmd_search_product(message: Message, state: FSMContext):
    await message.answer(message.text, reply_markup=SearchProductKeyboard.build_kb())
    await state.set_state(SearchPanel.search_panel)


@search_by_sku_router.message(
    StateFilter(SearchPanel.search_panel),
    F.text == SearchProductKeyboard.get_search_kb_texts("back"),
    GetUserInfoFilter(),
)
async def cmd_back(message: Message, state: FSMContext, user_info: User):
    await message.answer(
        message.text, reply_markup=MainKeyboard.build_main_kb(user_info.role)
    )
    await state.clear()


@search_by_sku_router.message(
    F.text == SearchProductKeyboard.get_search_kb_texts("search_by_sku")
)
async def ask_for_sku(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите артикул товара:")
    await state.set_state(SearchBySKU.waiting_for_sku)


@search_by_sku_router.message(StateFilter(SearchBySKU.waiting_for_sku), F.text)
async def return_product_card(message: Message, state: FSMContext):
    sku = message.text
    async with async_session_maker() as session:
        product = await GoodsDAO.find_one_or_none(session, filters=GoodsFilter(sku=sku))
    if product:
        msg = product_card_msg(product)
        if product.picture:
            await message.answer_photo(
                product.picture,
                caption=msg,
                reply_markup=invoce_butn(product.id),
            )
            return
        await message.answer(msg, reply_markup=invoce_butn(product.id))
    else:
        await message.answer(
            "Товар с таким артикулом не найден.",
            reply_markup=SearchProductKeyboard.build_kb(),
        )
    await state.set_state(SearchPanel.search_panel)


from math import ceil


@search_by_sku_router.message(
    F.text == SearchProductKeyboard.get_search_kb_texts("search_by_name")
)
async def ask_for_name(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите название товара или его часть:")
    await state.set_state(SearchByName.waiting_for_name)


@search_by_sku_router.message(StateFilter(SearchByName.waiting_for_name), F.text)
async def return_products_by_name(message: Message, state: FSMContext):
    search_query = message.text.lower()
    async with async_session_maker() as session:
        products = await GoodsDAO.find_all_by_name(session, search_query)
    if not products:
        await message.answer("Товары с таким названием не найдены.",reply_markup=SearchProductKeyboard.build_kb())
        await state.set_state(SearchPanel.search_panel)
        return

    # Сохраняем результаты поиска в состоянии
    await state.update_data(
        products=[product.to_dict() for product in products], page=0
    )
    await send_products_page(message, state)


async def send_products_page(message: Message, state: FSMContext):
    state_data = await state.get_data()
    products = state_data.get("products", [])
    page = state_data.get("page", 0)
    page_size = 4  # Количество товаров на одной странице
    total_pages = ceil(len(products) / page_size)

    # Получаем товары для текущей страницы
    start = page * page_size
    end = start + page_size
    current_page_products = products[start:end]

    kb = InlineKeyboardBuilder()
    for product in current_page_products:
        kb.button(text=product["name"], callback_data=f"product_{product['id']}")
    if page > 0:
        kb.button(text="⬅️ Назад", callback_data=f"page_{page - 1}")
    if page < total_pages - 1:
        kb.button(text="➡️ Вперед", callback_data=f"page_{page + 1}")
    kb.adjust(2)
    await message.answer(
        f"📋 <b>Результаты поиска (страница {page + 1} из {total_pages}):</b>",
        reply_markup=kb.as_markup(),
        parse_mode="HTML",
    )


@search_by_sku_router.callback_query(F.data.startswith("page_"))
async def paginate_products(query: CallbackQuery, state: FSMContext):
    page = int(query.data.split("_")[1])
    await state.update_data(page=page)
    await query.message.delete()
    await send_products_page(query.message, state)


@search_by_sku_router.callback_query(F.data.startswith("product_"))
async def process_products(query: CallbackQuery, state: FSMContext):
    product_id = int(query.data.split("_")[1])
    async with async_session_maker() as session:
        product = await GoodsDAO.find_one_or_none_by_id(product_id, session)
    await query.message.delete()
    msg = product_card_msg(product)
    await state.set_data(
            {
                "product_id": product.id,
                "product_name":product.name,
                "product_price":product.price
            }
        )
    if product.picture:
        await query.message.answer_photo(
            product.picture,
            caption=msg,
            reply_markup=invoce_butn(product_id),
        )
        return
    await query.message.answer(msg, reply_markup=invoce_butn(product_id))


@search_by_sku_router.callback_query(Invoice.filter())
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

@search_by_sku_router.pre_checkout_query()
async def process_pre_check_out_query(
    pre_checkout_query: PreCheckoutQuery, state: FSMContext
):
    state_data = await state.get_data()
    async with async_session_maker() as session:
        product = await GoodsDAO.find_one_or_none_by_id(
            state_data.get("product_id"), session
        )
    product_count_upd = await get_goods_count(product.offerID)
    await state.update_data({'product_count':product_count_upd})
    if product_count_upd != product.count:
        async with async_session_maker() as session:
            product.count = product_count_upd
            await GoodsDAO.update(
                session,
                filters=GoodsFilter(id=product.id),
                values=GoodsFilter.model_validate(product.to_dict()),
            )
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@search_by_sku_router.message(F.successful_payment,GetUserInfoFilter())
async def process_successful_payment(message: Message, state: FSMContext,user_info:User):
    state_data= await state.get_data()
    product_count = state_data.get("product_id")
    if product_count == 0 or product_count is None:
        await message.reply(
        f"Платеж на сумму {message.successful_payment.total_amount // 100}"
        f"{message.successful_payment.currency} прошел успешно!"
        f"К сожалению товара сейчас нет в наличии, нужно будет подождать некоторое время для его заказа, спасибо за понимание"
    )
    else:  
        await message.reply(
            f"Платеж на сумму {message.successful_payment.total_amount // 100} "
            f"{message.successful_payment.currency} прошел успешно!"
        )
    logger.info(f"Получен платеж от {message.from_user.id}")

    product_name = state_data.get("product_name")
    amount = message.successful_payment.total_amount // 100
    phone_number = user_info.phone_number
    currency = message.successful_payment.currency
    user_name = message.from_user.full_name or message.from_user.username or "Неизвестный пользователь"

    group_message = (
        f"🛒 <b>Новая покупка!</b>\n"
        f"👤 Покупатель: {user_name}, номер телефона{phone_number}\n"
        f"📦 Товар: {product_name}\n"
        f"💰 Сумма: {amount} {currency}\n"
        f"✅ Статус: Успешно оплачено"
    )
    await bot.send_message(chat_id='-1002509542406', text=group_message, parse_mode="HTML")

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
