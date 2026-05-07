import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.models.log import LogEntry, LogFilter, LogStats, LogLevel, LogCategory
from app.core.logging import logger
import uuid
import re

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
                logs_data = db.logs.data if hasattr(db.logs, 'data') else db.logs
                
                # Add buffer logs to existing logs
                for log_entry in self.log_buffer:
                    logs_data.append(log_entry)
                
                # Keep only last 1000 logs
                if len(logs_data) > 1000:
                    logs_data[:] = logs_data[-1000:]
                
                # Save to file
                db._save_data()
                
            self.log_buffer.clear()
        except Exception as e:
            logger.error(f"Failed to flush log buffer: {e}")
    
    async def get_logs(self, log_filter: LogFilter = None, skip: int = 0, limit: int = 100) -> List[LogEntry]:
        """Get logs with filtering and pagination"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                logs_data = db.logs.data if hasattr(db.logs, 'data') else db.logs
                
                # Apply filters
                filtered_logs = logs_data
                if log_filter:
                    if log_filter.level:
                        filtered_logs = [log for log in filtered_logs if log.get('level') == log_filter.level]
                    if log_filter.search_text:
                        search_lower = log_filter.search_text.lower()
                        filtered_logs = [log for log in filtered_logs if search_lower in log.get('message', '').lower()]
                
                # Sort by timestamp (newest first)
                filtered_logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Pagination
                paginated_logs = filtered_logs[skip:skip + limit]
                
                return [LogEntry(**log) if 'category' in log and 'function' in log else LogEntry(**{
                    **log,
                    'category': log.get('category', 'system').lower(),
                    'function': log.get('function', 'unknown'),
                    'module': log.get('module', 'unknown'),
                    'message': log.get('message', ''),
                    'level': log.get('level', 'INFO').upper(),
                    'timestamp': log.get('timestamp', datetime.utcnow())
                }) for log in paginated_logs]
            return []
        except Exception as e:
            logger.error(f"Failed to get logs: {e}")
            return []
    
    async def get_log_stats(self, hours: int = 24) -> LogStats:
        """Get log statistics"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                logs_data = db.logs.data if hasattr(db.logs, 'data') else db.logs
                
                # Filter logs by time
                start_time = datetime.utcnow() - timedelta(hours=hours)
                recent_logs = [log for log in logs_data if log.get('timestamp', '') >= start_time.isoformat()]
                
                # Total logs
                total_logs = len(recent_logs)
                
                # Logs by level
                level_counts = {}
                for log in recent_logs:
                    level = log.get('level', 'INFO')
                    level_counts[level] = level_counts.get(level, 0) + 1
                
                # Most common sources
                source_counts = {}
                for log in recent_logs:
                    source = log.get('source', 'unknown')
                    source_counts[source] = source_counts.get(source, 0) + 1
                
                # Get top sources
                top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                return LogStats(
                    total_logs=total_logs,
                    level_counts=level_counts,
                    top_sources=[{"source": src, "count": cnt} for src, cnt in top_sources],
                    error_rate=level_counts.get('ERROR', 0) / max(total_logs, 1) * 100,
                    warning_rate=level_counts.get('WARNING', 0) / max(total_logs, 1) * 100
                )
            return LogStats(total_logs=0, level_counts={}, top_sources=[], error_rate=0, warning_rate=0)
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return LogStats(total_logs=0, level_counts={}, top_sources=[], error_rate=0, warning_rate=0)
    
    async def get_log_timeline(self, hours: int = 24) -> List[Dict]:
        """Get log timeline data"""
        try:
            if self.database_manager:
                db = self.database_manager.get_database()
                logs_data = db.logs.data if hasattr(db.logs, 'data') else db.logs
                
                # Filter logs by time
                start_time = datetime.utcnow() - timedelta(hours=hours)
                recent_logs = [log for log in logs_data if log.get('timestamp', '') >= start_time.isoformat()]
                
                # Group by hour
                timeline_data = {}
                for log in recent_logs:
                    try:
                        timestamp = datetime.fromisoformat(log.get('timestamp', '').replace('Z', '+00:00'))
                        hour_key = timestamp.strftime('%Y-%m-%d %H:00')
                        
                        if hour_key not in timeline_data:
                            timeline_data[hour_key] = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
                        
                        level = log.get('level', 'INFO')
                        timeline_data[hour_key][level] = timeline_data[hour_key].get(level, 0) + 1
                    except:
                        continue
                
                # Convert to list and sort
                timeline = [
                    {
                        'timestamp': hour,
                        'counts': counts,
                        'total': sum(counts.values())
                    }
                    for hour, counts in timeline_data.items()
                ]
                
                return sorted(timeline, key=lambda x: x['timestamp'])
            return []
        except Exception as e:
            logger.error(f"Failed to get log timeline: {e}")
            return []
    
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
