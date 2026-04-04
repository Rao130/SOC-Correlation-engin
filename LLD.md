# SOC Correlation Engine - Low Level Design (LLD)

## 1. Database Schema Design

### 1.1 File-based Database Structure

#### 1.1.1 Alerts Database (`data/alerts.json`)
```json
{
  "alerts": [
    {
      "id": "alert_001",
      "timestamp": "2026-04-04T20:30:00Z",
      "severity": "high",
      "source": "SIEM",
      "title": "Suspicious Login Activity",
      "description": "Multiple failed login attempts detected",
      "source_ip": "192.168.1.100",
      "destination_ip": "10.0.0.1",
      "category": "authentication",
      "status": "open",
      "assigned_to": "analyst_001",
      "confidence": 85,
      "affected_assets": ["server_001", "database_001"],
      "mitigation_steps": ["Block IP", "Reset passwords"],
      "correlation_ids": ["corr_001"],
      "created_at": "2026-04-04T20:30:00Z",
      "updated_at": "2026-04-04T20:35:00Z"
    }
  ]
}
```

#### 1.1.2 Correlation Database (`data/correlations.json`)
```json
{
  "correlations": [
    {
      "id": "corr_001",
      "timestamp": "2026-04-04T20:35:00Z",
      "alert_ids": ["alert_001", "alert_002"],
      "correlation_type": "temporal",
      "confidence_score": 92,
      "pattern_description": "Multiple authentication failures from same source",
      "threat_actor": "Unknown",
      "attack_vector": "Credential Stuffing",
      "impact_assessment": "medium",
      "recommended_actions": ["Investigate source IP", "Review access logs"],
      "status": "active",
      "investigator": "analyst_001",
      "created_at": "2026-04-04T20:35:00Z",
      "updated_at": "2026-04-04T20:40:00Z"
    }
  ]
}
```

#### 1.1.3 Reputation Database (`data/reputation.json`)
```json
{
  "entities": [
    {
      "id": "entity_001",
      "type": "ip_address",
      "value": "192.168.1.100",
      "reputation_score": 25,
      "category": "malicious",
      "source": "internal_blacklist",
      "first_seen": "2026-04-01T10:00:00Z",
      "last_seen": "2026-04-04T20:30:00Z",
      "threat_types": ["brute_force", "malware"],
      "geolocation": {
        "country": "Unknown",
        "city": "Unknown",
        "latitude": 0.0,
        "longitude": 0.0
      },
      "related_alerts": ["alert_001", "alert_003"],
      "whitelisted": false,
      "notes": "Repeated suspicious activity detected",
      "updated_at": "2026-04-04T20:30:00Z"
    }
  ]
}
```

#### 1.1.4 Logs Database (`data/logs.json`)
```json
{
  "logs": [
    {
      "id": "log_001",
      "timestamp": "2026-04-04T20:30:00Z",
      "level": "WARNING",
      "source": "alert_service",
      "message": "High severity alert detected: Suspicious Login Activity",
      "module": "alert_processor",
      "user_id": "system",
      "session_id": "sess_001",
      "request_id": "req_001",
      "metadata": {
        "alert_id": "alert_001",
        "processing_time": 0.05,
        "source_ip": "192.168.1.100"
      }
    }
  ]
}
```

## 2. API Endpoint Specifications

### 2.1 Alert Management Endpoints

#### 2.1.1 GET /api/alerts
```python
# Purpose: Retrieve all alerts with filtering
# Parameters:
#   - severity: Filter by severity level (critical, high, medium, low)
#   - status: Filter by status (open, investigating, resolved)
#   - source: Filter by alert source
#   - limit: Maximum number of alerts to return
#   - offset: Pagination offset
# Response: List of alert objects
```

#### 2.1.2 POST /api/alerts
```python
# Purpose: Create new alert
# Request Body:
{
  "severity": "high",
  "source": "SIEM",
  "title": "Alert Title",
  "description": "Alert description",
  "source_ip": "192.168.1.100",
  "category": "authentication"
}
# Response: Created alert object with ID
```

