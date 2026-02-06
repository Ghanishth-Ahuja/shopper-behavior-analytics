from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class RFMFeatures(BaseModel):
    recency: float  # days since last purchase
    frequency: float  # number of purchases in period
    monetary: float  # total spent in period


class BrowsingFeatures(BaseModel):
    avg_session_duration: float
    pages_per_session: float
    bounce_rate: float
    cart_abandonment_rate: float
    search_frequency: float
    preferred_hour: int  # 0-23
    weekend_vs_weekday_ratio: float


class CategoryAffinity(BaseModel):
    category: str
    affinity_score: float  # 0-1


class UserFeaturesBase(BaseModel):
    user_id: str
    rfm_features: RFMFeatures
    browsing_features: BrowsingFeatures
    category_affinity_vector: List[CategoryAffinity]
    embedding_vector: List[float] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class UserFeaturesCreate(UserFeaturesBase):
    pass


class UserFeaturesUpdate(BaseModel):
    rfm_features: Optional[RFMFeatures] = None
    browsing_features: Optional[BrowsingFeatures] = None
    category_affinity_vector: Optional[List[CategoryAffinity]] = None
    embedding_vector: Optional[List[float]] = None


class UserFeaturesInDB(UserFeaturesBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")


class UserFeatures(UserFeaturesBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
