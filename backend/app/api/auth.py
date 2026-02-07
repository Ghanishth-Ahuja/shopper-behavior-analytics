from fastapi import APIRouter, HTTPException, Depends, status
from app.models.auth import DashboardUserCreate, DashboardUserLogin, Token, DashboardUser
from app.utils.security import security_manager
from app.database.mongodb import MongoDB, Collections
from datetime import datetime, timedelta
from app.config.settings import settings

router = APIRouter()

@router.post("/register", response_model=DashboardUser)
async def register(user_in: DashboardUserCreate):
    db = MongoDB.get_database()
    # Check if user exists
    existing_user = await db[Collections.DASHBOARD_USERS].find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = security_manager.hash_password(user_in.password)
    
    # Create user document
    user_dict = user_in.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password
    user_dict["created_at"] = datetime.utcnow()
    
    result = await db[Collections.DASHBOARD_USERS].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    return DashboardUser(**user_dict)

@router.post("/login", response_model=Token)
async def login(user_in: DashboardUserLogin):
    db = MongoDB.get_database()
    user = await db[Collections.DASHBOARD_USERS].find_one({"email": user_in.email})
    
    if not user or not security_manager.verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security_manager.create_access_token(
        data={"sub": str(user["email"]), "id": str(user["_id"])},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=DashboardUser)
async def get_me(current_user_payload: dict = Depends(security_manager.verify_token)):
    db = MongoDB.get_database()
    user = await db[Collections.DASHBOARD_USERS].find_one({"email": current_user_payload["sub"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return DashboardUser(**user)
