from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class SegmentBase(BaseModel):
    segment_id: str
    segment_name: str
    characteristics: Dict[str, Any] = {}
    top_categories: List[str] = []
    price_sensitivity: str  # "low", "medium", "high"
    avg_lifetime_value: float = 0.0
    size: int = 0
    description: Optional[str] = None


class SegmentCreate(SegmentBase):
    pass


class SegmentUpdate(BaseModel):
    segment_name: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    top_categories: Optional[List[str]] = None
    price_sensitivity: Optional[str] = None
    avg_lifetime_value: Optional[float] = None
    size: Optional[int] = None
    description: Optional[str] = None


class SegmentInDB(SegmentBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Segment(SegmentBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SegmentInsight(BaseModel):
    segment_id: str
    segment_name: str
    key_behaviors: List[str]
    preferences: Dict[str, float]
    pain_points: List[str]
    recommendations: List[str]
    conversion_rate: float
    avg_order_value: float
    churn_risk: str
