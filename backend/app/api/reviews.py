from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.review import Review, ReviewCreate, ReviewUpdate, ReviewAnalysis
from app.services.review_service import ReviewService

router = APIRouter()


@router.post("/", response_model=Review)
async def create_review(review: ReviewCreate):
    """Create a new review"""
    try:
        review_service = ReviewService()
        return await review_service.create_review(review)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{review_id}", response_model=Review)
async def get_review(review_id: str):
    """Get review by ID"""
    try:
        review_service = ReviewService()
        review = await review_service.get_review(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        return review
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{review_id}", response_model=Review)
async def update_review(review_id: str, review_update: ReviewUpdate):
    """Update review information"""
    try:
        review_service = ReviewService()
        updated_review = await review_service.update_review(review_id, review_update)
        if not updated_review:
            raise HTTPException(status_code=404, detail="Review not found")
        return updated_review
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/product/{product_id}", response_model=List[Review])
async def get_product_reviews(product_id: str, skip: int = 0, limit: int = 100):
    """Get all reviews for a product"""
    try:
        review_service = ReviewService()
        return await review_service.get_product_reviews(product_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze", response_model=ReviewAnalysis)
async def analyze_review(review_id: str):
    """Analyze review sentiment and aspects"""
    try:
        review_service = ReviewService()
        analysis = await review_service.analyze_review(review_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Review not found")
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/product/{product_id}/insights")
async def get_product_insights(product_id: str):
    """Get aggregated insights for a product"""
    try:
        review_service = ReviewService()
        insights = await review_service.get_product_insights(product_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Review])
async def get_reviews(skip: int = 0, limit: int = 100):
    """Get all reviews with pagination"""
    try:
        review_service = ReviewService()
        return await review_service.get_reviews(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{review_id}")
async def delete_review(review_id: str):
    """Delete a review"""
    try:
        review_service = ReviewService()
        success = await review_service.delete_review(review_id)
        if not success:
            raise HTTPException(status_code=404, detail="Review not found")
        return {"message": "Review deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
