from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.session import Session, SessionCreate, SessionUpdate, Event
from app.services.session_service import SessionService

router = APIRouter()


@router.post("/", response_model=Session)
async def create_session(session: SessionCreate):
    """Create a new session"""
    try:
        session_service = SessionService()
        return await session_service.create_session(session)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get session by ID"""
    try:
        session_service = SessionService()
        session = await session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{session_id}", response_model=Session)
async def update_session(session_id: str, session_update: SessionUpdate):
    """Update session information"""
    try:
        session_service = SessionService()
        updated_session = await session_service.update_session(session_id, session_update)
        if not updated_session:
            raise HTTPException(status_code=404, detail="Session not found")
        return updated_session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/events")
async def add_event_to_session(session_id: str, event: Event):
    """Add an event to a session"""
    try:
        session_service = SessionService()
        updated_session = await session_service.add_event(session_id, event)
        if not updated_session:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Event added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[Session])
async def get_user_sessions(user_id: str, skip: int = 0, limit: int = 100):
    """Get all sessions for a user"""
    try:
        session_service = SessionService()
        return await session_service.get_user_sessions(user_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        session_service = SessionService()
        success = await session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
