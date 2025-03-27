from typing import Optional

from pydantic import BaseModel

from app.db.models import User

class TelegramIDModel(BaseModel):
    telegram_id: int
    class Config:
        from_attributes = True
        
class UserModel(TelegramIDModel):
    username: Optional[str]
    first_name:Optional[str]
    role:User.Role

class UserFilterModel(BaseModel):
    telegram_id: int = None
    username: Optional[str] = None
    first_name:Optional[str] = None
    role:User.Role = None

class GoodsCategoryModel(BaseModel):
    category_id :int
    name :str

class GoodsCategoryFilter(BaseModel):
    category_id :int = None
    name :str = None

class GoodsModel(BaseModel):
    category_id:int
    offerID:str
    name:str
    description:str
    sku:Optional[str]
    price:int
    count:Optional[int]
    picture:Optional[str]

class GoodsFilter(BaseModel):
    id:int = None
    category_id:int = None
    offerID:str = None
    name:str = None
    description:str = None
    sku:Optional[str] = None
    price:int = None
    count:Optional[int] = None
    picture:Optional[str]= None