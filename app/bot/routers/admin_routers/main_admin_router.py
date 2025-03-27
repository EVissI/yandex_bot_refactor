from aiogram import Router

from app.bot.routers.admin_routers.update_goods import update_goods


admin_router = Router()
admin_router.include_router(update_goods)