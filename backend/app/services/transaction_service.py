from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.database.mongodb import MongoDB, Collections
from bson import ObjectId


class TransactionService:
    """Service for transaction management operations"""
    
    def __init__(self):
        self.db = MongoDB.get_database()
    
    async def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        """Create a new transaction"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            
            # Check if transaction already exists
            existing_transaction = await transactions_collection.find_one({"transaction_id": transaction_data.transaction_id})
            if existing_transaction:
                raise ValueError(f"Transaction with ID {transaction_data.transaction_id} already exists")
            
            # Create transaction document
            transaction_dict = transaction_data.dict()
            transaction_dict["_id"] = ObjectId()
            
            # Insert transaction
            result = await transactions_collection.insert_one(transaction_dict)
            
            # Update user lifetime value
            await self._update_user_lifetime_value(transaction_data.user_id, transaction_data.total_amount)
            
            # Get created transaction
            created_transaction = await transactions_collection.find_one({"_id": result.inserted_id})
            
            return Transaction(**created_transaction)
            
        except Exception as e:
            print(f"Error creating transaction: {e}")
            raise
    
    async def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            transaction_doc = await transactions_collection.find_one({"transaction_id": transaction_id})
            
            if transaction_doc:
                return Transaction(**transaction_doc)
            return None
            
        except Exception as e:
            print(f"Error getting transaction {transaction_id}: {e}")
            return None
    
    async def update_transaction(self, transaction_id: str, transaction_update: TransactionUpdate) -> Optional[Transaction]:
        """Update transaction information"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            
            # Prepare update data
            update_data = transaction_update.dict(exclude_unset=True)
            if not update_data:
                return await self.get_transaction(transaction_id)
            
            # Update transaction
            result = await transactions_collection.update_one(
                {"transaction_id": transaction_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return await self.get_transaction(transaction_id)
            
            return None
            
        except Exception as e:
            print(f"Error updating transaction {transaction_id}: {e}")
            return None
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """Delete a transaction"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            result = await transactions_collection.delete_one({"transaction_id": transaction_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting transaction {transaction_id}: {e}")
            return False
    
    async def get_user_transactions(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions for a user"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find({"user_id": user_id}).skip(skip).limit(limit)
            transactions = await cursor.to_list(length=None)
            
            return [Transaction(**transaction) for transaction in transactions]
            
        except Exception as e:
            print(f"Error getting user transactions for {user_id}: {e}")
            return []
    
    async def get_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """Get all transactions with pagination"""
        try:
            transactions_collection = self.db[Collections.TRANSACTIONS]
            cursor = transactions_collection.find().skip(skip).limit(limit)
            transactions = await cursor.to_list(length=None)
            
            return [Transaction(**transaction) for transaction in transactions]
            
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    async def get_transaction_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get transaction analytics for a user"""
        try:
            from datetime import timedelta
            
            transactions_collection = self.db[Collections.TRANSACTIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = transactions_collection.find({
                "user_id": user_id,
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return {
                    "user_id": user_id,
                    "period_days": days,
                    "total_transactions": 0,
                    "total_spent": 0,
                    "avg_order_value": 0
                }
            
            total_transactions = len(transactions)
            total_spent = sum(t.get("total_amount", 0) for t in transactions)
            avg_order_value = total_spent / total_transactions
            
            # Calculate daily spending
            daily_spending = {}
            for transaction in transactions:
                date = transaction.get("timestamp", datetime.utcnow()).date()
                amount = transaction.get("total_amount", 0)
                daily_spending[str(date)] = daily_spending.get(str(date), 0) + amount
            
            # Get most purchased categories
            category_counts = {}
            for transaction in transactions:
                items = transaction.get("items", [])
                for item in items:
                    product_id = item.get("product_id")
                    category = await self._get_product_category(product_id)
                    if category:
                        category_counts[category] = category_counts.get(category, 0) + 1
            
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                "user_id": user_id,
                "period_days": days,
                "total_transactions": total_transactions,
                "total_spent": total_spent,
                "avg_order_value": avg_order_value,
                "daily_spending": daily_spending,
                "top_categories": [{"category": cat, "count": count} for cat, count in top_categories]
            }
            
        except Exception as e:
            print(f"Error getting transaction analytics for {user_id}: {e}")
            return {"error": str(e)}
    
    async def get_revenue_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get overall revenue analytics"""
        try:
            from datetime import timedelta
            
            transactions_collection = self.db[Collections.TRANSACTIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = transactions_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            transactions = await cursor.to_list(length=None)
            
            if not transactions:
                return {
                    "period_days": days,
                    "total_revenue": 0,
                    "total_transactions": 0,
                    "avg_order_value": 0,
                    "unique_customers": 0
                }
            
            total_transactions = len(transactions)
            total_revenue = sum(t.get("total_amount", 0) for t in transactions)
            avg_order_value = total_revenue / total_transactions
            
            # Unique customers
            unique_customers = len(set(t.get("user_id") for t in transactions))
            
            # Daily revenue
            daily_revenue = {}
            for transaction in transactions:
                date = transaction.get("timestamp", datetime.utcnow()).date()
                amount = transaction.get("total_amount", 0)
                daily_revenue[str(date)] = daily_revenue.get(str(date), 0) + amount
            
            # Top customers by revenue
            customer_revenue = {}
            for transaction in transactions:
                user_id = transaction.get("user_id")
                amount = transaction.get("total_amount", 0)
                customer_revenue[user_id] = customer_revenue.get(user_id, 0) + amount
            
            top_customers = sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "period_days": days,
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "avg_order_value": avg_order_value,
                "unique_customers": unique_customers,
                "daily_revenue": daily_revenue,
                "top_customers": [{"user_id": uid, "revenue": revenue} for uid, revenue in top_customers]
            }
            
        except Exception as e:
            print(f"Error getting revenue analytics: {e}")
            return {"error": str(e)}
    
    async def get_category_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get performance analytics by product category"""
        try:
            from datetime import timedelta
            
            transactions_collection = self.db[Collections.TRANSACTIONS]
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            cursor = transactions_collection.find({
                "timestamp": {"$gte": start_date, "$lte": end_date}
            })
            transactions = await cursor.to_list(length=None)
            
            category_stats = {}
            
            for transaction in transactions:
                items = transaction.get("items", [])
                for item in items:
                    product_id = item.get("product_id")
                    category = await self._get_product_category(product_id)
                    
                    if category:
                        if category not in category_stats:
                            category_stats[category] = {
                                "revenue": 0,
                                "quantity": 0,
                                "transactions": 0,
                                "unique_customers": set()
                            }
                        
                        price = item.get("price", 0)
                        quantity = item.get("quantity", 1)
                        
                        category_stats[category]["revenue"] += price * quantity
                        category_stats[category]["quantity"] += quantity
                        category_stats[category]["transactions"] += 1
                        category_stats[category]["unique_customers"].add(transaction.get("user_id"))
            
            # Convert sets to counts and sort
            category_performance = []
            for category, stats in category_stats.items():
                category_performance.append({
                    "category": category,
                    "revenue": stats["revenue"],
                    "quantity": stats["quantity"],
                    "transactions": stats["transactions"],
                    "unique_customers": len(stats["unique_customers"]),
                    "avg_price_per_item": stats["revenue"] / stats["quantity"] if stats["quantity"] > 0 else 0
                })
            
            # Sort by revenue
            category_performance.sort(key=lambda x: x["revenue"], reverse=True)
            
            return {
                "period_days": days,
                "category_performance": category_performance
            }
            
        except Exception as e:
            print(f"Error getting category performance: {e}")
            return {"error": str(e)}
    
    async def _update_user_lifetime_value(self, user_id: str, amount: float) -> None:
        """Update user's lifetime value"""
        try:
            users_collection = self.db[Collections.USERS]
            await users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"lifetime_value": amount}}
            )
        except Exception as e:
            print(f"Error updating user lifetime value: {e}")
    
    async def _get_product_category(self, product_id: str) -> Optional[str]:
        """Get category for a product"""
        try:
            products_collection = self.db[Collections.PRODUCTS]
            product = await products_collection.find_one({"product_id": product_id})
            return product.get("category") if product else None
        except Exception:
            return None
    
    async def get_customer_lifetime_value_distribution(self) -> Dict[str, Any]:
        """Get distribution of customer lifetime values"""
        try:
            users_collection = self.db[Collections.USERS]
            cursor = users_collection.find({})
            users = await cursor.to_list(length=None)
            
            ltvs = [user.get("lifetime_value", 0) for user in users]
            
            if not ltvs:
                return {"error": "No users found"}
            
            # Calculate percentiles
            ltvs_sorted = sorted(ltvs)
            n = len(ltvs_sorted)
            
            percentiles = {
                "min": ltvs_sorted[0],
                "p25": ltvs_sorted[int(n * 0.25)],
                "p50": ltvs_sorted[int(n * 0.5)],
                "p75": ltvs_sorted[int(n * 0.75)],
                "p90": ltvs_sorted[int(n * 0.9)],
                "p95": ltvs_sorted[int(n * 0.95)],
                "max": ltvs_sorted[-1],
                "mean": sum(ltvs) / n,
                "total_customers": n
            }
            
            # Create buckets
            buckets = {
                "0-100": 0,
                "100-500": 0,
                "500-1000": 0,
                "1000-5000": 0,
                "5000+": 0
            }
            
            for ltv in ltvs:
                if ltv < 100:
                    buckets["0-100"] += 1
                elif ltv < 500:
                    buckets["100-500"] += 1
                elif ltv < 1000:
                    buckets["500-1000"] += 1
                elif ltv < 5000:
                    buckets["1000-5000"] += 1
                else:
                    buckets["5000+"] += 1
            
            return {
                "percentiles": percentiles,
                "buckets": buckets
            }
            
        except Exception as e:
            print(f"Error getting LTV distribution: {e}")
            return {"error": str(e)}
