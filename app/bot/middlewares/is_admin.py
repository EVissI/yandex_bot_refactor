from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.db.dao import UserDAO
from app.db.models import User
from app.db.database import async_session_maker
from app.db.schemas import UserFilterModel

class CheckIsAdmin(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            admins_ids = [user.telegram_id for user in await UserDAO.find_all(session,UserFilterModel(role=User.Role.admin))]
            if event.from_user.id in admins_ids:
                return await handler(event, data) 
            else:
                await event.answer(
                    'заглушка'
                )
