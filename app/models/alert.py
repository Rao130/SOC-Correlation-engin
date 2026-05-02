from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    NEW = "new"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"
    SUPPRESSED = "suppressed"

class AlertCategory(str, Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    DDOS = "ddos"
    INTRUSION = "intrusion"
    DATA_BREACH = "data_breach"
    POLICY_VIOLATION = "policy_violation"
    ANOMALY = "anomaly"
    OTHER = "other"
    NETWORK_ANOMALY = "network_anomaly"
    PORT_SCANNING = "port_scanning"
    PORT_SCAN = "port_scan"
    WEB_ATTACK = "web_attack"
    DATA_EXFILTRATION = "data_exfiltration"
    NETWORK_CONFIGURATION = "network_configuration"
    NETWORK_MONITORING = "network_monitoring"
    BRUTE_FORCE = "brute_force"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    LATERAL_MOVEMENT = "lateral_movement"
    C2_COMMUNICATION = "c2_communication"
    RECONNAISSANCE = "reconnaissance"

class EntityType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    EMAIL = "email"
    USER = "user"
    FILE = "file"
    IP_ADDRESS = "ip_address"
    PORT = "port"
    ANOMALY = "anomaly"
    MONITOR = "monitor"

class Entity(BaseModel):
    type: EntityType
    value: str
    reputation: Optional[Dict[str, Any]] = None

class Location(BaseModel):
    country: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[str] = None
    organization: Optional[str] = None

class Context(BaseModel):
    mitre_technique: Optional[str] = None
    mitre_tactic: Optional[str] = None
    kill_chain_phase: Optional[str] = None
    tags: List[str] = []
    campaign: Optional[str] = None
    actor: Optional[str] = None

class FatigueMetrics(BaseModel):
    duplicate_count: int = 0
    suppression_count: int = 0
    auto_resolve_count: int = 0
    analyst_action_count: int = 0
    last_analyst_action: Optional[datetime] = None
    average_resolution_time: Optional[float] = None

class Processing(BaseModel):
    processed: bool = False
    processing_time: Optional[float] = None
    correlation_processed: bool = False
    reputation_checked: bool = False

class Assignment(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    assigned_at: Optional[datetime] = None

class Note(BaseModel):
    user_id: str
    user_name: str
    note: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ExternalReference(BaseModel):
    source: str
    url: str
    description: str

class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    severity: Severity
    source: str = Field(..., min_length=1)
    category: AlertCategory
    confidence: int = Field(default=50, ge=0, le=100)
    entities: List[Entity] = []
    location: Optional[Location] = None
    context: Optional[Context] = None
    raw_data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AlertUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    severity: Optional[Severity] = None
    status: Optional[AlertStatus] = None
    confidence: Optional[int] = Field(None, ge=0, le=100)
    assigned_to: Optional[Assignment] = None
    notes: Optional[List[Note]] = None

class AlertResponse(BaseModel):
    alert_id: str
    title: str
    description: str
    severity: Severity
    source: str
    category: AlertCategory
    status: AlertStatus
    criticality_score: float
    confidence: int
    timestamp: datetime
    first_seen: datetime
    last_seen: datetime
    resolved_at: Optional[datetime] = None
    entities: List[Entity] = []
    location: Optional[Location] = None
    correlated_alerts: List[Dict[str, Any]] = []
    correlation_groups: List[str] = []
    context: Optional[Context] = None
    fatigue_metrics: FatigueMetrics
    processing: Processing
    assigned_to: Optional[Assignment] = None
    notes: List[Note] = []
    external_references: List[ExternalReference] = []
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AlertDocument(BaseModel):
    """MongoDB document model for Alert"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    severity: Severity
    source: str
    category: AlertCategory
    status: AlertStatus = AlertStatus.NEW
    criticality_score: float = 5.0
    confidence: int = 50
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    entities: List[Entity] = []
    location: Optional[Location] = None
    correlated_alerts: List[Dict[str, Any]] = []
    correlation_groups: List[str] = []
    context: Optional[Context] = None
    fatigue_metrics: FatigueMetrics = Field(default_factory=FatigueMetrics)
    processing: Processing = Field(default_factory=Processing)
    assigned_to: Optional[Assignment] = None
    notes: List[Note] = []
    external_references: List[ExternalReference] = []
    raw_data: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self) -> AlertResponse:
        """Convert to response model"""
        return AlertResponse(
            alert_id=self.alert_id,
            title=self.title,
            description=self.description,
            severity=self.severity,
            source=self.source,
            category=self.category,
            status=self.status,
            criticality_score=self.criticality_score,
            confidence=self.confidence,
            timestamp=self.timestamp,
            first_seen=self.first_seen,
            last_seen=self.last_seen,
            resolved_at=self.resolved_at,
            entities=self.entities,
            location=self.location,
            correlated_alerts=self.correlated_alerts,
            correlation_groups=self.correlation_groups,
            context=self.context,
            fatigue_metrics=self.fatigue_metrics,
            processing=self.processing,
            assigned_to=self.assigned_to,
            notes=self.notes,
            external_references=self.external_references,
            raw_data=self.raw_data,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def update_criticality_score(self) -> float:
        """Calculate and update criticality score"""
        score = 5.0  # Base score
        
        # Severity impact
        severity_weights = {
            Severity.LOW: 1,
            Severity.MEDIUM: 3,
            Severity.HIGH: 7,
            Severity.CRITICAL: 10
        }
        score += severity_weights.get(self.severity, 0)
        
        # Reputation impact
        if self.entities:
            min_reputation = 10
            for entity in self.entities:
                if entity.reputation and entity.reputation.get('score', 10) < min_reputation:
                    min_reputation = entity.reputation['score']
            score += (10 - min_reputation) * 0.5
        
        # Correlation impact
        score += len(self.correlated_alerts) * 0.3
        
        # Fatigue metrics impact
        if self.fatigue_metrics.duplicate_count > 5:
            score -= 2
        if self.fatigue_metrics.suppression_count > 3:
            score -= 1
        
        # Cap between 0 and 10
        self.criticality_score = max(0, min(10, score))
        return self.criticality_score
