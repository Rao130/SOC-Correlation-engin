from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "SOC Correlation Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_TYPE: str = "file"
    DATABASE_URL: str = "file://data/"
    REDIS_URL: str = "file://data/"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # External API Keys
    VIRUSTOTAL_API_KEY: Optional[str] = None
    ABUSEIPDB_API_KEY: Optional[str] = None
    OTX_API_KEY: Optional[str] = None
    SHODAN_API_KEY: Optional[str] = None
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/soc_engine.log"
    
    # Alert Processing
    ALERT_BATCH_SIZE: int = 100
    CORRELATION_TIME_WINDOW: int = 3600000  # 1 hour in milliseconds
    CRITICALITY_THRESHOLD: float = 7.5
    
    # Background Tasks
    BACKGROUND_TASK_INTERVAL: int = 60  # seconds
    CLEANUP_INTERVAL: int = 3600  # seconds
    
    # WebSocket
    WS_PING_INTERVAL: int = 25
    WS_PING_TIMEOUT: int = 5
    
    # GeoIP
    GEOIP_DB_PATH: str = "data/GeoLite2-City.mmdb"
    
    # Machine Learning
    ML_MODEL_UPDATE_INTERVAL: int = 86400  # 24 hours
    ANOMALY_THRESHOLD: float = 0.85
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    RATE_LIMIT_BURST: int = 200
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 1000
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".json", ".xml"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create directories if they don't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
