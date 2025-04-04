import asyncio
from app.db.dao import GoodsDAO
from app.db.database import async_session_maker
from app.db.schemas import GoodsFilter
from loguru import logger

from app.vk_updater.utils import add_market_card



async def add_product_to_vk_from_db():
    async with async_session_maker() as session:
        products = await GoodsDAO.find_all(session,GoodsFilter())
    for product in products:
        if product.vk_item_id is None:
            item_id = await add_market_card(product.name,
                                            product.description,
                                            product.category_id,
                                            product.sku,
                                            product.price,
                                            product.count,
                                            product.vk_picture_id)
            async with async_session_maker() as session:
                await GoodsDAO.update(session,GoodsFilter(id=product.id),GoodsFilter(vk_item_id=item_id) )
            logger.info(f"Added product {product.id} to VK")
        else:
            logger.info(f"Product {product.id} already has vk_id {product.vk_id}")
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(add_product_to_vk_from_db())
    loop.close()