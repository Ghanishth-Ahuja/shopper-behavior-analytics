from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class TransactionItem(BaseModel):
    product_id: str
    quantity: int = 1
    price: float
    discount: float = 0.0


class TransactionBase(BaseModel):
    transaction_id: str
    user_id: str
    items: List[TransactionItem]
    total_amount: float
    discount_amount: float = 0.0
    payment_method: Optional[str] = None
    shipping_address: Optional[Dict[str, Any]] = None
    timestamp: datetime
    status: str = "completed"  # "pending", "completed", "cancelled", "refunded"


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    items: Optional[List[TransactionItem]] = None
    total_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    payment_method: Optional[str] = None
    status: Optional[str] = None


class TransactionInDB(TransactionBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")


class Transaction(TransactionBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
