import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Column, DateTime,Boolean, Enum, ForeignKey, Integer,String
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
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)


class Goods(Base):
    __tablename__ = 'goods'
    id = Column(Integer, primary_key=True)

    category_id = Column(Integer, ForeignKey('goods_category.category_id'))
    offerID:Mapped[str]
    name :Mapped[str]
    description:Mapped[str]
    sku:Mapped[Optional[str]]
    price:Mapped[int]
    count:Mapped[Optional[int]]
    picture:Mapped[Optional[str]]

    goods_cat = relationship("GoodsCategory", back_populates="the_goods")

class GoodsCategory(Base):
    __tablename__ = 'goods_category'
    id = Column(Integer, primary_key=True)

    category_id = Column(Integer, unique=True)
    name = Column(String)

    # Связь с объявлениями
    the_goods = relationship("Goods", back_populates="goods_cat")