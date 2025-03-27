from loguru import logger
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from app.db.base import BaseDAO
from app.db.models import Goods, GoodsCategory, User
from sqlalchemy.ext.asyncio import AsyncSession
class UserDAO(BaseDAO[User]):
    model = User

class GoodsCategoryDAO(BaseDAO[GoodsCategory]):
    model = GoodsCategory

class GoodsDAO(BaseDAO[Goods]):
    model = Goods

    @classmethod
    async def find_available_by_category(cls, session: AsyncSession, category_id: int) -> list[Goods]:
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
            logger.error(f"Ошибка при получении доступных товаров для категории {category_id}: {e}")
            raise

    @classmethod
    async def find_unavailable_by_category(cls, session: AsyncSession, category_id: int) -> list[Goods]:
        """
        Возвращает список товаров, у которых count == 0 или count равен None,
        с фильтром по category_id.
        """
        try:
            query = (
                select(cls.model)
                 .where(
                        or_(cls.model.count == None, cls.model.count == 0)  
                )
                .where(cls.model.category_id == category_id)
            )
            result = await session.execute(query)
            records = result.scalars().all()
            return records
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении доступных товаров для категории {category_id}: {e}")
            raise