from aiogram import Router
from app.bot.routers.user_routers.goods_list import goods_list_router
from app.bot.routers.user_routers.search_by_sku import search_by_sku_router
user_router = Router()
user_router.include_router(goods_list_router)
user_router.include_router(search_by_sku_router)