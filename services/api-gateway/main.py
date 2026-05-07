"""
API Gateway for SOC Correlation Engine Microservices Architecture
Handles routing, authentication, rate limiting, and service discovery
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
import consul
import redis
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import logging
import asyncio
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

app = FastAPI(title="SOC API Gateway", version="2.0.0")

# Configuration
CONSUL_HOST = "consul"
REDIS_HOST = "redis"
JWT_SECRET = "your-super-secret-jwt-key-change-in-production"

# Initialize connections
consul_client = consul.Consul(host=CONSUL_HOST, port=8500)
redis_client = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

# Service registry
SERVICES = {
    "alert-service": "http://alert-service:8001",
    "correlation-service": "http://correlation-service:8002",
    "analytics-service": "http://analytics-service:8003",
    "ml-service": "http://ml-service:8004",
    "threat-hunting-service": "http://threat-hunting-service:8005",
    "compliance-service": "http://compliance-service:8006",
    "frontend-service": "http://frontend-service:3000"
}

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        current = self.redis.get(key)
        if current is None:
            self.redis.setex(key, window, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        self.redis.incr(key)
        return True

rate_limiter = RateLimiter(redis_client)

async def get_service_url(service_name: str) -> Optional[str]:
    """Get service URL from Consul service discovery"""
    try:
        services = consul_client.health.service(service_name, passing=True)[1]
        if services:
            service = services[0]
            address = service['Service']['Address']
            port = service['Service']['Port']
            return f"http://{address}:{port}"
    except Exception as e:
        logger.error(f"Error getting service {service_name}: {e}")
    
    # Fallback to hardcoded URLs
    return SERVICES.get(service_name)

async def verify_token(request: Request) -> Optional[Dict[str, Any]]:
    """Verify JWT token from request"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and metrics"""
    start_time = asyncio.get_event_loop().time()
    
    # Rate limiting
    client_ip = request.client.host
    if not await rate_limiter.is_allowed(f"rate_limit:{client_ip}", 100, 60):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"}
        )
    
    response = await call_next(request)
    process_time = asyncio.get_event_loop().time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Prometheus metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(process_time)
    
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

@app.get("/services")
async def list_services():
    """List all registered services"""
    try:
        services = consul_client.agent.services()
        return {"services": services}
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        return {"services": SERVICES}

async def proxy_request(request: Request, service_name: str, path: str):
    """Proxy request to microservice"""
    service_url = await get_service_url(service_name)
    if not service_url:
        raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
    
    # Verify authentication for protected routes
    if path not in ["/health", "/metrics"]:
        user_data = await verify_token(request)
        if not user_data:
            raise HTTPException(status_code=401, detail="Authentication required")
    
    # Prepare request
    url = f"{service_url}{path}"
    headers = dict(request.headers)
    headers.pop("host", None)
    
    # Add user context to headers
    if user_data:
        headers["X-User-ID"] = str(user_data.get("user_id"))
        headers["X-User-Role"] = user_data.get("role", "user")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if request.method == "GET":
                response = await client.get(url, headers=headers, params=request.query_params)
            elif request.method == "POST":
                body = await request.body()
                response = await client.post(url, headers=headers, content=body)
            elif request.method == "PUT":
                body = await request.body()
                response = await client.put(url, headers=headers, content=body)
            elif request.method == "DELETE":
                response = await client.delete(url, headers=headers)
            elif request.method == "PATCH":
                body = await request.body()
                response = await client.patch(url, headers=headers, content=body)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
        
        # Return response
        return JSONResponse(
            status_code=response.status_code,
            content=response.json(),
            headers=dict(response.headers)
        )
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error(f"Error proxying request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Alert service routes
@app.api_route("/api/alerts/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def alert_service_proxy(request: Request, path: str):
    return await proxy_request(request, "alert-service", f"/{path}")

# Correlation service routes
@app.api_route("/api/correlations/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def correlation_service_proxy(request: Request, path: str):
    return await proxy_request(request, "correlation-service", f"/{path}")

# Analytics service routes
@app.api_route("/api/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def analytics_service_proxy(request: Request, path: str):
    return await proxy_request(request, "analytics-service", f"/{path}")

# ML service routes
@app.api_route("/api/ml/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def ml_service_proxy(request: Request, path: str):
    return await proxy_request(request, "ml-service", f"/{path}")

# Threat hunting service routes
@app.api_route("/api/threat-hunting/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def threat_hunting_service_proxy(request: Request, path: str):
    return await proxy_request(request, "threat-hunting-service", f"/{path}")

# Compliance service routes
@app.api_route("/api/compliance/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def compliance_service_proxy(request: Request, path: str):
    return await proxy_request(request, "compliance-service", f"/{path}")

# Authentication endpoint
@app.post("/auth/login")
async def login(credentials: Dict[str, str]):
    """Authenticate user and return JWT token"""
    username = credentials.get("username")
    password = credentials.get("password")
    
    # Simplified authentication - in production, verify against user database
    if username and password:
        payload = {
            "user_id": username,
            "role": "admin",  # Simplified role assignment
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/auth/refresh")
async def refresh_token(request: Request):
    """Refresh JWT token"""
    user_data = await verify_token(request)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    payload = {
        "user_id": user_data.get("user_id"),
        "role": user_data.get("role"),
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
