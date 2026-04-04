from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    SYSTEM = "system"
    AUTH = "auth"
    ALERT = "alert"
    CORRELATION = "correlation"
    REPUTATION = "reputation"
    DATABASE = "database"
    API = "api"
    WEBSOCKET = "websocket"
    SECURITY = "security"
    PERFORMANCE = "performance"


class LogEntry(BaseModel):
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel
    category: LogCategory
    message: str
    module: str
    function: str
    line: Optional[int] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[list] = None


class LogFilter(BaseModel):
    level: Optional[LogLevel] = None
    category: Optional[LogCategory] = None
    module: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    request_id: Optional[str] = None
    error_code: Optional[str] = None
    tags: Optional[list] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    search_text: Optional[str] = None


class LogStats(BaseModel):
    total_logs: int
    logs_by_level: Dict[str, int]
    logs_by_category: Dict[str, int]
    recent_errors: int
    critical_alerts: int
    avg_response_time: Optional[float] = None
    top_error_codes: Dict[str, int]
