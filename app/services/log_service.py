import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.log import LogEntry, LogFilter, LogStats, LogLevel, LogCategory
from app.core.logging import setup_logging
import uuid
import re

logger = setup_logging()

class LogService:
    def __init__(self, database_manager=None):
        self.database_manager = database_manager
        self.log_buffer = []
        self.buffer_size = 100
        self._running = False
    
    async def start(self):
        """Start the log service"""
        self._running = True
        logger.info("Log service started")
    
    async def stop(self):
        """Stop the log service"""
        self._running = False
        await self.flush_buffer()
        logger.info("Log service stopped")
    
    async def log(self, level: LogLevel, category: LogCategory, message: str, 
                  module: str, function: str, line: Optional[int] = None,
                  **kwargs):
        """Add a log entry"""
        log_entry = LogEntry(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            level=level,
            category=category,
            message=message,
            module=module,
            function=function,
            line=line,
            **kwargs
        )
        
        self.log_buffer.append(log_entry.dict())
        
        if len(self.log_buffer) >= self.buffer_size:
            await self.flush_buffer()
    
    async def flush_buffer(self):
        """Flush log buffer to database"""
        if not self.log_buffer:
            return
        
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                collection = db.logs  # Get the logs collection
                for log_entry in self.log_buffer:
                    await collection.insert_one(log_entry)
            self.log_buffer.clear()
        except Exception as e:
            logger.error(f"Failed to flush log buffer: {e}")
    
    async def get_logs(self, log_filter: LogFilter, skip: int = 0, limit: int = 100) -> List[LogEntry]:
        """Get logs with filtering"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                collection = db.logs  # Get the logs collection
                query = self._build_query(log_filter)
                
                cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
                logs = await cursor.to_list()
                
                return [LogEntry(**log) for log in logs]
            return []
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    async def get_log_stats(self, hours: int = 24) -> LogStats:
        """Get log statistics"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                collection = db.logs  # Get the logs collection
                start_time = datetime.utcnow() - timedelta(hours=hours)
                
                # Total logs
                total_logs = await collection.count_documents({
                    "timestamp": {"$gte": start_time}
                })
                
                # Logs by level
                level_pipeline = [
                    {"$match": {"timestamp": {"$gte": start_time}}},
                    {"$group": {"_id": "$level", "count": {"$sum": 1}}}
                ]
                level_results = await collection.aggregate(level_pipeline).to_list()
                logs_by_level = {r["_id"]: r["count"] for r in level_results}
                
                # Logs by category
                category_pipeline = [
                    {"$match": {"timestamp": {"$gte": start_time}}},
                    {"$group": {"_id": "$category", "count": {"$sum": 1}}}
                ]
                category_results = await collection.aggregate(category_pipeline).to_list()
                logs_by_category = {r["_id"]: r["count"] for r in category_results}
                
                # Recent errors
                recent_errors = await collection.count_documents({
                    "timestamp": {"$gte": start_time},
                    "level": {"$in": ["ERROR", "CRITICAL"]}
                })
                
                # Critical alerts
                critical_alerts = await collection.count_documents({
                    "timestamp": {"$gte": start_time},
                    "level": "CRITICAL",
                    "category": "alert"
                })
                
                # Top error codes
                error_pipeline = [
                    {"$match": {"timestamp": {"$gte": start_time}, "error_code": {"$ne": None}}},
                    {"$group": {"_id": "$error_code", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                error_results = await collection.aggregate(error_pipeline).to_list()
                top_error_codes = {r["_id"]: r["count"] for r in error_results}
                
                return LogStats(
                    total_logs=total_logs,
                    logs_by_level=logs_by_level,
                    logs_by_category=logs_by_category,
                    recent_errors=recent_errors,
                    critical_alerts=critical_alerts,
                    top_error_codes=top_error_codes
                )
            
            return LogStats(
                total_logs=0,
                logs_by_level={},
                logs_by_category={},
                recent_errors=0,
                critical_alerts=0
            )
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return LogStats(
                total_logs=0,
                logs_by_level={},
                logs_by_category={},
                recent_errors=0,
                critical_alerts=0
            )
    
    def _build_query(self, log_filter: LogFilter) -> Dict[str, Any]:
        """Build MongoDB query from filter"""
        query = {}
        
        if log_filter.level:
            query["level"] = log_filter.level.value
        if log_filter.category:
            query["category"] = log_filter.category.value
        if log_filter.module:
            query["module"] = {"$regex": log_filter.module, "$options": "i"}
        if log_filter.user_id:
            query["user_id"] = log_filter.user_id
        if log_filter.session_id:
            query["session_id"] = log_filter.session_id
        if log_filter.ip_address:
            query["ip_address"] = log_filter.ip_address
        if log_filter.request_id:
            query["request_id"] = log_filter.request_id
        if log_filter.error_code:
            query["error_code"] = log_filter.error_code
        if log_filter.tags:
            query["tags"] = {"$in": log_filter.tags}
        if log_filter.start_time or log_filter.end_time:
            time_query = {}
            if log_filter.start_time:
                time_query["$gte"] = log_filter.start_time
            if log_filter.end_time:
                time_query["$lte"] = log_filter.end_time
            query["timestamp"] = time_query
        if log_filter.search_text:
            query["$or"] = [
                {"message": {"$regex": log_filter.search_text, "$options": "i"}},
                {"module": {"$regex": log_filter.search_text, "$options": "i"}},
                {"function": {"$regex": log_filter.search_text, "$options": "i"}}
            ]
        
        return query
    
    async def clear_old_logs(self, days: int = 30):
        """Clear logs older than specified days"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                collection = db.logs  # Get the logs collection
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                result = await collection.delete_many({
                    "timestamp": {"$lt": cutoff_date}
                })
                logger.info(f"Cleared {result.deleted_count} old logs")
        except Exception as e:
            logger.error(f"Failed to clear old logs: {e}")
    
    async def export_logs(self, log_filter: LogFilter, format: str = "json") -> str:
        """Export logs to specified format"""
        logs = await self.get_logs(log_filter, skip=0, limit=10000)
        
        if format == "json":
            import json
            return json.dumps([log.dict() for log in logs], indent=2, default=str)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["timestamp", "level", "category", "message", "module", "function"])
            for log in logs:
                writer.writerow([log.timestamp, log.level, log.category, log.message, log.module, log.function])
            return output.getvalue()
        
        return str([log.dict() for log in logs])
    
    def is_running(self) -> bool:
        """Check if service is running"""
        return self._running
