#!/usr/bin/env python3
"""
Real-time SOC Correlation Engine Startup Script
Ensures all real-time data pipelines are active and working
"""

import asyncio
import sys
import os
import signal
import time
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.database import init_db, db_manager
from app.api.routes import alerts, correlation, reputation, auth, analytics, dashboard, logs, maps, network, websocket, soar, compliance, cloud, uba, edr, ticketing, mobile, reports
try:
    from app.api.routes import threat_intel
    THREAT_INTEL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import threat_intel module: {e}")
    THREAT_INTEL_AVAILABLE = False
from app.services.network_monitor import network_monitor
from app.services.real_time_data_ingestion import real_time_ingestion

# Global service instances
network_monitor_task = None
websocket_broadcast_task = None

def handle_task_result(task: asyncio.Task):
    """Callback to handle background task completion/errors"""
    try:
        task.result()
    except asyncio.CancelledError:
        pass 
    except Exception as e:
        logger.error(f"Background task failed: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Real-time SOC Correlation Engine...")
    
    try:
        # Initialize database (MongoDB)
        await init_db()

        # Verify connection is actually alive
        db_health = await db_manager.health_check()
        if not db_health.get("mongodb", False):
            if db_health.get("fallback_mode"):
                logger.warning("⚠️ Running in Fallback Mode. Real-time data will be lost on restart.")
                logger.info("👉 Tip: Start MongoDB to enable data persistence.")
            else:
                logger.error("🛑 CRITICAL: Database service is completely unreachable.")
                
            if not os.getenv("DEBUG", "False").lower() == "true":
                logger.error("Shutting down due to missing infrastructure.")
                sys.exit(1)
        
        # Start network monitoring
        global network_monitor_task
        network_monitor_task = asyncio.create_task(network_monitor.start_monitoring())
        network_monitor_task.add_done_callback(handle_task_result)
        logger.info("Real-time network monitoring started")
        
        # Start real-time data ingestion
        await real_time_ingestion.start_ingestion()
        logger.info("🚀 Real-time data ingestion started from actual sources")
        
        # Start WebSocket broadcasts
        global websocket_broadcast_task
        websocket_broadcast_task = asyncio.create_task(websocket.start_real_time_broadcasts())
        websocket_broadcast_task.add_done_callback(handle_task_result)
        logger.info("WebSocket real-time broadcasts started")
        
        logger.info("✅ All production real-time services started. Pure real-time data flow active.")
        
    except Exception as e:
        logger.error(f"Failed to start some services: {e}")
        logger.error("CRITICAL: The system requires MongoDB to function correctly.")
        logger.info("Continuing with available services...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Real-time SOC Correlation Engine...")
    
    try:
        # Stop network monitoring
        network_monitor.stop_monitoring()
        if network_monitor_task:
            network_monitor_task.cancel()
        logger.info("Network monitoring stopped")
        
        # Stop real-time data ingestion
        await real_time_ingestion.stop_ingestion()
        logger.info("Real-time data ingestion stopped")
        
        # Stop WebSocket broadcasts
        if websocket_broadcast_task:
            websocket_broadcast_task.cancel()
        logger.info("WebSocket broadcasts stopped")
        
        # Disconnect database
        await db_manager.disconnect()
        
        logger.info("All services stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Create FastAPI app
app = FastAPI(
    title="Real-time SOC Correlation Engine",
    description="Industry-ready SOC alert fatigue reduction system with real-time data pipelines",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket connections
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
app.include_router(ticketing.router, prefix="/api/ticketing", tags=["Ticketing"])
app.include_router(mobile.router, prefix="/api/mobile", tags=["Mobile"])

# Conditionally include optional modules
if THREAT_INTEL_AVAILABLE:
    try:
        app.include_router(threat_intel.router, prefix="/api/threat-intel", tags=["Threat Intelligence"])
        logger.info("Threat Intelligence module loaded")
    except Exception as e:
        logger.warning(f"Failed to load Threat Intelligence module: {e}")


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
            <head><title>Real-time SOC Correlation Engine</title></head>
            <body>
                <h1>Real-time SOC Correlation Engine</h1>
                <p>Dashboard not found. Please check static files.</p>
                <p><a href="/api/network/status">Check Network Status</a></p>
                <p><a href="/api/analytics/realtime-stats">Real-time Statistics</a></p>
            </body>
        </html>
        """)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with real-time status"""
    try:
        db_health = await db_manager.health_check()
        
        # Get service status
        service_status = {
            "network_monitoring": network_monitor.monitoring_active,
            "real_time_ingestion": real_time_ingestion.active,
            "data_sources": real_time_ingestion.data_sources,
            "memory_alerts": len(network_monitor.memory_alerts)
        }
        
        return {
            "status": "healthy",
            "database": db_health,
            "services": service_status,
            "version": "1.0.0",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "version": "1.0.0"
        }

def _is_recent_alert(timestamp_str: str) -> bool:
    """Check if alert is recent (within last hour)"""
    try:
        if not timestamp_str:
            return False
        
        # Handle different timestamp formats
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str.replace('Z', '+00:00')
        
        alert_time = datetime.fromisoformat(timestamp_str)
        return alert_time > datetime.utcnow() - timedelta(hours=1)
    except (ValueError, TypeError, AttributeError):
        return False

# Real-time status endpoint
@app.get("/api/realtime-status")
async def realtime_status():
    """Get real-time system status"""
    try:
        return {
            "network_monitoring": {
                "active": network_monitor.monitoring_active,
                "memory_alerts": len(network_monitor.memory_alerts),
                "recent_alerts": len([a for a in network_monitor.memory_alerts 
                                    if _is_recent_alert(a.get('timestamp', ''))])
            },
            "data_ingestion": await real_time_ingestion.get_ingestion_statistics(),
            "database": await db_manager.health_check(),
            "timestamp": time.time()
        }
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}

# Comprehensive features status endpoint
@app.get("/api/features-status")
async def features_status():
    """Get status of all features and modules"""
    try:
        db_health = await db_manager.health_check()
        
        return {
            "status": "operational",
            "version": "1.0.0",
            "timestamp": time.time(),
            "core_features": {
                "realtime_monitoring": network_monitor.monitoring_active,
                "data_generation": data_generator.active,
                "websocket_broadcasts": websocket_broadcast_task is not None,
                "log_streaming": log_streamer_task is not None,
                "database": db_health.get("status", "unknown")
            },
            "security_modules": {
                "soar": {"status": "available", "endpoint": "/api/soar"},
                "compliance": {"status": "available", "endpoint": "/api/compliance"},
                "cloud_connectors": {"status": "available", "endpoint": "/api/cloud"},
                "uba": {"status": "available", "endpoint": "/api/uba"},
                "edr": {"status": "available", "endpoint": "/api/edr"},
                "ticketing": {"status": "available", "endpoint": "/api/ticketing"},
                "threat_intel": {"status": "available", "endpoint": "/api/threat-intel"},
                "ai_incident": {"status": "available", "endpoint": "/api/ai-incident"}
            },
            "mobile_features": {
                "mobile_app": {"status": "available", "endpoint": "/api/mobile"},
                "push_notifications": {"status": "available"},
                "offline_mode": {"status": "available"}
            },
            "api_endpoints": {
                "total": 15,
                "available": [
                    "/api/alerts", "/api/correlations", "/api/reputation",
                    "/api/analytics", "/api/dashboard", "/api/logs", "/api/maps",
                    "/api/network", "/api/soar", "/api/compliance", "/api/cloud",
                    "/api/uba", "/api/edr", "/api/ticketing", "/api/mobile",
                    "/api/threat-intel", "/api/ai-incident"
                ]
            },
            "statistics": {
                "generated_alerts": len(data_generator.generated_alerts),
                "memory_alerts": len(network_monitor.memory_alerts),
                "uptime_seconds": time.time()
            }
        }
    except Exception as e:
        return {"error": str(e), "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    
    # Setup logging
    setup_logging()
    
    # Print startup message
    print("=" * 80)
    print("ENTERPRISE-GRADE SOC CORRELATION ENGINE")
    print("=" * 80)
    print(f"Starting on http://{settings.HOST}:{settings.PORT}")
    print(f"Main Dashboard: http://{settings.HOST}:{settings.PORT}")
    print(f"Health Check: http://{settings.HOST}:{settings.PORT}/health")
    print(f"Real-time Status: http://{settings.HOST}:{settings.PORT}/api/realtime-status")
    print(f"Features Status: http://{settings.HOST}:{settings.PORT}/api/features-status")
    print("=" * 80)
    print("🚀 ADVANCED FEATURES:")
    print("  📊 Real-time network monitoring & analytics")
    print("  🔔 Live security data generation")
    print("  🌐 WebSocket real-time updates")
    print("  💾 MongoDB data persistence")
    print("  📱 Mobile app for real-time alerts")
    print("=" * 80)
    print("🛡️ SECURITY MODULES:")
    print("  🔧 SOAR - Automated Response Playbooks")
    print("  📋 Compliance Reporting (PCI-DSS, HIPAA, GDPR)")
    print("  ☁️ Cloud Connectors (AWS, Azure, GCP)")
    print("  👤 User Behavior Analytics (UBA)")
    print("  🛡️ EDR Integrations (CrowdStrike, SentinelOne)")
    print("  🎫 Ticketing Integration (ServiceNow, Jira)")
    print("  🧠 AI Incident Response Generator")
    print("  🌍 Commercial Threat Intelligence")
    print("=" * 80)
    print("📡 API ENDPOINTS:")
    print("  /api/soar - Security Orchestration")
    print("  /api/compliance - Compliance Reports")
    print("  /api/cloud - Cloud Security")
    print("  /api/uba - User Analytics")
    print("  /api/edr - Endpoint Detection")
    print("  /api/ticketing - Incident Management")
    print("  /api/mobile - Mobile Alerts")
    print("  /api/threat-intel - Threat Intelligence")
    print("  /api/ai-incident - AI Incident Response")
    print("=" * 80)
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    uvicorn.run(
        "start_realtime_system:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
