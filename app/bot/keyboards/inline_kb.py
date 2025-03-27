from typing import Optional
from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from app.db.models import GoodsCategory,Goods

class ChooseCategory(CallbackData, prefix="choose_cat"):
    category_id:int    
    selected_product_sheet_type:int

class GoodsList(CallbackData, prefix="choose_product"):
    page:Optional[int]
    action:str
    category_id:Optional[int]
    product_id:Optional[int]
    selected_product_sheet_type:int

class BuyByArticul(CallbackData, prefix="buy_by_articul"):
    product_id:int

def show_category_inl_kb(category_list:list[GoodsCategory],selected_product_sheet_type:str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not category_list:
        kb.button(text='К сожалению, список пуст',callback_data=ChooseCategory(
            category_id=None,
        ).pack())
    for category in category_list:
        kb.button(text=category.name,callback_data=ChooseCategory(
            category_id=category.category_id,
            selected_product_sheet_type = selected_product_sheet_type
        ).pack())
    kb.adjust(1)
    return kb.as_markup()


def buy_button(goods:Goods) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Купить',callback_data=BuyByArticul(
        category_id=goods.category_id,
    ).pack())
    kb.adjust(1)
    return kb.as_markup()


def link_about_us_button() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🌐 Мы в ВК',url='https://vk.com/kubikkubikru')
    kb.button(text='🛒 Мы в Яндекс Маркете',url='https://market.yandex.ru/business--kubik-kubik/121482691?generalContext=t%3DshopInShop%3Bi%3D1%3Bbi%3D121482691%3B&rs=eJwzEv3EKMTBKLDwEKsEg0bL5xNyGgdmnZQDAE3yB9Q%2C&searchContext=sins_ctx')
    kb.button(text='📦 Мы в Авито',url='https://www.avito.ru/user/092af343bd36e5ba4592ed8aa8b31611/profile?src=sharing')
    kb.button(text='🏠 Наш сайт',web_app=WebAppInfo(url ='https://kubik-kubik.ru/sale/'))  
    kb.adjust(1)
    return kb.as_markup()


def show_product_inl_kb(goods_list:list[Goods], product_id:int, selected_product_sheet_type:int, category_id:int = None,
                        page = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    pagin_counter = 0 
    if page > 0:
        pagin_counter +=1
        kb.button(text='<-',callback_data=GoodsList(
            page= page-1,
            action='Pagination',
            category_id=category_id,
            product_id = None,
            selected_product_sheet_type = selected_product_sheet_type
        ).pack())
    if page < len(goods_list)-1:
        pagin_counter +=1
        kb.button(text='->',callback_data=GoodsList(
            page= page+1,
            action='Pagination',
            category_id=category_id,
            product_id = None,
            selected_product_sheet_type = selected_product_sheet_type
        ).pack())
    if selected_product_sheet_type == 1:
        kb.button(text='Купить',url='https://market.yandex.ru/business--kubik-kubik/121482691?generalContext=t%3DshopInShop%3Bi%3D1%3Bbi%3D121482691%3B&rs=eJwzEv3EKMTBKLDwEKsEg0bL5xNyGgdmnZQDAE3yB9Q%2C&searchContext=sins_ctx',
                callback_data=GoodsList(
                page=None,
                action='Buy',
                category_id=category_id,
                product_id=product_id,
                selected_product_sheet_type = selected_product_sheet_type
            ).pack())
    if selected_product_sheet_type == 2:
        kb.button(text='Заказать',url='https://market.yandex.ru/business--kubik-kubik/121482691?generalContext=t%3DshopInShop%3Bi%3D1%3Bbi%3D121482691%3B&rs=eJwzEv3EKMTBKLDwEKsEg0bL5xNyGgdmnZQDAE3yB9Q%2C&searchContext=sins_ctx',
                callback_data=GoodsList(
                page=None,
                action='Buy',
                category_id=category_id,
                product_id=product_id,
                selected_product_sheet_type = selected_product_sheet_type
            ).pack())
    kb.button(text='Назад',callback_data=GoodsList(
            page=None,
            action='Back',
            category_id=category_id,
            product_id=None,
            selected_product_sheet_type = selected_product_sheet_type
        ).pack())
    if pagin_counter != 0:
        kb.adjust(pagin_counter,1,1)
    else: 
        kb.adjust(1,1)
    return kb.as_markup() 