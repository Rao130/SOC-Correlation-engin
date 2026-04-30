"""
Rate Limiting & Security Middleware - Production-Grade Traffic Control
Features: Redis-backed rate limiting, IP-based throttling, sliding window algorithm
"""

from fastapi import Request, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import redis
import logging
import asyncio
from functools import wraps
import json

logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITER - Sliding Window Algorithm with Redis
# ============================================================================

class RateLimiter:
    """
    Rate limiter using sliding window algorithm with Redis backend
    Supports:
    - IP-based limiting
    - User-based limiting
    - Endpoint-specific limits
    - Burst protection
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_limit: int = 100,
        default_window_seconds: int = 60
    ):
        """
        Initialize rate limiter
        
        Args:
            redis_url: Redis connection URL
            default_limit: Default requests per window
            default_window_seconds: Default window in seconds
        """
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_limit = default_limit
        self.default_window = default_window_seconds
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int = None,
        window_seconds: int = None
    ) -> Tuple[bool, Dict[str, any]]:
        """
        Check if request is within rate limit
        
        Args:
            key: Rate limit key (e.g., "user:123", "ip:192.168.1.1")
            limit: Request limit (uses default if None)
            window_seconds: Time window in seconds (uses default if None)
            
        Returns:
            Tuple of (allowed: bool, info: Dict with limit info)
        """
        limit = limit or self.default_limit
        window = window_seconds or self.default_window
        
        now = datetime.utcnow().timestamp()
        window_start = now - window
        
        try:
            # Get current request count in window
            pipeline = self.redis.pipeline()
            
            # Remove old entries
            pipeline.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(now): now})
            
            # Set expiration
            pipeline.expire(key, window + 10)
            
            results = pipeline.execute()
            current_count = results[1]  # Count after removing old entries
            
            remaining = limit - current_count
            reset_at = int(now) + window
            
            info = {
                "limit": limit,
                "remaining": max(0, remaining),
                "reset_at": reset_at,
                "current": current_count,
                "allowed": current_count < limit
            }
            
            if not info["allowed"]:
                logger.warning(f"Rate limit exceeded for key: {key}")
            
            return info["allowed"], info
            
        except Exception as e:
            logger.error(f"Rate limiter error: {e}")
            # Fail open - allow request if Redis is down
            return True, {"allowed": True, "error": str(e)}

class IpBasedRateLimiter(RateLimiter):
    """Rate limiter based on IP address"""
    
    async def check_ip_limit(
        self,
        ip_address: str,
        limit: int = 100,
        window_seconds: int = 60
    ) -> Tuple[bool, Dict]:
        """Check rate limit for IP address"""
        key = f"rate_limit:ip:{ip_address}"
        return await self.check_rate_limit(key, limit, window_seconds)

class UserBasedRateLimiter(RateLimiter):
    """Rate limiter based on user ID"""
    
    async def check_user_limit(
        self,
        user_id: str,
        limit: int = 1000,
        window_seconds: int = 3600
    ) -> Tuple[bool, Dict]:
        """Check rate limit for user"""
        key = f"rate_limit:user:{user_id}"
        return await self.check_rate_limit(key, limit, window_seconds)

class EndpointRateLimiter(RateLimiter):
    """Rate limiter for specific endpoints"""
    
    async def check_endpoint_limit(
        self,
        endpoint: str,
        ip_address: str,
        limit: int = 50,
        window_seconds: int = 60
    ) -> Tuple[bool, Dict]:
        """Check rate limit for endpoint + IP combination"""
        key = f"rate_limit:endpoint:{endpoint}:ip:{ip_address}"
        return await self.check_rate_limit(key, limit, window_seconds)

# ============================================================================
# BURST PROTECTION - DDoS & Brute Force Detection
# ============================================================================

class BurstProtector:
    """Detects and protects against burst attacks"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        burst_threshold: int = 50,  # Requests in 10 seconds
        cooldown_seconds: int = 300  # 5 minute cooldown
    ):
        """Initialize burst protector"""
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.burst_threshold = burst_threshold
        self.cooldown = cooldown_seconds
    
    async def check_burst(
        self,
        key: str
    ) -> Tuple[bool, str]:
        """
        Check if burst detected
        
        Returns:
            (is_safe: bool, message: str)
        """
        now = datetime.utcnow().timestamp()
        window_start = now - 10  # 10 second window
        
        try:
            pipeline = self.redis.pipeline()
            
            # Count recent requests
            pipeline.zcount(key, window_start, now)
            
            # Add current timestamp
            pipeline.zadd(key, {str(now): now})
            
            # Set expiration
            pipeline.expire(key, 20)
            
            results = pipeline.execute()
            recent_count = results[0]
            
            if recent_count > self.burst_threshold:
                # Set cooldown
                cooldown_key = f"{key}:cooldown"
                self.redis.setex(cooldown_key, self.cooldown, "1")
                logger.warning(f"Burst detected for key: {key}, count: {recent_count}")
                return False, f"Too many requests. Cooldown: {self.cooldown}s"
            
            # Check if in cooldown
            if self.redis.exists(f"{key}:cooldown"):
                return False, f"In cooldown period. Wait {self.cooldown}s"
            
            return True, "Safe"
            
        except Exception as e:
            logger.error(f"Burst detection error: {e}")
            return True, "Safe (error)"