#### 2.1.3 PUT /api/alerts/{alert_id}
```python
# Purpose: Update existing alert
# Request Body:
{
  "status": "investigating",
  "assigned_to": "analyst_001",
  "notes": "Investigation started"
}
# Response: Updated alert object
```

### 2.2 Correlation Endpoints

#### 2.2.1 GET /api/correlations
```python
# Purpose: Retrieve correlation results
# Parameters:
#   - correlation_type: Filter by correlation type
#   - confidence_min: Minimum confidence score
#   - status: Filter by correlation status
# Response: List of correlation objects
```

#### 2.2.2 POST /api/correlations/analyze
```python
# Purpose: Trigger correlation analysis
# Request Body:
{
  "alert_ids": ["alert_001", "alert_002"],
  "analysis_type": "temporal"
}
# Response: Correlation analysis results
```

### 2.3 Reputation Endpoints

#### 2.3.1 GET /api/reputation/entities
```python
# Purpose: Retrieve reputation entities
# Parameters:
#   - entity_type: Filter by entity type (ip_address, domain, email)
#   - category: Filter by reputation category
#   - min_score: Minimum reputation score
# Response: List of reputation entities
```

#### 2.3.2 POST /api/reputation/check
```python
# Purpose: Check entity reputation
# Request Body:
{
  "entity_type": "ip_address",
  "value": "192.168.1.100"
}
# Response: Reputation information for the entity
```

## 3. WebSocket Message Protocol

### 3.1 Message Structure
```json
{
  "type": "alert_created|alert_updated|correlation_found|system_status",
  "timestamp": "2026-04-04T20:30:00Z",
  "data": {
    // Message-specific data
  },
  "metadata": {
    "source": "alert_service",
    "version": "1.0"
  }
}
```

### 3.2 Message Types

#### 3.2.1 alert_created
```json
{
  "type": "alert_created",
  "timestamp": "2026-04-04T20:30:00Z",
  "data": {
    "alert_id": "alert_001",
    "severity": "high",
    "title": "Suspicious Login Activity",
    "source": "SIEM"
  }
}
```

#### 3.2.2 correlation_found
```json
{
  "type": "relation_found",
  "timestamp": "2026-04-04T20:35:00Z",
  "data": {
    "correlation_id": "corr_001",
    "alert_ids": ["alert_001", "alert_002"],
    "confidence_score": 92
  }
}
```

## 4. Data Models

### 4.1 Alert Model (`app/models/alert.py`)
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Alert(BaseModel):
    id: str
    timestamp: datetime
    severity: str = Field(..., regex="^(critical|high|medium|low)$")
    source: str
    title: str
    description: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    category: str
    status: str = Field(default="open", regex="^(open|investigating|resolved)$")
    assigned_to: Optional[str] = None
    confidence: int = Field(..., ge=0, le=100)
    affected_assets: List[str] = []
    mitigation_steps: List[str] = []
    correlation_ids: List[str] = []
    created_at: datetime
    updated_at: datetime

class AlertCreate(BaseModel):
    severity: str
    source: str
    title: str
    description: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    category: str

class AlertUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None
```

### 4.2 Correlation Model (`app/models/correlation.py`)
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List

class Correlation(BaseModel):
    id: str
    timestamp: datetime
    alert_ids: List[str]
    correlation_type: str
    confidence_score: int = Field(..., ge=0, le=100)
    pattern_description: str
    threat_actor: Optional[str] = None
    attack_vector: Optional[str] = None
    impact_assessment: str = Field(..., regex="^(low|medium|high|critical)$")
    recommended_actions: List[str] = []
    status: str = Field(default="active", regex="^(active|resolved|false_positive)$")
    investigator: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CorrelationAnalysis(BaseModel):
    alert_ids: List[str]
    analysis_type: str
    parameters: dict = {}
```

