import aiohttp
import requests
from app.config import settings,vk_session
from loguru import logger

def add_market_item(name, description, price, category_id, main_photo_id):
    url = "https://api.vk.com/method/market.add"
    params = {
        "access_token": settings.VK_API_KEY.get_secret_value(),
        "v": "5.131",
        "owner_id": settings.VK_ID_GROUP,  # Для группы указываем owner_id с минусом
        "name": name,
        "description": description,
        "category_id": category_id,
        "price": price,
        "main_photo_id": main_photo_id,
        "deleted": 0  # 1 - товар скрыт, 0 - активен
    }
    response = requests.post(url, params=params)
    return response.json()

async def upload_photo_to_vk(image_url):
    """
    Загружает фото в ВКонтакте и возвращает photo_id.
    """
    # Получаем URL сервера для загрузки
    upload_server_url = f"https://api.vk.com/method/market.getProductPhotoUploadServer"
    params = {
        "access_token": settings.VK_API_KEY.get_secret_value(),
        "group_id": settings.VK_ID_GROUP,
        "v": "5.199",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(upload_server_url, params=params) as resp:
            response = await resp.json(content_type=None)
            upload_url = response["response"]["upload_url"]

        # Загрузка фото по URL без сохранения на диск
        async with session.get(image_url) as resp:
            photo_data = await resp.read()

        # Отправка фото на сервер VK
        data = aiohttp.FormData()
        data.add_field('file', photo_data, filename='photo.jpg', content_type='image/jpeg')
        async with session.post(upload_url, data=data) as resp:
            upload_r_t = await resp.text()

        save_url = "https://api.vk.com/method/market.saveProductPhoto"
        save_params = {
            "upload_response": upload_r_t,
            "access_token": settings.VK_API_KEY.get_secret_value(),
            "v": "5.199"
        }
        async with session.get(save_url, params=save_params) as resp:
            save_response = await resp.json()
        return save_response['response']['photo_id']