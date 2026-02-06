from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserBase(BaseModel):
    user_id: str
    demographics: Dict[str, Any] = {}
    signup_date: datetime
    acquisition_channel: str
    lifetime_value: float = 0.0
    segment_id: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    demographics: Optional[Dict[str, Any]] = None
    acquisition_channel: Optional[str] = None
    lifetime_value: Optional[float] = None
    segment_id: Optional[str] = None


class UserInDB(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(UserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
