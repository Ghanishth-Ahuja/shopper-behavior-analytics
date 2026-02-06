from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.services.analytics_service import AnalyticsService

router = APIRouter()


class AffinityMatrixResponse(BaseModel):
    segment_id: str
    segment_name: str
    category_affinities: Dict[str, float]
    total_users: int


class CategoryLiftResponse(BaseModel):
    category: str
    lift_score: float
    baseline_conversion: float
    segment_conversion: float
    segment_id: str


class CustomerPersona(BaseModel):
    persona_name: str
    characteristics: List[str]
    behaviors: List[str]
    preferences: List[str]
    segment_id: str
    user_count: int


@router.get("/affinity-matrix", response_model=List[AffinityMatrixResponse])
async def get_affinity_matrix():
    """Get category affinity matrix for all segments"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_affinity_matrix()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category-lift", response_model=List[CategoryLiftResponse])
async def get_category_lift():
    """Get category lift analysis for segments"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_category_lift()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/customer-personas", response_model=List[CustomerPersona])
async def get_customer_personas():
    """Get customer personas based on behavioral analysis"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_customer_personas()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/rfm-analysis")
async def get_rfm_analysis():
    """Get RFM (Recency, Frequency, Monetary) analysis"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_rfm_analysis()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cohort-analysis")
async def get_cohort_analysis():
    """Get cohort analysis for user retention"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_cohort_analysis()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conversion-funnel")
async def get_conversion_funnel():
    """Get conversion funnel analysis"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_conversion_funnel()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/segment-performance/{segment_id}")
async def get_segment_performance(segment_id: str):
    """Get performance metrics for a specific segment"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_segment_performance(segment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/product-performance")
async def get_product_performance(category: Optional[str] = None, limit: int = 50):
    """Get product performance metrics"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_product_performance(category, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sentiment-analysis")
async def get_sentiment_analysis(category: Optional[str] = None):
    """Get sentiment analysis insights"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_sentiment_analysis(category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/price-sensitivity")
async def get_price_sensitivity_analysis():
    """Get price sensitivity analysis by segment"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_price_sensitivity_analysis()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/behavioral-patterns")
async def get_behavioral_patterns():
    """Get behavioral patterns and insights"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_behavioral_patterns()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_metrics():
    """Get overall dashboard KPI metrics"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_dashboard_metrics()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard/{segment_id}")
async def get_segment_dashboard(segment_id: str):
    """Get comprehensive dashboard data for a segment"""
    try:
        analytics_service = AnalyticsService()
        return await analytics_service.get_segment_dashboard(segment_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
