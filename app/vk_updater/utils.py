import aiohttp
import requests
from app.config import settings
from loguru import logger

async def add_market_card(name,
                          description,
                          category_id,
                          sku,
                          price,
                          stock_amount,
                          main_photo_id,
                          ):
    add_url = 'https://api.vk.com/method/market.add'
    params = {
        "v": "5.199",
        "access_token": settings.VK_API_KEY.get_secret_value(),
        "owner_id": f'-{settings.VK_ID_GROUP}',
        "name": name[:100],  
        "description": description or "",  
        "category_id": category_id or 0, 
        "price": price or 0, 
        "main_photo_id": main_photo_id or 0,  
        "sku": sku or "",  
        "stock_amount": stock_amount or 0, 
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(add_url, params=params) as resp:
            logger.info(await resp.text())
            response = await resp.json(content_type=None)
            
            return response['response']
            
        
async def get_all_market_card():
    get_url = 'https://api.vk.com/method/market.get'
    items = []
    offset = 0
    count = 200  # максимально допустимое количество товаров в одном запросе
    
    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "v": "5.199",
                "access_token": settings.VK_API_KEY.get_secret_value(),
                "owner_id": f'-{settings.VK_ID_GROUP}',
                "count": count,
                'offset': offset
            }
            async with session.get(get_url, params=params) as response:
                data = await response.json()
            
            if "error" in data:
                raise Exception(f"VK API Error: {data['error']}")
            
            result = data.get("response", {})
            current_items = result.get("items", [])
            
            if not current_items:
                break

            items.extend(current_items)
            # Если получено меньше товаров, чем запрашивали, значит достигли конца
            if len(current_items) < count:
                break
            
            offset += count
        return items

async def upload_photo_to_vk(image_url):
    """
    Загружает фото в ВКонтакте и возвращает photo_id.
    """
    # Получаем URL сервера для загрузки
    try:
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
    except Exception as e:
        logger.error(f'Ошибка при публикации фотографий на сервер вк {str(e)}')
        return None