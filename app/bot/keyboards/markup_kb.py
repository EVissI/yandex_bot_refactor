from typing import Dict
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger

from app.db.models import User


del_kbd = ReplyKeyboardRemove()


def back_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Назад")
    return kb.as_markup(resize_keyboard=True)


class MainKeyboard:
    __user_kb_texts_dict_ru = {
        "goods_list": '🛍️ Просмотр товаров',
        "search_by_sku": "🔍 Поиск по артикулу",
        'goods_not_in_cash': '📦 Товары на заказ',
        'about_us': 'ℹ️ О нас'
    }

    __admin_kb_text_dict_ru = {
        "update_goods": "обновить список товаров"
    }
    @staticmethod
    def get_user_kb_texts() -> Dict[str, str]:
        """
        "goods_list"\n
        "search_by_sku"\n
        'goods_not_in_cash'\n
        'about_us'
        """
        return MainKeyboard.__user_kb_texts_dict_ru

    @staticmethod
    def get_admin_kb_texts() -> Dict[str, str]:
        """
        "some_admin_button"\n
        "update_goods"
        """
        return MainKeyboard.__admin_kb_text_dict_ru

    @staticmethod
    def build_main_kb(user_role: User.Role) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.get_user_kb_texts().values():
            kb.button(text=val)

        if user_role == User.Role.admin:
            for val in MainKeyboard.get_admin_kb_texts().values():
                kb.button(text=val)
        kb.adjust(
            len(MainKeyboard.get_user_kb_texts()),
            len(MainKeyboard.get_admin_kb_texts()),
        )

        return kb.as_markup(resize_keyboard=True)
