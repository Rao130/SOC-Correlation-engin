import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.log_service import LogService
from app.models.log import LogLevel, LogCategory
from app.core.database import init_db

async def create_test_logs():
    """Create some test logs for testing"""
    
    # Initialize database
    db_manager = await init_db()
    
    # Create log service
    log_service = LogService(db_manager)
    await log_service.start()
    
    # Create test logs
    test_logs = [
        (LogLevel.INFO, LogCategory.SYSTEM, "System started successfully", "main", "lifespan"),
        (LogLevel.INFO, LogCategory.DATABASE, "Database connection established", "database", "connect"),
        (LogLevel.WARNING, LogCategory.AUTH, "Failed login attempt", "auth", "login"),
        (LogLevel.ERROR, LogCategory.API, "API request failed", "api", "handle_request"),
        (LogLevel.INFO, LogCategory.ALERT, "New alert received", "alerts", "process_alert"),
        (LogLevel.CRITICAL, LogCategory.SECURITY, "Security breach detected", "security", "monitor"),
        (LogLevel.INFO, LogCategory.CORRELATION, "Alert correlation completed", "correlation", "analyze"),
        (LogLevel.WARNING, LogCategory.PERFORMANCE, "High response time detected", "performance", "monitor"),
        (LogLevel.ERROR, LogCategory.WEBSOCKET, "WebSocket connection lost", "websocket", "handle_disconnect"),
        (LogLevel.INFO, LogCategory.REPUTATION, "Reputation database updated", "reputation", "update"),
    ]
    
    for level, category, message, module, function in test_logs:
        await log_service.log(
            level=level,
            category=category,
            message=message,
            module=module,
            function=function,
            user_id="test_user",
            ip_address="127.0.0.1",
            request_id=f"req_{len(test_logs)}",
            duration_ms=100.5
        )
    
    # Flush buffer
    await log_service.flush_buffer()
    
    print(f"Created {len(test_logs)} test logs")
    
    await log_service.stop()

if __name__ == "__main__":
    asyncio.run(create_test_logs())
