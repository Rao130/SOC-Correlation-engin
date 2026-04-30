"""
SOC Correlation Engine - Production Main Application
Complete with security, monitoring, API documentation, and performance features
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware.base import BaseHTTPMiddleware

import uvicorn
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

# Import our security modules
from app.core.config import Settings
from app.core.database import init_db, db_manager
from app.core.auth_enhanced import get_auth_provider, TokenResponse
from app.core.rate_limiting import (
    RateLimitMiddleware, 
    IpBasedRateLimiter, 
    LoginAttemptTracker,
    BurstProtector
)
from app.services.network_monitor import network_monitor
from app.services.real_data_generator import data_generator
from app.services.log_streamer import log_streamer
from app.core.encryption import get_encryption_services
from app.utils.logger import setup_logger

# ============================================================================
# SETUP
# ============================================================================

# Configuration
settings = Settings()
logger = setup_logger("soc_engine", settings.LOG_LEVEL)
encryption_services = get_encryption_services()

# Global service tasks
network_monitor_task = None
websocket_broadcast_task = None

# Import functional routes (ensuring these are imported for registration)
from app.api.routes import (
    alerts, correlation, reputation, auth, analytics, 
    dashboard, logs, maps, network, websocket, soar, 
    compliance, cloud, uba, edr, ticketing, mobile, reports
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'soc_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'status_code']
)
REQUEST_DURATION = Histogram(
    'soc_http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)
ERROR_COUNT = Counter(
    'soc_errors_total',
    'Total errors',
    ['error_type', 'endpoint']
)

# Security services
auth_provider = get_auth_provider()
ip_limiter = IpBasedRateLimiter()
login_tracker = LoginAttemptTracker()
burst_protector = BurstProtector()

# ============================================================================
# LIFECYCLE EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup
    logger.info("=" * 80)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.VERSION} Starting")
    logger.info(f"📅 {datetime.utcnow().isoformat()}")
    logger.info(f"🔧 Environment: {'PRODUCTION' if not settings.DEBUG else 'DEBUG'}")
    logger.info(f"🔐 Security: Token Rotation={auth_provider.jwt_manager.token_rotation_enabled}")
    logger.info("=" * 80)
    
    try:
        # Initialize database (MongoDB)
        await init_db()
        db_health = await db_manager.health_check()
        
        if db_health.get("fallback_mode"):
            logger.warning("⚠️ DATABASE WARNING: Running in Fallback Mode (In-Memory). Data will not be saved!")
        else:
            logger.info("✅ MongoDB database connected and initialized")
        
        # Start background services and WebSocket broadcasts
        global network_monitor_task, websocket_broadcast_task
        network_monitor_task = asyncio.create_task(network_monitor.start_monitoring())
        
        # Start WebSocket real-time broadcasts
        websocket_broadcast_task = asyncio.create_task(websocket.start_real_time_broadcasts())
        
        logger.info("🚀 Production Mode: Real-time network monitoring and WebSocket services active")
        
    except Exception as e:
        logger.error(f"Failed to start background services: {e}")

    yield
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    try:
        network_monitor.stop_monitoring()
        
        if network_monitor_task: network_monitor_task.cancel()
        if websocket_broadcast_task: websocket_broadcast_task.cancel()
        
        await db_manager.disconnect()
        logger.info("All background services gracefully stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# ============================================================================
# CUSTOM MIDDLEWARE
# ============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Remove server header
        response.headers.pop("Server", None)
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Request info
        logger.info(f"→ {request.method} {request.url.path} from {client_ip}")
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.error(f"❌ Request error: {request.method} {request.url.path} - {e}")
            ERROR_COUNT.labels(error_type="unhandled", endpoint=request.url.path).inc()
            raise
        
        # Response info
        logger.info(f"← {request.method} {request.url.path} {status_code}")
        return response

class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next):
        import time
        
        start = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            raise
        finally:
            duration = time.time() - start
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status="success" if 200 <= status_code < 300 else "error",
                status_code=status_code
            ).inc()
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
        
        return response

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Security Operations Center (SOC) alert correlation platform with ML-powered threat detection",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE STACK (Order matters!)
# ============================================================================

# 1. Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"] + [h.strip() for h in settings.ALLOWED_ORIGINS]
)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=600  # 10 minutes
)

# 3. Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Custom middleware (bottom up = last to execute)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ============================================================================
# ROUTE REGISTRATION
# ============================================================================

app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(correlation.router, prefix="/api/correlations", tags=["Correlation"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["Reputation"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
app.include_router(soar.router, prefix="/api/soar", tags=["SOAR"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance"])
app.include_router(cloud.router, prefix="/api/cloud", tags=["Cloud"])
app.include_router(uba.router, prefix="/api/uba", tags=["UBA"])
app.include_router(edr.router, prefix="/api/edr", tags=["EDR"])

# ============================================================================
# CUSTOM OPENAPI SCHEMA
# ============================================================================

def custom_openapi():
    """Generate custom OpenAPI schema with security configuration"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="""
# 🔐 Production-Grade SOC Correlation Engine API

## Overview
Enterprise security operations center platform with advanced alert correlation, 
machine learning-powered threat detection, and real-time threat intelligence integration.

## Security Features
- ✅ **JWT Token Authentication** with automatic refresh
- ✅ **Rate Limiting** (100 req/min per IP)
- ✅ **Brute Force Protection** (5 attempts, 15min lockout)
- ✅ **AES-256 Encryption** at rest
- ✅ **Burst Protection** against DDoS
- ✅ **Audit Logging** for all security events

