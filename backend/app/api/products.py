from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from app.models.product import Product, ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter()


@router.post("/", response_model=Product)
async def create_product(product: ProductCreate):
    """Create a new product"""
    try:
        product_service = ProductService()
        return await product_service.create_product(product)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[Product])
async def get_products(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = Query(None),
    brand: Optional[str] = Query(None)
):
    """Get all products with optional filtering"""
    try:
        product_service = ProductService()
        return await product_service.get_products(
            skip=skip, 
            limit=limit, 
            category=category, 
            brand=brand
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by ID"""
    try:
        product_service = ProductService()
        product = await product_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate):
    """Update product information"""
    try:
        product_service = ProductService()
        updated_product = await product_service.update_product(product_id, product_update)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category/{category}", response_model=List[Product])
async def get_products_by_category(category: str, skip: int = 0, limit: int = 100):
    """Get products by category"""
    try:
        product_service = ProductService()
        return await product_service.get_products_by_category(category, skip, limit)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{product_id}")
async def delete_product(product_id: str):
    """Delete a product"""
    try:
        product_service = ProductService()
        success = await product_service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
