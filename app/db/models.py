from datetime import datetime
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from typing import Optional
from app.db.database import Base


class User(Base):
    class Role(enum.Enum):
        admin = "admin"
        user = "user"

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String, default=None)
    first_name: Mapped[Optional[str]] = mapped_column(String, default=None)
    phone_number: Mapped[Optional[str]] = mapped_column(String, default=None)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)

    payments = relationship("Payment", back_populates="user")


class Goods(Base):
    __tablename__ = "goods"
    id = Column(Integer, primary_key=True)

    offerID: Mapped[str]
    name: Mapped[str]
    description: Mapped[str]
    sku: Mapped[Optional[str]]
    price: Mapped[int]
    count: Mapped[Optional[int]]
    tg_picture_id: Mapped[Optional[str]]
    vk_picture_id: Mapped[Optional[int]]
    vk_item_id:Mapped[Optional[int]]

    category_id = Column(Integer, ForeignKey("goods_category.category_id"))
    goods_cat = relationship("GoodsCategory", back_populates="the_goods")

    payments = relationship("Payment", back_populates="goods")


class GoodsCategory(Base):
    __tablename__ = "goods_category"
    id = Column(Integer, primary_key=True)

    category_id = Column(Integer, unique=True)
    name = Column(String)

    # Связь с объявлениями
    the_goods = relationship("Goods", back_populates="goods_cat")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(String, unique=True, nullable=False)  # Идентификатор платежа
    user_telegram_id = Column(
        BigInteger, ForeignKey("users.telegram_id"), nullable=False
    )  # Связь с пользователем
    goods_id = Column(Integer, ForeignKey("goods.id"), nullable=True)  # Связь с товаром
    amount = Column(Integer, nullable=False)  # Сумма платежа в копейках
    description = Column(String, nullable=True)  # Описание платежа
    status = Column(String, nullable=False)  # Статус платежа

    user = relationship("User", back_populates="payments")
    goods = relationship("Goods", back_populates="payments")
