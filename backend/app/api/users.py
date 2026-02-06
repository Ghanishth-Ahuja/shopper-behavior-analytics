from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.database.mongodb import MongoDB, Collections

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_service = UserService()
        return await user_service.create_user(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user_service = UserService()
        user = await user_service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    try:
        user_service = UserService()
        updated_user = await user_service.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/segment")
async def get_user_segment(user_id: str):
    """Get user's segment information"""
    try:
        user_service = UserService()
        segment_info = await user_service.get_user_segment(user_id)
        if not segment_info:
            raise HTTPException(status_code=404, detail="User segment not found")
        return segment_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    try:
        user_service = UserService()
        return await user_service.get_users(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        user_service = UserService()
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
