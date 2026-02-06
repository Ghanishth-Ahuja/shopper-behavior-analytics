from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.config.settings import settings
from app.utils.logger import get_logger
import hashlib
import secrets
import redis.asyncio as redis

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Redis client for rate limiting and token blacklisting
redis_client = None


async def get_redis_client():
    """Get Redis client"""
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.REDIS_URL)
    return redis_client


class SecurityManager:
    """Security management utilities"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def blacklist_token(token: str) -> bool:
        """Add token to blacklist"""
        try:
            r = await get_redis_client()
            
            # Extract expiration from token
            payload = jwt.decode(token, options={"verify_signature": False})
            exp = payload.get("exp")
            
            if exp:
                # Calculate TTL until expiration
                ttl = exp - int(datetime.utcnow().timestamp())
                if ttl > 0:
                    await r.setex(f"blacklist:{token}", ttl, "1")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return False
    
    @staticmethod
    async def is_token_blacklisted(token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            r = await get_redis_client()
            result = await r.get(f"blacklist:{token}")
            return result is not None
        except Exception as e:
            logger.error(f"Error checking token blacklist: {e}")
            return False
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def verify_api_key(plain_key: str, hashed_key: str) -> bool:
        """Verify API key against hash"""
        return SecurityManager.hash_api_key(plain_key) == hashed_key


class RateLimiter:
    """Rate limiting utilities"""
    
    @staticmethod
    async def check_rate_limit(
        key: str, 
        limit: int, 
        window: int = 60, 
        identifier: str = "ip"
    ) -> Dict[str, Any]:
        """Check rate limit for given key"""
        try:
            r = await get_redis_client()
            
            # Create Redis key
            redis_key = f"rate_limit:{identifier}:{key}"
            
            # Get current count
            current = await r.get(redis_key)
            
            if current is None:
                # First request in window
                await r.setex(redis_key, window, 1)
                return {
                    "allowed": True,
                    "remaining": limit - 1,
                    "reset_time": datetime.utcnow() + timedelta(seconds=window)
                }
            
            current_count = int(current)
            
            if current_count >= limit:
                # Rate limit exceeded
                ttl = await r.ttl(redis_key)
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_time": datetime.utcnow() + timedelta(seconds=ttl)
                }
            
            # Increment counter
            await r.incr(redis_key)
            await r.expire(redis_key, window)
            
            return {
                "allowed": True,
                "remaining": limit - current_count - 1,
                "reset_time": datetime.utcnow() + timedelta(seconds=window)
            }
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # Allow request if rate limiting fails
            return {
                "allowed": True,
                "remaining": limit - 1,
                "reset_time": datetime.utcnow() + timedelta(seconds=window)
            }
    
    @staticmethod
    async def check_user_rate_limit(user_id: str, endpoint: str, limit: int = 100) -> Dict[str, Any]:
        """Check rate limit for specific user and endpoint"""
        key = f"{user_id}:{endpoint}"
        return await RateLimiter.check_rate_limit(key, limit, identifier="user")
    
    @staticmethod
    async def check_ip_rate_limit(ip_address: str, limit: int = 1000) -> Dict[str, Any]:
        """Check rate limit for IP address"""
        return await RateLimiter.check_rate_limit(ip_address, limit, identifier="ip")


class DataMasking:
    """Data masking utilities for PII protection"""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""
        if "@" not in email:
            return email
        
        local, domain = email.split("@", 1)
        
        if len(local) <= 2:
            masked_local = local[0] + "*" * (len(local) - 1)
        else:
            masked_local = local[:2] + "*" * (len(local) - 2)
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""
        if len(phone) <= 4:
            return "*" * len(phone)
        
        return phone[:2] + "*" * (len(phone) - 4) + phone[-2:]
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """Mask credit card number"""
        # Remove spaces and dashes
        clean_card = card_number.replace(" ", "").replace("-", "")
        
        if len(clean_card) <= 4:
            return "*" * len(clean_card)
        
        return "*" * (len(clean_card) - 4) + clean_card[-4:]
    
    @staticmethod
    def mask_user_id(user_id: str) -> str:
        """Mask user ID"""
        if len(user_id) <= 4:
            return "*" * len(user_id)
        
        return user_id[:2] + "*" * (len(user_id) - 4) + user_id[-2:]


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "&", "\"", "'", "/"]
        sanitized = input_str
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        
        # Truncate to max length
        return sanitized[:max_length]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id:
            return False
        
        # Check for alphanumeric and underscore only
        import re
        pattern = r'^[a-zA-Z0-9_]+$'
        return re.match(pattern, user_id) is not None and len(user_id) <= 50
    
    @staticmethod
    def validate_product_id(product_id: str) -> bool:
        """Validate product ID format"""
        if not product_id:
            return False
        
        # Similar to user ID validation
        return InputValidator.validate_user_id(product_id)
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate rating (1-5)"""
        return isinstance(rating, int) and 1 <= rating <= 5
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price (positive)"""
        return isinstance(price, (int, float)) and price >= 0
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range"""
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            return False
        
        return start_date <= end_date


class SecurityHeaders:
    """Security headers for HTTP responses"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


class AuditLogger:
    """Audit logging for security events"""
    
    @staticmethod
    async def log_login_attempt(user_id: str, ip_address: str, success: bool, user_agent: str = None):
        """Log login attempt"""
        event_type = "login_success" if success else "login_failed"
        
        audit_data = {
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow()
        }
        
        # Store in audit log collection
        try:
            db = get_redis_client()  # Using Redis for fast audit logging
            await db.lpush("audit_log", str(audit_data))
            
            # Keep only last 10000 audit entries
            await db.ltrim("audit_log", 0, 9999)
            
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")
        
        # Also log to application logger
        logger.info(f"Audit: {event_type} for user {user_id} from {ip_address}")
    
    @staticmethod
    async def log_data_access(user_id: str, resource: str, action: str, ip_address: str):
        """Log data access"""
        audit_data = {
            "event_type": "data_access",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow()
        }
        
        try:
            db = await get_redis_client()
            await db.lpush("audit_log", str(audit_data))
            await db.ltrim("audit_log", 0, 9999)
        except Exception as e:
            logger.error(f"Error logging data access: {e}")
        
        logger.info(f"Audit: Data access - {action} on {resource} by user {user_id}")
    
    @staticmethod
    async def log_permission_denied(user_id: str, resource: str, action: str, ip_address: str):
        """Log permission denied event"""
        audit_data = {
            "event_type": "permission_denied",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow()
        }
        
        try:
            db = await get_redis_client()
            await db.lpush("audit_log", str(audit_data))
            await db.ltrim("audit_log", 0, 9999)
        except Exception as e:
            logger.error(f"Error logging permission denied: {e}")
        
        logger.warning(f"Audit: Permission denied - {action} on {resource} by user {user_id}")


# Initialize security components
security_manager = SecurityManager()
rate_limiter = RateLimiter()
data_masking = DataMasking()
input_validator = InputValidator()
security_headers = SecurityHeaders()
audit_logger = AuditLogger()
