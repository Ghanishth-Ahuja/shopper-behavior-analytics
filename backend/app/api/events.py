from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from app.models.session import Event
from app.services.event_service import EventService

router = APIRouter()


@router.post("/track")
async def track_event(event: Event, background_tasks: BackgroundTasks):
    """Track user events in real-time"""
    try:
        event_service = EventService()
        
        # Store event immediately
        result = await event_service.track_event(event)
        
        # Add background task for real-time feature updates
        background_tasks.add_task(
            event_service.update_user_features_realtime, 
            event.user_id, 
            event
        )
        
        return {"message": "Event tracked successfully", "event_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}")
async def get_user_events(user_id: str, skip: int = 0, limit: int = 100):
    """Get events for a specific user"""
    try:
        event_service = EventService()
        return await event_service.get_user_events(user_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/session/{session_id}")
async def get_session_events(session_id: str, skip: int = 0, limit: int = 100):
    """Get events for a specific session"""
    try:
        event_service = EventService()
        return await event_service.get_session_events(session_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/product/{product_id}")
async def get_product_events(product_id: str, skip: int = 0, limit: int = 100):
    """Get events related to a specific product"""
    try:
        event_service = EventService()
        return await event_service.get_product_events(product_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/type/{event_type}")
async def get_events_by_type(event_type: str, skip: int = 0, limit: int = 100):
    """Get events by type (view, add_to_cart, purchase, etc.)"""
    try:
        event_service = EventService()
        return await event_service.get_events_by_type(event_type, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/realtime/{user_id}")
async def get_realtime_events(user_id: str, minutes: int = 30):
    """Get recent events for real-time processing"""
    try:
        event_service = EventService()
        return await event_service.get_realtime_events(user_id, minutes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
