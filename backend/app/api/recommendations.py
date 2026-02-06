from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from app.services.recommendation_service import RecommendationService

router = APIRouter()


class RecommendationResponse(BaseModel):
    product_id: str
    score: float
    reason: str
    segment_boost: float = 0.0
    real_time_boost: float = 0.0


@router.get("/user/{user_id}", response_model=List[RecommendationResponse])
async def get_user_recommendations(
    user_id: str, 
    limit: int = 10, 
    category: Optional[str] = None,
    price_range: Optional[str] = None
):
    """Get personalized recommendations for a user"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_user_recommendations(
            user_id=user_id,
            limit=limit,
            category=category,
            price_range=price_range
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/segment/{segment_id}", response_model=List[RecommendationResponse])
async def get_segment_recommendations(
    segment_id: str, 
    limit: int = 10,
    category: Optional[str] = None
):
    """Get recommendations for a user segment"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_segment_recommendations(
            segment_id=segment_id,
            limit=limit,
            category=category
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/similar/{product_id}", response_model=List[RecommendationResponse])
async def get_similar_products(product_id: str, limit: int = 10):
    """Get similar products based on content and collaborative filtering"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_similar_products(product_id, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/trending", response_model=List[RecommendationResponse])
async def get_trending_products(limit: int = 10, category: Optional[str] = None):
    """Get trending products"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_trending_products(limit, category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/frequently-bought-together/{product_id}", response_model=List[RecommendationResponse])
async def get_frequently_bought_together(product_id: str, limit: int = 5):
    """Get products frequently bought together with the given product"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_frequently_bought_together(product_id, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/explain/{user_id}/{product_id}")
async def explain_recommendation(user_id: str, product_id: str):
    """Explain why a product is recommended to a user"""
    try:
        recommendation_service = RecommendationService()
        explanation = await recommendation_service.explain_recommendation(user_id, product_id)
        if not explanation:
            raise HTTPException(status_code=404, detail="Recommendation explanation not found")
        return explanation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/feedback")
async def record_recommendation_feedback(
    user_id: str, 
    product_id: str, 
    feedback: str,  # "click", "purchase", "ignore"
    position: int
):
    """Record feedback for recommendation improvement"""
    try:
        recommendation_service = RecommendationService()
        await recommendation_service.record_feedback(user_id, product_id, feedback, position)
        return {"message": "Feedback recorded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/performance")
async def get_recommendation_performance():
    """Get recommendation system performance metrics"""
    try:
        recommendation_service = RecommendationService()
        return await recommendation_service.get_performance_metrics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
