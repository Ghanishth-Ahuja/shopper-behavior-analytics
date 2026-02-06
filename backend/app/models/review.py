from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from .user import PyObjectId


class ReviewBase(BaseModel):
    review_id: str
    user_id: str
    product_id: str
    rating: int  # 1-5
    review_text: str
    sentiment_score: Optional[float] = None
    extracted_aspects: Dict[str, Any] = {}
    helpful_count: int = 0
    verified_purchase: bool = False
    timestamp: datetime


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = None
    review_text: Optional[str] = None
    sentiment_score: Optional[float] = None
    extracted_aspects: Optional[Dict[str, Any]] = None
    helpful_count: Optional[int] = None


class ReviewInDB(ReviewBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Review(ReviewBase):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReviewAnalysis(BaseModel):
    review_id: str
    sentiment: str  # "positive", "negative", "neutral"
    sentiment_score: float
    aspects: Dict[str, float]  # aspect -> sentiment score
    topics: List[str]
    confidence: float