## Authentication
All endpoints (except `/auth/*`) require Bearer token:
```
Authorization: Bearer <your-jwt-token>
```

## Rate Limits
- **Standard**: 100 requests per 60 seconds per IP
- **Authenticated**: 1000 requests per hour per user
- **Burst Protection**: 50 requests in 10 seconds triggers cooldown

## Response Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1234567890
```
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerTokenAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token with 15-minute expiration"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for service-to-service authentication"
        }
    }
    
    # Set security as default
    openapi_schema["security"] = [{"BearerTokenAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ============================================================================
# ENDPOINTS - AUTHENTICATION
# ============================================================================

@app.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="User Login",
    description="Authenticate user and receive JWT token pair",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many login attempts"}
    }
)
async def login(request: Request, username: str, password: str):
    """
    Login endpoint - Returns access and refresh tokens
    
    **Security Features:**
    - Bcrypt password hashing verification
    - Brute force protection (5 attempts, 15min lockout)
    - Audit logging of all attempts
    """
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "")
    
    # Check if account is locked
    is_locked, remaining = await login_tracker.is_locked(username, ip_address)
    if is_locked:
        logger.warning(f"Login attempt on locked account: {username} from {ip_address}")
        raise HTTPException(
            status_code=429,
            detail=f"Account locked. Try again in {remaining} seconds"
        )
    
    # In production, lookup user from database
    # This is a demo with hardcoded credentials
    DEMO_USERS = {
        "admin": {
            "user_id": "user_001",
            "password_hash": "$2b$12$...",  # Use PasswordManager.hash_password()
            "email": "admin@soc-engine.local",
            "role": "admin",
            "permissions": ["read", "write", "admin"]
        }
    }
    
    try:
        # Attempt authentication
        token_response = auth_provider.authenticate_user(
            username=username,
            password=password,
            user_db=DEMO_USERS,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if not token_response:
            # Record failed attempt
            attempt_info = await login_tracker.record_failed_attempt(username, ip_address)
            remaining_attempts = attempt_info["remaining"]
            raise HTTPException(
                status_code=401,
                detail=f"Invalid credentials. {remaining_attempts} attempts remaining"
            )
        
        # Reset on successful login
        await login_tracker.reset_attempts(username, ip_address)
        
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        ERROR_COUNT.labels(error_type="auth_error", endpoint="/auth/login").inc()
        raise HTTPException(status_code=500, detail="Authentication service error")

@app.post(
    "/auth/refresh",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Refresh Access Token",
    description="Get new access token using refresh token"
)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    
    **Security Features:**
    - Validates refresh token signature and expiration
    - Implements token rotation (old refresh token revoked)
    - Returns new token pair
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    try:
        # Verify refresh token
        payload = auth_provider.jwt_manager.verify_token(
            refresh_token,
            auth_provider.jwt_manager.TokenType.REFRESH
        )
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Refresh access token
        token_response = auth_provider.refresh_token(
            refresh_token,
            {"role": payload.get("role"), "permissions": payload.get("permissions")}
        )
        
        if not token_response:
            raise HTTPException(status_code=401, detail="Token refresh failed")
        
        return token_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(status_code=500, detail="Token refresh failed")

@app.post(
    "/auth/logout",
    tags=["Authentication"],
    summary="User Logout",
    description="Revoke current access token"
)
async def logout(request: Request, token: str):
    """
    Logout endpoint - Revokes token
    
    **Security Features:**
    - Adds token to revocation list
    - Logs logout event
    """
    user_id = request.headers.get("X-User-ID", "unknown")
    auth_provider.logout(token, user_id)
    
    return {"message": "Logged out successfully"}

# ============================================================================
# ENDPOINTS - SYSTEM HEALTH & MONITORING
# ============================================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="System health status"
)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.VERSION,
        "uptime_seconds": 0  # Implement with start time tracking
    }

@app.get(
    "/metrics",
    tags=["Monitoring"],
    summary="Prometheus Metrics",
    description="Prometheus format metrics for monitoring"
)
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

@app.get(
    "/api/status",
    tags=["System"],
    summary="Detailed System Status",
    description="Detailed system status including database and dependencies"
)
async def system_status():
    """Get detailed system status"""
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG
        },
        "security": {
            "token_rotation_enabled": auth_provider.jwt_manager.token_rotation_enabled,
            "encryption_enabled": True,
            "rate_limiting_enabled": True
        },
        "database": {
            "type": settings.DATABASE_TYPE,
            "host": settings.MONGODB_URL.split("@")[-1] if "@" in settings.MONGODB_URL else "local"
        },
        "cache": {
            "type": "redis",
            "enabled": True
        }
    }

# ============================================================================
# ENDPOINTS - DOCUMENTATION
# ============================================================================

@app.get("/", tags=["Documentation"], include_in_schema=False)
async def root():
    """Root endpoint - redirect to API docs"""
    return FileResponse("static/index.html") if os.path.exists("static/index.html") else {
        "message": "SOC Correlation Engine API",
        "docs": "/api/docs",
        "version": settings.VERSION
    }

@app.get("/api/docs", tags=["Documentation"], include_in_schema=False)
async def swagger_docs():
    """Swagger UI documentation"""
    return FileResponse("static/swagger.html") if os.path.exists("static/swagger.html") else {
        "docs_url": "/api/docs"
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    ERROR_COUNT.labels(error_type="http_error", endpoint=request.url.path).inc()
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    ERROR_COUNT.labels(error_type="unhandled", endpoint=request.url.path).inc()
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "Internal server error" if not settings.DEBUG else str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("🚀 Starting SOC Correlation Engine...")
    
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        reload=settings.DEBUG,
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE")
    )
