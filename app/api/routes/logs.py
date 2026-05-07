"""
Logs API Routes
Provides access to real-time security logs and log analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.log import LogEntry, LogFilter, LogStats, LogLevel, LogCategory
from app.services.log_service import LogService
from app.core.database import get_db
from app.core.logging import logger
from app.services.log_streamer import log_streamer

router = APIRouter()

# Global log service instance
log_service = None

def get_log_service():
    """Get log service instance"""
    global log_service
    return log_service

def initialize_log_service(service):
    """Initialize log service instance"""
    global log_service
    log_service = service

@router.get("", response_model=List[LogEntry])
async def get_logs(
    level: Optional[LogLevel] = Query(None),
    category: Optional[LogCategory] = Query(None),
    module: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    ip_address: Optional[str] = Query(None),
    request_id: Optional[str] = Query(None),
    error_code: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    search_text: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db = Depends(get_db)
):
    """Get logs with advanced filtering"""
    try:
        # First try to get data from the real-time log streamer
        from app.services.log_streamer import log_streamer
        
        if hasattr(log_streamer, 'generated_logs') and log_streamer.generated_logs:
            all_logs = log_streamer.generated_logs
            
            # Apply filters
            filtered_logs = all_logs
            
            if level:
                level_value = level.value if hasattr(level, 'value') else level
                filtered_logs = [log for log in filtered_logs if log.get('level') == level_value]
            if category:
                category_value = category.value if hasattr(category, 'value') else category
                filtered_logs = [log for log in filtered_logs if log.get('category') == category_value]
            if module:
                filtered_logs = [log for log in filtered_logs if log.get('module') == module]
            if user_id:
                filtered_logs = [log for log in filtered_logs if log.get('user_id') == user_id]
            if ip_address:
                filtered_logs = [log for log in filtered_logs if log.get('ip_address') == ip_address]
            if search_text:
                search_lower = search_text.lower()
                filtered_logs = [log for log in filtered_logs 
                               if search_lower in log.get('message', '').lower() or 
                                  search_lower in log.get('module', '').lower()]
            
            # Sort by timestamp (newest first) - proper datetime parsing
            def get_timestamp(log):
                ts = log.get('timestamp', '')
                try:
                    # Parse ISO format timestamp
                    return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    # Fallback to string comparison
                    return ts
            
            filtered_logs.sort(key=get_timestamp, reverse=True)
            
            # Apply pagination
            paginated_logs = filtered_logs[skip:skip + limit]
            
            logger.info(f"Returning {len(paginated_logs)} logs from memory (total: {len(filtered_logs)})")
            
            # Convert to LogEntry format
            log_entries = []
            for log in paginated_logs:
                log_entry = LogEntry(
                    id=log.get('id', ''),
                    timestamp=log.get('timestamp', ''),
                    level=log.get('level', 'INFO'),
                    category=log.get('category', 'SYSTEM'),
                    message=log.get('message', ''),
                    module=log.get('module', 'system'),
                    function=log.get('function', 'log_event'),
                    user_id=log.get('user_id', 'system'),
                    ip_address=log.get('ip_address', ''),
                    host=log.get('host', ''),
                    process=log.get('process', ''),
                    pid=log.get('pid', 0),
                    raw_log=log.get('raw_log', ''),
                    analysis=log.get('analysis', {}),
                    security_relevant=log.get('security_relevant', False)
                )
                log_entries.append(log_entry)
            
            return log_entries
        
        # Fallback to sample logs if no in-memory data
        sample_logs = [
            {
                "id": "log_1",
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "category": "system",
                "message": "System initialized successfully",
                "module": "system",
                "function": "initialize_system",
                "user_id": "system",
                "ip_address": "127.0.0.1"
            },
            {
                "id": "log_2", 
                "timestamp": datetime.utcnow().isoformat(),
                "level": "WARNING",
                "category": "performance",
                "message": "High memory usage detected",
                "module": "monitoring",
                "function": "check_memory_usage",
                "user_id": "system",
                "ip_address": "127.0.0.1"
            },
            {
                "id": "log_3",
                "timestamp": datetime.utcnow().isoformat(),
                "level": "ERROR",
                "category": "database",
                "message": "Database connection timeout",
                "module": "database",
                "function": "connect_to_database",
                "user_id": "system",
                "ip_address": "127.0.0.1"
            }
        ]
        
        # Apply limit
        return sample_logs[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@router.get("/stats")
async def get_log_stats(
    hours: int = Query(24, ge=1, le=168),
    log_service: LogService = Depends(get_log_service)
):
    """Get log statistics"""
    try:
        stats = await log_service.get_log_stats(hours=hours)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get log stats: {str(e)}")

@router.get("/levels")
async def get_log_levels():
    """Get available log levels"""
    return [{"value": level.value, "label": level.value} for level in LogLevel]

@router.get("/categories")
async def get_log_categories():
    """Get available log categories"""
    return [{"value": cat.value, "label": cat.value} for cat in LogCategory]

@router.get("/modules")
async def get_log_modules(
    log_service: LogService = Depends(get_log_service)
):
    """Get available log modules"""
    try:
        if log_service.database_manager:
            db = log_service.database_manager.get_database()
            collection = db.logs  # Get the logs collection
            pipeline = [
                {"$group": {"_id": "$module", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 50}
            ]
            results = await collection.aggregate(pipeline).to_list()
            return [{"value": r["_id"], "label": r["_id"], "count": r["count"]} for r in results]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get modules: {str(e)}")

@router.get("/error-codes")
async def get_error_codes(
    log_service: LogService = Depends(get_log_service)
):
    """Get common error codes"""
    try:
        if log_service.database_manager:
            db = log_service.database_manager.get_database()
            collection = db.logs  # Get the logs collection
            pipeline = [
                {"$match": {"error_code": {"$ne": None}}},
                {"$group": {"_id": "$error_code", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            results = await collection.aggregate(pipeline).to_list()
            return [{"value": r["_id"], "label": r["_id"], "count": r["count"]} for r in results]
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get error codes: {str(e)}")

@router.get("/search")
async def search_logs(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    log_service: LogService = Depends(get_log_service)
):
    """Search logs by text"""
    try:
        log_filter = LogFilter(search_text=query)
        logs = await log_service.get_logs(log_filter, skip=skip, limit=limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search logs: {str(e)}")

@router.get("/export")
async def export_logs(
    format: str = Query("json", regex="^(json|csv)$"),
    level: Optional[LogLevel] = Query(None),
    category: Optional[LogCategory] = Query(None),
    module: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    search_text: Optional[str] = Query(None),
    log_service: LogService = Depends(get_log_service)
):
    """Export logs in specified format"""
    try:
        log_filter = LogFilter(
            level=level,
            category=category,
            module=module,
            start_time=start_time,
            end_time=end_time,
            search_text=search_text
        )
        
        exported_data = await log_service.export_logs(log_filter, format)
        
        filename = f"logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        if format == "csv":
            return PlainTextResponse(
                exported_data,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        return PlainTextResponse(
            exported_data,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export logs: {str(e)}")

@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365),
    log_service: LogService = Depends(get_log_service)
):
    """Clean up old logs"""
    try:
        await log_service.clear_old_logs(days=days)
        return {"message": f"Cleaned up logs older than {days} days"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup logs: {str(e)}")

@router.get("/unique-filters")
async def get_unique_filters(
    log_service: LogService = Depends(get_log_service)
):
    """Get unique values for advanced filtering"""
    try:
        if log_service.database_manager:
            db = log_service.database_manager.get_database()
            collection = db.logs  # Get the logs collection
            
            # Get unique users
            user_pipeline = [
                {"$match": {"user_id": {"$ne": None}}},
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            user_results = await collection.aggregate(user_pipeline).to_list()
            
            # Get unique IPs
            ip_pipeline = [
                {"$match": {"ip_address": {"$ne": None}}},
                {"$group": {"_id": "$ip_address", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            ip_results = await collection.aggregate(ip_pipeline).to_list()
            
            # Get unique tags
            tag_pipeline = [
                {"$match": {"tags": {"$ne": None}}},
                {"$unwind": "$tags"},
                {"$group": {"_id": "$tags", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 20}
            ]
            tag_results = await collection.aggregate(tag_pipeline).to_list()
            
            return {
                "users": [{"value": r["_id"], "count": r["count"]} for r in user_results],
                "ip_addresses": [{"value": r["_id"], "count": r["count"]} for r in ip_results],
                "tags": [{"value": r["_id"], "count": r["count"]} for r in tag_results]
            }
        
        return {"users": [], "ip_addresses": [], "tags": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unique filters: {str(e)}")

@router.get("/timeline")
async def get_log_timeline(
    hours: int = Query(24, ge=1, le=168),
    log_service: LogService = Depends(get_log_service)
):
    """Get log timeline data for charts"""
    try:
        timeline_data = await log_service.get_log_timeline(hours=hours)
        return {"timeline": timeline_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get timeline: {str(e)}")

@router.get("/realtime")
async def get_realtime_logs(
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    source: Optional[str] = Query(None)
):
    """Get real-time generated logs"""
    try:
        logs = log_streamer.get_recent_logs(limit=limit, severity=severity, source=source)
        return {
            "logs": logs,
            "count": len(logs),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting realtime logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get realtime logs: {str(e)}")

@router.get("/realtime/stats")
async def get_realtime_log_stats():
    """Get real-time log statistics"""
    try:
        stats = log_streamer.get_log_statistics()
        return {
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting realtime log stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get realtime log stats: {str(e)}")

@router.post("/generate")
async def generate_logs(count: int = Query(10, ge=1, le=100)):
    """Generate new log entries"""
    try:
        logs = await log_streamer.generate_log_burst(count)
        return {
            "message": f"Generated {count} log entries",
            "logs": logs,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate logs: {str(e)}")

@router.post("/start-streaming")
async def start_log_streaming():
    """Start continuous log generation"""
    try:
        if not log_streamer.active:
            # Start in background
            import asyncio
            asyncio.create_task(log_streamer.start_continuous_generation())
            return {"message": "Log streaming started"}
        else:
            return {"message": "Log streaming already active"}
    except Exception as e:
        logger.error(f"Error starting log streaming: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start log streaming: {str(e)}")

@router.post("/stop-streaming")
async def stop_log_streaming():
    """Stop continuous log generation"""
    try:
        log_streamer.stop_generation()
        return {"message": "Log streaming stopped"}
    except Exception as e:
        logger.error(f"Error stopping log streaming: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop log streaming: {str(e)}")

def initialize_log_service(service: LogService):
    """Initialize log service for router"""
    global log_service
    log_service = service
