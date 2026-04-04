from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid

class EntityType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    EMAIL = "email"

class ReputationSource(str, Enum):
    VIRUSTOTAL = "virustotal"
    ABUSEIPDB = "abuseipdb"
    OTX = "otx"
    SHODAN = "shodan"
    INTERNAL = "internal"
    CUSTOM = "custom"

class RiskLevel(str, Enum):
    BENIGN = "benign"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    UNKNOWN = "unknown"

class ClassificationCategory(str, Enum):
    MALWARE = "malware"
    PHISHING = "phishing"
    BOTNET = "botnet"
    SCANNER = "scanner"
    SPAM = "spam"
    COMPROMISED = "compromised"
    LEGITIMATE = "legitimate"
    UNKNOWN = "unknown"

class ActivityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ReputationScore(BaseModel):
    source: ReputationSource
    score: float = Field(..., ge=0, le=100)
    details: Optional[Dict[str, Any]] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    confidence: int = Field(default=50, ge=0, le=100)

class Classification(BaseModel):
    category: ClassificationCategory = ClassificationCategory.UNKNOWN
    confidence: int = Field(default=0, ge=0, le=100)
    last_updated: Optional[datetime] = None

class GeoInfo(BaseModel):
    country: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    asn: Optional[str] = None
    organization: Optional[str] = None
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False

class ThreatIntel(BaseModel):
    campaigns: List[str] = []
    actors: List[str] = []
    families: List[str] = []
    techniques: List[str] = []
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    activity_level: ActivityLevel = ActivityLevel.LOW

class HistoryEntry(BaseModel):
    action: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str

class Metrics(BaseModel):
    alert_count: int = 0
    false_positive_count: int = 0
    true_positive_count: int = 0
    suppression_count: int = 0
    last_alert: Optional[datetime] = None
    average_severity: float = 0.0

class ListInfo(BaseModel):
    whitelisted: bool = False
    blacklisted: bool = False
    whitelist_reason: Optional[str] = None
    blacklist_reason: Optional[str] = None
    list_source: Optional[str] = None
    list_expiry: Optional[datetime] = None

class ReputationCreate(BaseModel):
    entity: str = Field(..., min_length=1)
    entity_type: EntityType
    scores: List[ReputationScore] = []
    geo_info: Optional[GeoInfo] = None
    threat_intel: Optional[ThreatIntel] = None

class ReputationUpdate(BaseModel):
    scores: Optional[List[ReputationScore]] = None
    classification: Optional[Classification] = None
    geo_info: Optional[GeoInfo] = None
    threat_intel: Optional[ThreatIntel] = None
    lists: Optional[ListInfo] = None

class ReputationResponse(BaseModel):
    entity: str
    entity_type: EntityType
    scores: List[ReputationScore]
    aggregated_score: float
    risk_level: RiskLevel
    classification: Classification
    geo_info: Optional[GeoInfo] = None
    threat_intel: Optional[ThreatIntel] = None
    history: List[HistoryEntry] = []
    metrics: Metrics
    lists: ListInfo
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ReputationDocument(BaseModel):
    """MongoDB document model for Reputation"""
    entity: str
    entity_type: EntityType
    scores: List[ReputationScore] = []
    aggregated_score: float = 50.0
    risk_level: RiskLevel = RiskLevel.UNKNOWN
    classification: Classification = Field(default_factory=Classification)
    geo_info: Optional[GeoInfo] = None
    threat_intel: Optional[ThreatIntel] = None
    history: List[HistoryEntry] = []
    metrics: Metrics = Field(default_factory=Metrics)
    lists: ListInfo = Field(default_factory=ListInfo)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=90))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_response(self) -> ReputationResponse:
        """Convert to response model"""
        return ReputationResponse(
            entity=self.entity,
            entity_type=self.entity_type,
            scores=self.scores,
            aggregated_score=self.aggregated_score,
            risk_level=self.risk_level,
            classification=self.classification,
            geo_info=self.geo_info,
            threat_intel=self.threat_intel,
            history=self.history,
            metrics=self.metrics,
            lists=self.lists,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    def update_aggregated_score(self) -> float:
        """Calculate and update aggregated reputation score"""
        if not self.scores:
            self.aggregated_score = 50.0
            self.risk_level = RiskLevel.UNKNOWN
            return self.aggregated_score
        
        # Weighted average based on source reliability and recency
        source_weights = {
            ReputationSource.VIRUSTOTAL: 0.3,
            ReputationSource.ABUSEIPDB: 0.25,
            ReputationSource.OTX: 0.2,
            ReputationSource.SHODAN: 0.15,
            ReputationSource.INTERNAL: 0.1,
            ReputationSource.CUSTOM: 0.1
        }
        
        weighted_sum = 0.0
        total_weight = 0.0
        
        for score in self.scores:
            weight = source_weights.get(score.source, 0.1)
            # Recency factor - decay over 7 days
            recency_factor = max(0.1, 1.0 - (datetime.utcnow() - score.last_updated).total_seconds() / (7 * 24 * 3600))
            adjusted_weight = weight * recency_factor * (score.confidence / 100)
            
            weighted_sum += score.score * adjusted_weight
            total_weight += adjusted_weight
        
        self.aggregated_score = weighted_sum / total_weight if total_weight > 0 else 50.0
        
        # Update risk level based on aggregated score
        if self.aggregated_score >= 80:
            self.risk_level = RiskLevel.MALICIOUS
        elif self.aggregated_score >= 60:
            self.risk_level = RiskLevel.SUSPICIOUS
        elif self.aggregated_score <= 20:
            self.risk_level = RiskLevel.BENIGN
        else:
            self.risk_level = RiskLevel.UNKNOWN
        
        return self.aggregated_score

    def add_score(self, source: ReputationSource, score: float, details: Optional[Dict[str, Any]] = None, confidence: int = 50) -> None:
        """Add or update a reputation score"""
        # Remove existing score from same source
        self.scores = [s for s in self.scores if s.source != source]
        
        # Add new score
        new_score = ReputationScore(
            source=source,
            score=score,
            details=details,
            confidence=confidence
        )
        self.scores.append(new_score)
        
        # Update aggregated score
        self.update_aggregated_score()
        
        # Add to history
        self.history.append(HistoryEntry(
            action="score_added",
            new_value={"source": source.value, "score": score, "confidence": confidence},
            source="system"
        ))
        
        # Update timestamp
        self.updated_at = datetime.utcnow()

    def update_metrics(self, alert_action: str, severity: Optional[str] = None) -> None:
        """Update entity metrics based on alert actions"""
        if alert_action == "alert_generated":
            self.metrics.alert_count += 1
            if severity:
                severity_values = {"low": 1, "medium": 3, "high": 7, "critical": 10}
                severity_value = severity_values.get(severity, 1)
                self.metrics.average_severity = (
                    (self.metrics.average_severity * (self.metrics.alert_count - 1) + severity_value) / 
                    self.metrics.alert_count
                )
            self.metrics.last_alert = datetime.utcnow()
        elif alert_action == "false_positive":
            self.metrics.false_positive_count += 1
        elif alert_action == "true_positive":
            self.metrics.true_positive_count += 1
        elif alert_action == "suppressed":
            self.metrics.suppression_count += 1
        
        self.updated_at = datetime.utcnow()
