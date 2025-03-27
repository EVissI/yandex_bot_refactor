﻿from datetime import datetime
from decimal import Decimal
from functools import wraps
import re
import uuid
from loguru import logger

from sqlalchemy import func, TIMESTAMP, inspect, text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from app.config import settings

engine = create_async_engine(url=str(settings.DB_URL))
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    def to_dict(self, exclude_none: bool = False):
        """
        Преобразует объект модели в словарь.

        Args:
            exclude_none (bool): Исключать ли None значения из результата

        Returns:
            dict: Словарь с данными объекта
        """
        result = {}
        for column in inspect(self.__class__).columns:
            value = getattr(self, column.key)

            # Преобразование специальных типов данных
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = float(value)
            elif isinstance(value, uuid.UUID):
                value = str(value)

            # Добавляем значение в результат
            if not exclude_none or value is not None:
                result[column.key] = value

        return result