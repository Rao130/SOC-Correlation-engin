from pydantic_settings import BaseSettings
from typing import List, Optional
import os
import json

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "SOC Correlation Engine"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
    
    def _validate_config(self):
        """Validate critical configuration values"""
        # Validate port range
        if not (1 <= self.PORT <= 65535):
            raise ValueError(f"PORT must be between 1 and 65535, got {self.PORT}")
        
        # Validate MongoDB URL format
        if not self.MONGODB_URL.startswith(('mongodb://', 'mongodb+srv://')):
            raise ValueError("MONGODB_URL must start with mongodb:// or mongodb+srv://")
        
        # Validate secret key length
        if len(self.SECRET_KEY) < 32:
            logger.warning("SECRET_KEY should be at least 32 characters for security")
        
        # Validate log level
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL not in valid_log_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_log_levels}, got {self.LOG_LEVEL}")
    
    # Database
    DATABASE_TYPE: str = "mongodb"
    MONGODB_URL: str = "mongodb://127.0.0.1:27017"
    DATABASE_NAME: str = "soc_correlation_engine_new"
    REDIS_URL: str = "redis://localhost:6379"
    
    # MongoDB Connection Options
    MONGODB_HOST: str = "127.0.0.1"
    MONGODB_PORT: int = 27017
    MONGODB_USERNAME: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_AUTH_SOURCE: str = "admin"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - Handle both string and list formats
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://127.0.0.1:59743,http://127.0.0.1:8000,http://127.0.0.1:59071,http://127.0.0.1:55000,http://127.0.0.1:55065,http://127.0.0.1:64392,http://localhost:55000,http://localhost:55065,http://localhost:64392")
        if origins_str.startswith("["):
            try:
                return json.loads(origins_str)
            except:
                pass
        return [origin.strip() for origin in origins_str.split(",")]
    
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
    
# Data Generation (for testing/demo only - disable in production SIEM mode)
    ENABLE_DATA_GENERATION: bool = False  # Set to False for production SIEM mode
    
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
    RATE_LIMIT_WINDOW_MS: int = 900000
    RATE_LIMIT_MAX_REQUESTS: int = 100
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 1000
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".csv", ".json", ".xml"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env

# Create settings instance
settings = Settings()

# Create directories if they don't exist
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
