from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class EventBase(BaseModel):
    type: str  # "view", "add_to_cart", "purchase", "search", "filter"
    product_id: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, Any] = {}


class Event(EventBase):
    pass


class SessionBase(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[Event] = []
    device_type: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None


class SessionCreate(SessionBase):
    pass


class SessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    events: Optional[List[Event]] = None


class SessionInDB(SessionBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")


class Session(SessionBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
