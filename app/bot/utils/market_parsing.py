import re

import aiohttp
from pydantic import ValidationError
from app.config import settings, bot, admins
from app.db.dao import GoodsCategoryDAO, GoodsDAO
from app.db.database import async_session_maker
from app.db.schemas import (
    GoodsCategoryFilter,
    GoodsCategoryModel,
    GoodsModel,
    GoodsFilter,
)
from bs4 import BeautifulSoup

from sqlalchemy.exc import SQLAlchemyError


def strip_html_tags(s):
    """
    Удаляет HTML теги из текста, а также целые строки, содержащие теги <h3>...</h3>.
    """
    if s is None:
        return None
    soup = BeautifulSoup(s, "html.parser")

    # Удаляем все элементы <h3> и их содержимое
    for h3_tag in soup.find_all("h3"):
        h3_tag.decompose()  # Удаляет элемент из дерева

    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def extract_articul(text):
    match = re.search(r"\b\d{5}\b", text)
    if match:
        return match.group(0)
    return None


async def process_offer(offer):
    """
    Обрабатывает информацию о товаре, скачивает изображения и возвращает
    строку с путями к изображениям, разделенными запятыми.
    """

    image_urls = offer.get("offer").get("pictures")
    if not image_urls:
        print("Нет URL изображений для скачивания.")
        return ""  # Возвращаем пустую строку, если нет изображений
    img = image_urls[0]
    msg = await bot.send_photo(admins[0], img)
    return msg.photo[-1].file_id


async def parsing_market(chat_id):
    page_token = None
    while True:
        async with async_session_maker() as session:
            async with aiohttp.ClientSession() as http_session:
                url = f"https://api.partner.market.yandex.ru/v2/businesses/{str(121482691)}/offer-mappings?limit=200"
                if page_token:
                    url += f"&page_token={page_token}"

                headers = {
                    "Api-Key": str(settings.YA_API_KEY),
                    "Content-Type": "application/json",
                }

                response = await http_session.post(url, headers=headers)

                if response.status == 200:
                    data = await response.json()
                    offer_mappings = data.get("result", {}).get("offerMappings", [])
                    if not offer_mappings:
                        break

                    # Вывод информации о товарах
                    for offer in offer_mappings:
                        marker_id = offer.get("mapping").get("marketCategoryId")
                        market_name = offer.get("mapping").get("marketCategoryName")
                        name = offer.get("offer").get("name")
                        await add_category(category_id=marker_id, name=market_name)
                        if not await GoodsDAO.find_one_or_none(
                            session, GoodsFilter(name=name)
                        ):
                            picture_id = await process_offer(offer)

                            offer_id = offer.get("offer").get("offerId")
                            description = offer.get("offer").get("description")
                            description = strip_html_tags(description)
                            sku = extract_articul(name)
                            price = offer.get("offer").get("basicPrice").get("value")
                            count = await get_goods_count(offer_id)
                            try:
                                good = GoodsModel(
                                    name=name,
                                    offerID=offer_id,
                                    description=description,
                                    sku=sku,
                                    price=price,
                                    picture=picture_id,
                                    count=count,
                                    category_id=marker_id,
                                )
                                await GoodsDAO.add(session, good)
                            except ValidationError:
                                continue
                    page_token = (
                        data.get("result", {}).get("paging", {}).get("nextPageToken")
                    )  # Получение токена следующей
                    # страницы
                    if not page_token:
                        await bot.send_message(chat_id, "Обновление товаров законченно")
                        break
                else:
                    print(f"Ошибка: {response.status}, {response.text}")
                    break


async def add_category(category_id, name):
    try:
        async with async_session_maker() as session:
            # Проверяем, существует ли категория с таким category_id
            existing_category = await GoodsCategoryDAO.find_one_or_none(
                session, GoodsCategoryFilter(category_id=category_id)
            )

            if existing_category is not None:
                print(f"Category with id {category_id} already exists. Skipping.")
                return None  # Или можно вернуть существующую категорию, если это необходимо

            new_category = GoodsCategoryModel(category_id=category_id, name=name)
            await GoodsCategoryDAO.add(session, new_category)
            return new_category
    except SQLAlchemyError as e:
        print("Error adding category:", e)
        return None


async def get_goods_count(offer_id):
    # Тело запроса с указанием списка SKU (это типо айди товара)
    data = {"shopSkus": [str(offer_id)]}
    url = f"https://api.partner.market.yandex.ru/campaigns/{settings.YA_CAMPAIGN_ID}/stats/skus"

    headers = {"Api-Key": settings.YA_API_KEY, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as http_session:
        response = await http_session.post(url, headers=headers, json=data)
        if response.status == 200:
            data = await response.json()
            goods = data.get("result", {}).get("shopSkus", [])
            for item in goods:
                if not item.get("warehouses"):
                    return None
                for warehouse in item["warehouses"]:
                    for stock in warehouse["stocks"]:
                        if stock.get("type") == "AVAILABLE":
                            return stock.get("count")
        else:
            print(f"Ошибка: {response.status}, {response.text}")