### 4.3 Reputation Model (`app/models/reputation.py`)
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class Geolocation(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: float = 0.0
    longitude: float = 0.0

class Reputation(BaseModel):
    id: str
    type: str = Field(..., regex="^(ip_address|domain|email|url|file_hash)$")
    value: str
    reputation_score: int = Field(..., ge=0, le=100)
    category: str = Field(..., regex="^(malicious|suspicious|benign|unknown)$")
    source: str
    first_seen: datetime
    last_seen: datetime
    threat_types: List[str] = []
    geolocation: Geolocation
    related_alerts: List[str] = []
    whitelisted: bool = False
    notes: Optional[str] = None
    updated_at: datetime

class ReputationCheck(BaseModel):
    entity_type: str
    value: str
```

## 5. Service Layer Implementation

### 5.1 Alert Service (`app/services/alert_service.py`)
```python
import asyncio
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.models.alert import Alert, AlertCreate, AlertUpdate

class AlertService:
    def __init__(self):
        self.db = get_db()
    
    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Create new alert and broadcast via WebSocket"""
        alert = Alert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **alert_data.dict()
        )
        
        # Save to database
        self.db.save_alert(alert)
        
        # Broadcast via WebSocket
        await self.broadcast_alert_created(alert)
        
        return alert
    
    async def get_alerts(self, severity: Optional[str] = None, 
                        status: Optional[str] = None,
                        limit: int = 100, offset: int = 0) -> List[Alert]:
        """Retrieve alerts with filtering"""
        return self.db.get_alerts(severity, status, limit, offset)
    
    async def update_alert(self, alert_id: str, update_data: AlertUpdate) -> Alert:
        """Update existing alert"""
        alert = self.db.get_alert(alert_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(alert, field, value)
        
        alert.updated_at = datetime.now()
        self.db.update_alert(alert)
        
        # Broadcast update
        await self.broadcast_alert_updated(alert)
        
        return alert
    
    async def broadcast_alert_created(self, alert: Alert):
        """Broadcast alert creation via WebSocket"""
        from app.services.websocket_service import websocket_manager
        message = {
            "type": "alert_created",
            "timestamp": datetime.now().isoformat(),
            "data": {
                "alert_id": alert.id,
                "severity": alert.severity,
                "title": alert.title,
                "source": alert.source
            }
        }
        await websocket_manager.broadcast(message)
```

### 5.2 Correlation Service (`app/services/correlation_service.py`)
```python
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.correlation import Correlation, CorrelationAnalysis

class CorrelationService:
    def __init__(self):
        self.db = get_db()
        self.correlation_rules = self.load_correlation_rules()
    
    def load_correlation_rules(self) -> Dict[str, Any]:
        """Load correlation analysis rules"""
        return {
            "temporal": {
                "time_window": 300,  # 5 minutes
                "min_alerts": 2,
                "same_source": True
            },
            "spatial": {
                "same_network": True,
                "min_alerts": 3
            },
            "pattern": {
                "sequence_match": True,
                "time_tolerance": 600  # 10 minutes
            }
        }
    
    async def analyze_correlations(self, analysis: CorrelationAnalysis) -> List[Correlation]:
        """Perform correlation analysis on alerts"""
        alerts = self.db.get_alerts_by_ids(analysis.alert_ids)
        correlations = []
        
        if analysis.analysis_type == "temporal":
            correlations = await self.temporal_correlation(alerts)
        elif analysis.analysis_type == "spatial":
            correlations = await self.spatial_correlation(alerts)
        elif analysis.analysis_type == "pattern":
            correlations = await self.pattern_correlation(alerts)
        
        # Save correlations
        for correlation in correlations:
            self.db.save_correlation(correlation)
            await self.broadcast_correlation_found(correlation)
        
        return correlations
    
    async def temporal_correlation(self, alerts: List[Alert]) -> List[Correlation]:
        """Temporal correlation analysis"""
        correlations = []
        time_window = self.correlation_rules["temporal"]["time_window"]
        
        # Group alerts by time window
        time_groups = self.group_alerts_by_time(alerts, time_window)
        
        for group in time_groups:
            if len(group) >= self.correlation_rules["temporal"]["min_alerts"]:
                correlation = Correlation(
                    id=f"corr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now(),
                    alert_ids=[alert.id for alert in group],
                    correlation_type="temporal",
                    confidence_score=self.calculate_confidence(group),
                    pattern_description="Temporal correlation detected",
                    impact_assessment="medium",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                correlations.append(correlation)
        
        return correlations
    
    def calculate_confidence(self, alerts: List[Alert]) -> int:
        """Calculate correlation confidence score"""
        base_score = 50
        
        # Factor in severity
        severity_bonus = sum(
            {"critical": 20, "high": 15, "medium": 10, "low": 5}[alert.severity]
            for alert in alerts
        )
        
        # Factor in same source
        source_ips = [alert.source_ip for alert in alerts if alert.source_ip]
        if len(set(source_ips)) < len(source_ips):
            source_bonus = 15
        else:
            source_bonus = 0
        
        confidence = min(100, base_score + severity_bonus + source_bonus)
        return confidence
```

## 6. Frontend Component Architecture

### 6.1 Dashboard Component Structure
```javascript
// Main dashboard controller
class DashboardController {
    constructor() {
        this.activeSection = 'dashboard';
        this.websocket = null;
        this.data = {
            alerts: [],
            correlations: [],
            reputation: [],
            analytics: {}
        };
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }
    
    setupWebSocket() {
        this.websocket = new WebSocket('ws://localhost:8000/ws');
        this.websocket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleWebSocketMessage(message);
        };
    }
    
    handleWebSocketMessage(message) {
        switch(message.type) {
            case 'alert_created':
                this.updateAlerts(message.data);
                this.showNotification('New alert created', 'warning');
                break;
            case 'correlation_found':
                this.updateCorrelations(message.data);
                this.showNotification('New correlation found', 'info');
                break;
        }
    }
}
```

### 6.2 Map Component Implementation
```javascript
class ThreatMap {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.threats = [];
        this.markers = [];
        this.init();
    }
    
    init() {
        this.loadThreatData();
        this.renderMap();
        this.setupControls();
    }
    
    loadThreatData() {
        // Load threat data from API or use mock data
        this.threats = [
            {
                id: 1,
                name: "DDoS Attack",
                severity: "critical",
                country: "USA",
                coordinates: [37.7749, -122.4194],
                x: 20,
                y: 35
            }
            // ... more threats
        ];
    }
    
    renderMap() {
        this.container.innerHTML = `
            <div class="simple-map-container">
                <div class="map-canvas">
                    <div class="world-bg"></div>
                    <div class="markers-layer">
                        ${this.renderMarkers()}
                    </div>
                </div>
                <div class="map-header">
                    <h3>🌍 Global Threat Map</h3>
                    <div class="map-stats">
                        <span>🚨 ${this.threats.length} Threats</span>
                        <span>🌍 ${this.getCountryCount()} Countries</span>
                    </div>
                </div>
                <div class="map-controls">
                    <button onclick="zoomIn()">🔍</button>
                    <button onclick="zoomOut()">🔍</button>
                    <button onclick="resetMap()">🏠</button>
                </div>
            </div>
        `;
    }
    
    renderMarkers() {
        return this.threats.map(threat => `
            <div class="threat-marker ${threat.severity}" 
                 style="left: ${threat.x}%; top: ${threat.y}%"
                 onclick="showThreat(${threat.id})"
                 title="${threat.name}">
                <div class="marker-dot"></div>
            </div>
        `).join('');
    }
}
```

## 7. Configuration Management

### 7.1 Application Configuration (`app/core/config.py`)
```python
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "SOC Correlation Engine"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database Settings
    database_url: str = "file://./data"
    data_directory: str = "./data"
    
    # WebSocket Settings
    websocket_enabled: bool = True
    websocket_path: str = "/ws"
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"
    log_rotation: bool = True
    
    # Security Settings
    secret_key: str = "your-secret-key-here"
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # Correlation Settings
    correlation_enabled: bool = True
    correlation_interval: int = 60  # seconds
    
    # External Integrations
    siem_integration: bool = False
    threat_intelligence_feeds: list = []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 8. Error Handling and Logging

### 8.1 Error Handling Strategy
```python
from fastapi import HTTPException
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class SOCException(Exception):
    """Base exception for SOC application"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class AlertNotFoundError(SOCException):
    """Raised when alert is not found"""
    pass

class CorrelationError(SOCException):
    """Raised when correlation analysis fails"""
    pass

class DatabaseError(SOCException):
    """Raised when database operation fails"""
    pass

def handle_exceptions(func):
    """Decorator for handling exceptions"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SOCException as e:
            logger.error(f"SOC Exception: {e.message}")
            raise HTTPException(status_code=400, detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper
```

### 8.2 Logging Configuration
```python
import logging
import logging.handlers
from pathlib import Path

def setup_logging():
    """Setup application logging"""
    # Create logs directory
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.handlers.RotatingFileHandler(
                "./logs/app.log",
                maxBytes=10485760,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("websockets").setLevel(logging.INFO)
```

## 9. Testing Strategy

### 9.1 Unit Tests
```python
import pytest
from app.services.alert_service import AlertService
from app.models.alert import AlertCreate

class TestAlertService:
    def setup_method(self):
        self.alert_service = AlertService()
    
    @pytest.mark.asyncio
    async def test_create_alert(self):
        """Test alert creation"""
        alert_data = AlertCreate(
            severity="high",
            source="SIEM",
            title="Test Alert",
            description="Test description",
            category="test"
        )
        
        alert = await self.alert_service.create_alert(alert_data)
        
        assert alert.severity == "high"
        assert alert.source == "SIEM"
        assert alert.title == "Test Alert"
        assert alert.status == "open"
    
    @pytest.mark.asyncio
    async def test_get_alerts(self):
        """Test alert retrieval"""
        alerts = await self.alert_service.get_alerts()
        assert isinstance(alerts, list)
    
    @pytest.mark.asyncio
    async def test_update_alert(self):
        """Test alert update"""
        # Create alert first
        alert_data = AlertCreate(
            severity="high",
            source="SIEM",
            title="Test Alert",
            description="Test description",
            category="test"
        )
        alert = await self.alert_service.create_alert(alert_data)
        
        # Update alert
        updated_alert = await self.alert_service.update_alert(
            alert.id, 
            AlertUpdate(status="investigating")
        )
        
        assert updated_alert.status == "investigating"
```

### 9.2 Integration Tests
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAPIIntegration:
    def test_alerts_endpoint(self):
        """Test alerts API endpoint"""
        response = client.get("/api/alerts")
        assert response.status_code == 200
        assert "alerts" in response.json()
    
    def test_create_alert_endpoint(self):
        """Test alert creation endpoint"""
        alert_data = {
            "severity": "high",
            "source": "SIEM",
            "title": "Test Alert",
            "description": "Test description",
            "category": "test"
        }
        
        response = client.post("/api/alerts", json=alert_data)
        assert response.status_code == 201
        assert "id" in response.json()
    
    def test_correlation_endpoint(self):
        """Test correlation analysis endpoint"""
        correlation_data = {
            "alert_ids": ["alert_001", "alert_002"],
            "analysis_type": "temporal"
        }
        
        response = client.post("/api/correlations/analyze", json=correlation_data)
        assert response.status_code == 200
```

## 10. Performance Optimization

### 10.1 Database Optimization
```python
class DatabaseOptimizer:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def get_alerts_cached(self, filters: dict) -> list:
        """Get alerts with caching"""
        cache_key = f"alerts_{hash(str(filters))}"
        
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        # Fetch from database
        alerts = await self.db.get_alerts(**filters)
        
        # Cache the result
        self.cache[cache_key] = (alerts, time.time())
        
        return alerts
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
```

### 10.2 Frontend Optimization
```javascript
class PerformanceOptimizer {
    constructor() {
        this.updateQueue = [];
        this.isUpdating = false;
        this.batchSize = 50;
    }
    
    queueUpdate(updateFunction) {
        this.updateQueue.push(updateFunction);
        
        if (!this.isUpdating) {
            this.processQueue();
        }
    }
    
    async processQueue() {
        this.isUpdating = true;
        
        while (this.updateQueue.length > 0) {
            const batch = this.updateQueue.splice(0, this.batchSize);
            
            // Process batch
            await Promise.all(batch.map(fn => fn()));
            
            // Allow UI to breathe
            await new Promise(resolve => setTimeout(resolve, 0));
        }
        
        this.isUpdating = false;
    }
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}
```

This Low Level Design provides detailed implementation specifications for the SOC Correlation Engine, covering database schemas, API endpoints, data models, service implementations, and optimization strategies.
