from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from loguru import logger
from app.bot.common.messages import TEXTS
from app.bot.keyboards.inline_kb import link_about_us_button
from app.bot.keyboards.markup_kb import MainKeyboard
from app.bot.middlewares.is_admin import CheckIsAdmin
from app.db.dao import UserDAO
from app.db.database import async_session_maker
from app.db.models import User
from app.db.schemas import TelegramIDModel, UserModel
from app.config import admins, bot
from app.bot.routers.admin_routers.main_admin_router import admin_router
from app.bot.routers.user_routers.main_user_router import user_router

main_router = Router()
main_router.include_router(user_router)

admin_router.message.middleware(CheckIsAdmin())
main_router.include_router(admin_router)


@main_router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user_id = message.from_user.id
        async with async_session_maker() as session:
            user_info = await UserDAO.find_one_or_none(
                session=session, filters=TelegramIDModel(telegram_id=user_id)
            )
        if user_info:
            msg = "заглушка"
            async with async_session_maker() as session:
                await UserDAO.update(
                    session=session,
                    filters=TelegramIDModel(telegram_id=user_id),
                    values=UserModel.model_validate(user_info.to_dict()),
                )
            await message.answer(
                msg, reply_markup=MainKeyboard.build_main_kb(user_info.role)
            )
            return
        if user_id in admins:
            values = UserModel(
                telegram_id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                phone_number=None,
                role=User.Role.admin,
            )
            async with async_session_maker() as session:
                await UserDAO.add(session=session, values=values)
            await message.answer(
                "Привет администрации",
                reply_markup=MainKeyboard.build_main_kb(values.role),
            )
            return
        values = UserModel(
            telegram_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            phone_number=None,
            role=User.Role.user,
        )
        async with async_session_maker() as session:
            await UserDAO.add(session=session, values=values)
        msg = "заглушка"
        await message.answer(msg, reply_markup=MainKeyboard.build_main_kb(values.role))
        for admin in admins:
            await bot.send_message(
                admin,
                f"К тебе зашел новый юзер {message.from_user.first_name} [id: {message.from_user.id}]",
            )

    except Exception as e:
        logger.error(
            f"Ошибка при выполнении команды /start для пользователя {message.from_user.id}: {e}"
        )
        await message.answer("что-то пошло не так")


@main_router.message(F.text == MainKeyboard.get_user_kb_texts().get("about_us"))
async def cmd_about_us(message: Message):
    await message.answer(TEXTS.get("about_us"), reply_markup=link_about_us_button())
