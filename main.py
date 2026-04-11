from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, db_manager
from app.api.routes import alerts, correlation, reputation, auth
from app.core.logging import logger

# Global service instances
log_service_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SOC Correlation Engine...")
    
    try:
        # Initialize database (MongoDB)
        await init_db()
        logger.info("MongoDB database initialized")
        
        logger.info("Core services started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start some services: {e}")
        # Continue without problematic services
        logger.info("Continuing with basic functionality...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down SOC Correlation Engine...")
    
    try:
        # Disconnect database
        await db_manager.disconnect()
        
        logger.info("All services stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="SOC Correlation Engine",
    description="Industry-ready SOC alert fatigue reduction system with MongoDB backend",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include API routes
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(correlation.router, prefix="/api/correlations", tags=["Correlation"])
app.include_router(reputation.router, prefix="/api/reputation", tags=["Reputation"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main dashboard"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="""
        <html>
            <head><title>SOC Correlation Engine</title></head>
            <body>
                <h1>SOC Correlation Engine</h1>
                <p>Dashboard not found. Please check static files.</p>
            </body>
        </html>
        """)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_health = await db_manager.health_check()
        return {
            "status": "healthy",
            "database": db_health,
            "version": "1.0.0"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "1.0.0"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