# ============================================================================
# LOGIN ATTEMPT PROTECTION - Brute Force Defense
# ============================================================================

class LoginAttemptTracker:
    """Tracks login attempts to prevent brute force attacks"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_attempts: int = 5,
        lockout_seconds: int = 900  # 15 minutes
    ):
        """Initialize login attempt tracker"""
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_seconds
    
    async def record_failed_attempt(self, username: str, ip_address: str) -> Dict:
        """
        Record failed login attempt
        
        Returns:
            Dict with attempt info and lockout status
        """
        key = f"login_attempts:{username}:{ip_address}"
        attempts = int(self.redis.incr(key))
        self.redis.expire(key, 3600)  # 1 hour window
        
        locked_key = f"{key}:locked"
        
        info = {
            "attempts": attempts,
            "max_attempts": self.max_attempts,
            "remaining": max(0, self.max_attempts - attempts),
            "locked": attempts >= self.max_attempts
        }
        
        if info["locked"]:
            self.redis.setex(locked_key, self.lockout_duration, "1")
            logger.warning(f"Account locked due to failed attempts: {username} from {ip_address}")
        
        return info
    
    async def is_locked(self, username: str, ip_address: str) -> Tuple[bool, Optional[int]]:
        """
        Check if account is locked
        
        Returns:
            (is_locked: bool, remaining_lockout_seconds: int or None)
        """
        locked_key = f"login_attempts:{username}:{ip_address}:locked"
        ttl = self.redis.ttl(locked_key)
        
        return ttl > 0, ttl if ttl > 0 else None
    
    async def reset_attempts(self, username: str, ip_address: str) -> None:
        """Reset failed attempts on successful login"""
        key = f"login_attempts:{username}:{ip_address}"
        self.redis.delete(key)
        self.redis.delete(f"{key}:locked")

# ============================================================================
# MIDDLEWARE FACTORY - FastAPI Integration
# ============================================================================

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ip_limit: int = 100,
        ip_window: int = 60
    ):
        """Initialize middleware"""
        self.limiter = IpBasedRateLimiter(redis_url)
        self.ip_limit = ip_limit
        self.ip_window = ip_window
        self.burst_protector = BurstProtector(redis_url)
    
    async def __call__(self, request: Request, call_next):
        """Process request through middleware"""
        ip_address = self._get_client_ip(request)
        
        # Check burst protection
        is_safe, message = await self.burst_protector.check_burst(f"burst:{ip_address}")
        if not is_safe:
            raise HTTPException(status_code=429, detail=message)
        
        # Check IP rate limit
        allowed, info = await self.limiter.check_ip_limit(
            ip_address,
            self.ip_limit,
            self.ip_window
        )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset_at"])
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Reset at {info['reset_at']}"
            )
        
        return response
    
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Get client IP from request (handles proxies)"""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

# ============================================================================
# DEPENDENCY INJECTION - For endpoint protection
# ============================================================================

async def rate_limit_dep(
    request: Request,
    limiter: IpBasedRateLimiter = Depends(lambda: IpBasedRateLimiter())
) -> Dict:
    """Dependency for rate limit checking"""
    ip = request.client.host if request.client else "unknown"
    allowed, info = await limiter.check_ip_limit(ip, 100, 60)
    
    if not allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return info

# ============================================================================
# UTILITIES
# ============================================================================

def rate_limit_decorator(limit: int = 100, window: int = 60):
    """Decorator for rate limiting individual functions"""
    limiter = IpBasedRateLimiter()
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get IP from request context if available
            ip = "unknown"
            for arg in args:
                if isinstance(arg, Request):
                    ip = arg.client.host if arg.client else "unknown"
                    break
            
            allowed, _ = await limiter.check_ip_limit(ip, limit, window)
            if not allowed:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

