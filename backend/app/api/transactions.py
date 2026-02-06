from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/", response_model=Transaction)
async def create_transaction(transaction: TransactionCreate):
    """Create a new transaction"""
    try:
        transaction_service = TransactionService()
        return await transaction_service.create_transaction(transaction)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get transaction by ID"""
    try:
        transaction_service = TransactionService()
        transaction = await transaction_service.get_transaction(transaction_id)
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(transaction_id: str, transaction_update: TransactionUpdate):
    """Update transaction information"""
    try:
        transaction_service = TransactionService()
        updated_transaction = await transaction_service.update_transaction(transaction_id, transaction_update)
        if not updated_transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated_transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[Transaction])
async def get_user_transactions(user_id: str, skip: int = 0, limit: int = 100):
    """Get all transactions for a user"""
    try:
        transaction_service = TransactionService()
        return await transaction_service.get_user_transactions(user_id, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Transaction])
async def get_transactions(skip: int = 0, limit: int = 100):
    """Get all transactions with pagination"""
    try:
        transaction_service = TransactionService()
        return await transaction_service.get_transactions(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}")
async def delete_transaction(transaction_id: str):
    """Delete a transaction"""
    try:
        transaction_service = TransactionService()
        success = await transaction_service.delete_transaction(transaction_id)
        if not success:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
