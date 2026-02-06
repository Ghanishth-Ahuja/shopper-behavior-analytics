from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class ProductBase(BaseModel):
    product_id: str
    category: str
    sub_category: Optional[str] = None
    brand: Optional[str] = None
    attributes: Dict[str, Any] = {}
    price_history: List[Dict[str, Any]] = []


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    brand: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    price_history: Optional[List[Dict[str, Any]]] = None


class ProductInDB(ProductBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Product(ProductBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
