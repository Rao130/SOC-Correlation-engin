from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import os
from dotenv import load_dotenv

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging
from app.api.routes import auth, alerts, correlation, reputation, dashboard, maps, analytics, logs
from app.services.alert_processor import AlertProcessor
from app.services.correlation_engine import CorrelationEngine
from app.services.reputation_service import ReputationService
from app.services.websocket_service import WebSocketManager
from app.services.log_service import LogService

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Security
security = HTTPBearer()

# Global variables for services
alert_processor = None
correlation_engine = None
reputation_service = None
websocket_manager = None
log_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SOC Correlation Engine...")
    
    # Initialize database
    db_manager = await init_db()
    logger.info("Database initialized")
    
    # Initialize services
    global alert_processor, correlation_engine, reputation_service, websocket_manager, log_service
    
    alert_processor = AlertProcessor()
    correlation_engine = CorrelationEngine(db_manager)  # Pass database manager
    reputation_service = ReputationService()
    websocket_manager = WebSocketManager()
    log_service = LogService(db_manager)
    
    # Initialize log service
    await log_service.start()
    logs.initialize_log_service(log_service)
    
    # Start background services
    await alert_processor.start()
    await correlation_engine.start()
    await reputation_service.start()
    
    logger.info("All services started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SOC Correlation Engine...")
    
    if alert_processor:
        await alert_processor.stop()
    if correlation_engine:
        await correlation_engine.stop()
    if reputation_service:
        await reputation_service.stop()
    if log_service:
        await log_service.stop()
    
    logger.info("All services stopped")

# Create FastAPI app
app = FastAPI(
    title="SOC Correlation Engine",
    description="Industry-ready SOC alert fatigue reduction system with correlation, context, reputation database, and criticality analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(correlation.router, prefix="/api/correlation", tags=["Correlation"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["Reputation"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dashboard not found")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "alert_processor": alert_processor.is_running() if alert_processor else False,
            "correlation_engine": correlation_engine.is_running() if correlation_engine else False,
            "reputation_service": reputation_service.is_running() if reputation_service else False,
            "websocket_manager": websocket_manager.is_connected() if websocket_manager else False,
            "log_service": log_service.is_running() if log_service else False
        }
    }

@app.get("/api/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        stats = {
            "alerts": {
                "total": await alert_processor.get_total_alerts() if alert_processor else 0,
                "new": await alert_processor.get_new_alerts() if alert_processor else 0,
                "investigating": await alert_processor.get_investigating_alerts() if alert_processor else 0,
                "resolved": await alert_processor.get_resolved_alerts() if alert_processor else 0
            },
            "correlations": {
                "total": await correlation_engine.get_total_correlations() if correlation_engine else 0,
                "active": await correlation_engine.get_active_correlations() if correlation_engine else 0
            },
            "reputation": {
                "total_entities": await reputation_service.get_total_entities() if reputation_service else 0,
                "malicious": await reputation_service.get_malicious_count() if reputation_service else 0,
                "suspicious": await reputation_service.get_suspicious_count() if reputation_service else 0
            },
            "system": {
                "uptime": asyncio.get_event_loop().time(),
                "memory_usage": os.getmeminfo().rss if hasattr(os, 'getmeminfo') else 0,
                "cpu_usage": 0  # Would need psutil for actual CPU usage
            }
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system statistics")

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages
            await websocket_manager.handle_message(websocket, data)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket_manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
