from typing import List, Optional, Dict, Any
from app.models.product import Product, ProductCreate, ProductUpdate
from app.database.mongodb import MongoDB, Collections
from bson import ObjectId


class ProductService:
    """Service for product management operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Check if product already exists
            existing_product = await products_collection.find_one({"product_id": product_data.product_id})
            if existing_product:
                raise ValueError(f"Product with ID {product_data.product_id} already exists")
            
            # Create product document
            product_dict = product_data.dict()
            product_dict["_id"] = ObjectId()
            product_dict["created_at"] = datetime.utcnow()
            product_dict["updated_at"] = datetime.utcnow()
            
            # Insert product
            result = await products_collection.insert_one(product_dict)
            
            # Get created product
            created_product = await products_collection.find_one({"_id": result.inserted_id})
            
            return Product(**created_product)
            
        except Exception as e:
            print(f"Error creating product: {e}")
            raise
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            product_doc = await products_collection.find_one({"product_id": product_id})
            
            if product_doc:
                return Product(**product_doc)
            return None
            
        except Exception as e:
            print(f"Error getting product {product_id}: {e}")
            return None
    
    async def update_product(self, product_id: str, product_update: ProductUpdate) -> Optional[Product]:
        """Update product information"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Prepare update data
            update_data = product_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_product(product_id)
            
            update_data["updated_at"] = datetime.utcnow()
            
            # Update product
            result = await products_collection.update_one(
                {"product_id": product_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_product(product_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating product {product_id}: {e}")
            return None
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            result = await products_collection.delete_one({"product_id": product_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")
            return False
    
    async def get_products(self, skip: int = 0, limit: int = 100, category: Optional[str] = None, brand: Optional[str] = None) -> List[Product]:
        """Get all products with optional filtering"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Build filter
            filter_dict = {}
            if category:
                filter_dict["category"] = category
            if brand:
                filter_dict["brand"] = brand
            
            cursor = products_collection.find(filter_dict).skip(skip).limit(limit)
            products = await cursor.to_list(length=None)
            
            return [Product(**product) for product in products]
            
        except Exception as e:
            print(f"Error getting products: {e}")
            return []
    
    async def get_products_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by category"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            cursor = products_collection.find({"category": category}).skip(skip).limit(limit)
            products = await cursor.to_list(length=None)
            
            return [Product(**product) for product in products]
            
        except Exception as e:
            print(f"Error getting products by category {category}: {e}")
            return []
    
    async def get_product_analytics(self, product_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a product"""
        try:
            analytics = {}
            
            # Get product info
            product = await self.get_product(product_id)
            if not product:
                return {"error": "Product not found"}
            
            analytics["product_info"] = {
                "product_id": product.product_id,
                "category": product.category,
                "sub_category": product.sub_category,
                "brand": product.brand
            }
            
            # Get transaction analytics
            transactions_collection = self.db[Collections.TRANSACTIONS]
            pipeline = [
                {"$match": {"items.product_id": product_id}},
                {"$unwind": "$items"},
                {"$match": {"items.product_id": product_id}},
                {"$group": {
                    "_id": None,
                    "total_quantity": {"$sum": "$items.quantity"},
                    "total_revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                    "total_transactions": {"$sum": 1},
                    "avg_price": {"$avg": "$items.price"},
                    "unique_customers": {"$addToSet": "$user_id"}
                }},
                {"$project": {
                    "total_quantity": 1,
                    "total_revenue": 1,
                    "total_transactions": 1,
                    "avg_price": 1,
                    "unique_customers": {"$size": "$unique_customers"}
                }}
            ]
            
            cursor = transactions_collection.aggregate(pipeline)
            transaction_results = await cursor.to_list(length=None)
            
            if transaction_results:
                analytics["transaction_analytics"] = transaction_results[0]
            else:
                analytics["transaction_analytics"] = {
                    "total_quantity": 0,
                    "total_revenue": 0,
                    "total_transactions": 0,
                    "avg_price": 0,
                    "unique_customers": 0
                }
            
            # Get review analytics
            reviews_collection = self.db[Collections.REVIEWS]
            cursor = reviews_collection.find({"product_id": product_id})
            reviews = await cursor.to_list(length=None)
            
            if reviews:
                avg_rating = sum(r.get("rating", 0) for r in reviews) / len(reviews)
                rating_distribution = {}
                for review in reviews:
                    rating = review.get("rating", 0)
                    rating_distribution[rating] = rating_distribution.get(rating, 0) + 1
                
                analytics["review_analytics"] = {
                    "total_reviews": len(reviews),
                    "avg_rating": avg_rating,
                    "rating_distribution": rating_distribution
                }
            else:
                analytics["review_analytics"] = {
                    "total_reviews": 0,
                    "avg_rating": 0,
                    "rating_distribution": {}
                }
            
            # Get view analytics
            sessions_collection = self.db[Collections.SESSIONS]
            pipeline = [
                {"$match": {"events.product_id": product_id}},
                {"$unwind": "$events"},
                {"$match": {"events.product_id": product_id, "events.type": "view"}},
                {"$group": {
                    "_id": None,
                    "total_views": {"$sum": 1},
                    "unique_viewers": {"$addToSet": "$user_id"}
                }},
                {"$project": {
                    "total_views": 1,
                    "unique_viewers": {"$size": "$unique_viewers"}
                }}
            ]
            
            cursor = sessions_collection.aggregate(pipeline)
            view_results = await cursor.to_list(length=None)
            
            if view_results:
                analytics["view_analytics"] = view_results[0]
            else:
                analytics["view_analytics"] = {
                    "total_views": 0,
                    "unique_viewers": 0
                }
            
            # Calculate conversion rate
            total_views = analytics["view_analytics"]["total_views"]
            total_transactions = analytics["transaction_analytics"]["total_transactions"]
            
            if total_views > 0:
                analytics["conversion_rate"] = (total_transactions / total_views) * 100
            else:
                analytics["conversion_rate"] = 0
            
            return analytics
            
        except Exception as e:
            print(f"Error getting product analytics for {product_id}: {e}")
            return {"error": str(e)}
    
    async def search_products(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name, category, brand"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Create search filter
            search_filter = {
                "$or": [
                    {"product_id": {"$regex": query, "$options": "i"}},
                    {"category": {"$regex": query, "$options": "i"}},
                    {"sub_category": {"$regex": query, "$options": "i"}},
                    {"brand": {"$regex": query, "$options": "i"}}
                ]
            }
            
            cursor = products_collection.find(search_filter).skip(skip).limit(limit)
            products = await cursor.to_list(length=None)
            
            return [Product(**product) for product in products]
            
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            categories = await products_collection.distinct('category')
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    async def get_brands(self) -> List[str]:
        """Get all unique brands"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            brands = await products_collection.distinct('brand')
            return [brand for brand in brands if brand]  # Filter out None/empty
        except Exception as e:
            print(f"Error getting brands: {e}")
            return []
    
    async def get_top_products(self, metric: str = "revenue", limit: int = 10, category: Optional[str] = None) -> List[Dict]:
        """Get top products by various metrics"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            
            # Build match stage
            match_stage = {"$unwind": "$items"}
            if category:
                # Need to join with products to filter by category
                match_stage = {
                    "$lookup": {
                        "from": "products",
                        "localField": "items.product_id",
                        "foreignField": "product_id",
                        "as": "product_info"
                    }
                }
                pipeline = [
                    match_stage,
                    {"$unwind": "$product_info"},
                    {"$match": {"product_info.category": category}},
                    {"$group": {
                        "_id": "$items.product_id",
                        "total_revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                        "total_quantity": {"$sum": "$items.quantity"},
                        "total_transactions": {"$sum": 1}
                    }},
                    {"$sort": {f"total_{metric}": -1}},
                    {"$limit": limit}
                ]
            else:
                pipeline = [
                    match_stage,
                    {"$group": {
                        "_id": "$items.product_id",
                        "total_revenue": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}},
                        "total_quantity": {"$sum": "$items.quantity"},
                        "total_transactions": {"$sum": 1}
                    }},
                    {"$sort": {f"total_{metric}": -1}},
                    {"$limit": limit}
                ]
            
            cursor = transactions_collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            
            # Get product details
            top_products = []
            for result in results:
                product_id = result["_id"]
                product = await self.get_product(product_id)
                
                if product:
                    top_products.append({
                        "product_id": product_id,
                        "product_info": {
                            "category": product.category,
                            "brand": product.brand,
                            "sub_category": product.sub_category
                        },
                        "metrics": {
                            "total_revenue": result["total_revenue"],
                            "total_quantity": result["total_quantity"],
                            "total_transactions": result["total_transactions"]
                        }
                    })
            
            return top_products
            
        except Exception as e:
            print(f"Error getting top products: {e}")
            return []
    
    async def update_product_price(self, product_id: str, new_price: float) -> bool:
        """Update product price and maintain price history"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            
            # Get current product
            product = await self.get_product(product_id)
            if not product:
                return False
            
            # Add new price to history
            price_history = product.price_history.copy()
            price_history.append({
                "price": new_price,
                "timestamp": datetime.utcnow()
            })
            
            # Update product
            result = await products_collection.update_one(
                {"product_id": product_id},
                {
                    "$set": {
                        "price_history": price_history,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            print(f"Error updating product price for {product_id}: {e}")
            return False
