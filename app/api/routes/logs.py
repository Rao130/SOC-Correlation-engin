from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.log import LogEntry, LogFilter, LogStats, LogLevel, LogCategory
from app.services.log_service import LogService
from app.core.database import get_db

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

@router.get("/", response_model=List[LogEntry])
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
    log_service: LogService = Depends(get_log_service)
):
    """Get logs with advanced filtering"""
    try:
        log_filter = LogFilter(
            level=level,
            category=category,
            module=module,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            request_id=request_id,
            error_code=error_code,
            tags=tags.split(',') if tags else None,
            start_time=start_time,
            end_time=end_time,
            search_text=search_text
        )
        
        logs = await log_service.get_logs(log_filter, skip=skip, limit=limit)
        return [log.dict() for log in logs]
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

def initialize_log_service(service: LogService):
    """Initialize log service for the router"""
    global log_service
    log_service = service
