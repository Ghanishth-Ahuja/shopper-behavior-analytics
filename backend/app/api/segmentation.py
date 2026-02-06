from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.segment import Segment, SegmentCreate, SegmentUpdate, SegmentInsight
from app.services.segmentation_service import SegmentationService

router = APIRouter()


@router.post("/train")
async def train_segmentation_model(background_tasks: BackgroundTasks):
    """Train the segmentation model"""
    try:
        segmentation_service = SegmentationService()
        
        # Add background task for training
        background_tasks.add_task(segmentation_service.train_segmentation_model)
        
        return {"message": "Segmentation training started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Segment])
async def get_segments(skip: int = 0, limit: int = 100):
    """Get all segments"""
    try:
        segmentation_service = SegmentationService()
        return await segmentation_service.get_segments(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{segment_id}", response_model=Segment)
async def get_segment(segment_id: str):
    """Get segment by ID"""
    try:
        segmentation_service = SegmentationService()
        segment = await segmentation_service.get_segment(segment_id)
        if not segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return segment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/", response_model=Segment)
async def create_segment(segment: SegmentCreate):
    """Create a new segment (manual)"""
    try:
        segmentation_service = SegmentationService()
        return await segmentation_service.create_segment(segment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{segment_id}", response_model=Segment)
async def update_segment(segment_id: str, segment_update: SegmentUpdate):
    """Update segment information"""
    try:
        segmentation_service = SegmentationService()
        updated_segment = await segmentation_service.update_segment(segment_id, segment_update)
        if not updated_segment:
            raise HTTPException(status_code=404, detail="Segment not found")
        return updated_segment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{segment_id}/insights")
async def get_segment_insights(segment_id: str):
    """Get detailed insights for a segment"""
    try:
        segmentation_service = SegmentationService()
        insights = await segmentation_service.get_segment_insights(segment_id)
        if not insights:
            raise HTTPException(status_code=404, detail="Segment not found")
        return insights
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{segment_id}/users")
async def get_segment_users(segment_id: str, skip: int = 0, limit: int = 100):
    """Get users in a specific segment"""
    try:
        segmentation_service = SegmentationService()
        return await segmentation_service.get_segment_users(segment_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assign/{user_id}")
async def assign_user_to_segment(user_id: str, segment_id: str):
    """Assign a user to a segment"""
    try:
        segmentation_service = SegmentationService()
        success = await segmentation_service.assign_user_to_segment(user_id, segment_id)
        if not success:
            raise HTTPException(status_code=404, detail="User or segment not found")
        return {"message": "User assigned to segment successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{segment_id}")
async def delete_segment(segment_id: str):
    """Delete a segment"""
    try:
        segmentation_service = SegmentationService()
        success = await segmentation_service.delete_segment(segment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Segment not found")
        return {"message": "Segment deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
