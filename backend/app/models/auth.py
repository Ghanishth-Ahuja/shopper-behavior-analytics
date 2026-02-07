from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from .user import PyObjectId

class DashboardUserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "viewer"  # viewer, admin, editor

class DashboardUserCreate(DashboardUserBase):
    password: str

class DashboardUserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DashboardUser(DashboardUserBase):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
