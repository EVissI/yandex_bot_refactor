from typing import Dict
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove,WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger

from app.db.models import User


del_kbd = ReplyKeyboardRemove()


def back_button():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Назад")
    return kb.as_markup(resize_keyboard=True)


def request_contact_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="📞 Поделиться номером", request_contact=True)
    return kb.as_markup(resize_keyboard=True)


class SearchProductKeyboard:

    __search_kb_text_dict_ru = {
        'search_by_sku':'Поиск по артикулу',
        'search_by_name':'Поиск по названию',
        'back':'назад'
    }   

    @staticmethod
    def get_search_kb_texts(key = None) -> Dict[str, str] | None:
        """
        'search_by_sku'\n
        'search_by_name'\n
        'back'
        """
        if key is not None:
            return SearchProductKeyboard.__search_kb_text_dict_ru.get(key)
        return SearchProductKeyboard.__search_kb_text_dict_ru
    
    @staticmethod
    def build_kb():
        kb = ReplyKeyboardBuilder()
        for val in SearchProductKeyboard.get_search_kb_texts().values():
            kb.button(text=val)
        return kb.as_markup(resize_keyboard=True)
    
class MainKeyboard:
    __user_kb_texts_dict_ru = {
        "goods_list": '🛍️ Просмотр товаров',
        'goods_not_in_cash': '📦 Товары на заказ',
        "search_product": "🔍 Поиск товара",
        'about_us': 'ℹ️ О нас'
    }

    __admin_kb_text_dict_ru = {
        "update_goods": "обновить список товаров"
    }
    @staticmethod
    def get_user_kb_texts(key = None) -> Dict[str, str] | None:
        """
        "goods_list"\n
        "search_product"\n
        'goods_not_in_cash'\n
        'about_us'
        """
        if key is not None:
            return MainKeyboard.__user_kb_texts_dict_ru.get(key)
        return MainKeyboard.__user_kb_texts_dict_ru

    @staticmethod
    def get_admin_kb_texts(key = None) -> Dict[str, str]:
        """
        "some_admin_button"\n
        "update_goods"
        """
        if key is not None:
            return MainKeyboard.__admin_kb_text_dict_ru.get(key)
        return MainKeyboard.__admin_kb_text_dict_ru

    @staticmethod
    def build_main_kb(user_role: User.Role) -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardBuilder()

        for val in MainKeyboard.get_user_kb_texts().values():
            kb.button(text=val)
        kb.button(text='Наш сайт',web_app=WebAppInfo(url ='https://kubik-kubik.ru/sale/'))
        if user_role == User.Role.admin:
            for val in MainKeyboard.get_admin_kb_texts().values():
                kb.button(text=val)
        kb.adjust(
            2,2,1 ,
            len(MainKeyboard.get_admin_kb_texts()),
        )

        return kb.as_markup(resize_keyboard=True)
