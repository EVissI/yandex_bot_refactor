﻿def product_card_msg(product):
    availability = "Нет в наличии" if not product.count else f"{product.count} шт."
    description = truncate_message(product.description)
    return (
            f"🎁 <b>Карточка товара</b> 🎁\n"
            f"🔹 <b>Название:</b> {product.name}\n"
            f"💰 <b>Цена:</b> {product.price} руб.\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"📦 <b>Артикул:</b> {product.sku}\n"
            f"📊 <b>Наличие:</b> {availability}\n"
        )
def truncate_message(message: str, limit: int = 700) -> str:
    """
    Проверяет длину строки и сокращает её до указанного лимита символов,
    добавляя '...' в конце, если строка была обрезана.
    
    :param message: Исходная строка.
    :param limit: Максимальное количество символов (по умолчанию 3500).
    :return: Обрезанная строка, если она превышает лимит.
    """
    if len(message) > limit:
        return message[:limit - 3] + "..."
    return message


TEXTS = {
    'about_us': "Добро пожаловать в нашу уютный магазинчик! 🎉\n\n"
        "Мы специализируемся на продаже игрушек, чтобы радовать детей и взрослых. "
        "У нас вы найдете широкий ассортимент качественных товаров для творчества, игр и развития.\n\n"
        "📌 Наши ссылки:\n"
        "🔗 <a href = ''>ВКонтакте</a>\n"
        "🔗 <a href = ''>Яндекс Маркет</a>\n\n"
        "Спасибо, что выбираете нас! 😊",
    'start_message': "👋 Добро пожаловать в наш уютный магазин игрушек! 🎉\n\n"
    "Мы рады видеть вас здесь! У нас вы найдете:\n"
    "🔹 Широкий ассортимент игрушек\n"
    "🔹 Уникальные наборы LEGO,Mega Bloks,K'NEX и не только\n"
    "🔹 Товары для творчества и развития\n\n"
    "📌 Используйте меню ниже, чтобы:\n"
    "🛍️ Просмотреть товары\n"
    "🔍 Найти товар по артикулу\n"
    "📦 Узнать о товарах на заказ\n"
    "ℹ️ Узнать больше о нас\n\n"
    "Спасибо, что выбрали нас! 😊"
}