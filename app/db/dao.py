from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from app.db.base import BaseDAO
from app.db.models import Goods, GoodsCategory, User, Payment
from sqlalchemy.ext.asyncio import AsyncSession


class UserDAO(BaseDAO[User]):
    model = User


class GoodsCategoryDAO(BaseDAO[GoodsCategory]):
    model = GoodsCategory


class GoodsDAO(BaseDAO[Goods]):
    model = Goods
    @staticmethod
    async def find_all_by_name(session, name_substring: str):
        """
        Возвращает все товары, название которых содержит указанную подстроку.

        :param session: Сессия для работы с базой данных.
        :param name_substring: Подстрока для поиска в названии товара.
        :return: Список товаров, соответствующих критериям.
        """
        query = select(Goods).where(Goods.name.ilike(f"%{name_substring}%"))
        result = await session.execute(query)
        return result.scalars().all()
    
    @classmethod
    async def find_available_by_category(
        cls, session: AsyncSession, category_id: int
    ) -> list[Goods]:
        """
        Возвращает список товаров, у которых count > 0 и count не равен None,
        с фильтром по category_id.
        """
        try:
            query = (
                select(cls.model)
                .where(cls.model.count.isnot(None))
                .where(cls.model.count > 0)
                .where(cls.model.category_id == category_id)
            )
            result = await session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при получении доступных товаров для категории {category_id}: {e}"
            )
            raise

    @classmethod
    async def find_unavailable_by_category(
        cls, session: AsyncSession, category_id: int
    ) -> list[Goods]:
        """
        Возвращает список товаров, у которых count == 0 или count равен None,
        с фильтром по category_id.
        """
        try:
            query = (
                select(cls.model)
                .where(or_(cls.model.count == None, cls.model.count == 0))
                .where(cls.model.category_id == category_id)
            )
            result = await session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            logger.error(
                f"Ошибка при получении доступных товаров для категории {category_id}: {e}"
            )
            raise


class PaymentDAO(BaseDAO[Payment]):
    model = Payment
