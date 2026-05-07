"""
Advanced Security Features for SOC Correlation Engine
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import jwt
from cryptography.fernet import Fernet
import ipaddress
import re

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    rules: List[Dict]
    actions: List[str]
    severity_threshold: ThreatLevel
    auto_response: bool

class AdvancedSecurityEngine:
    """Advanced security analysis and response engine"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.active_policies = {}
        self.threat_intelligence_cache = {}
        self.behavioral_baselines = {}
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    async def initialize_security_policies(self):
        """Initialize advanced security policies"""
        policies = [
            SecurityPolicy(
                name="Zero_Trust_Access",
                rules=[
                    {"type": "authentication", "require_mfa": True},
                    {"type": "authorization", "principle": "least_privilege"},
                    {"type": "encryption", "data_at_rest": True, "data_in_transit": True}
                ],
                actions=["block", "alert", "log"],
                severity_threshold=ThreatLevel.HIGH,
                auto_response=True
            ),
            SecurityPolicy(
                name="Advanced_Threat_Detection",
                rules=[
                    {"type": "ml_anomaly", "confidence_threshold": 0.85},
                    {"type": "behavioral_analysis", "deviation_threshold": 2.5},
                    {"type": "threat_intelligence", "ioc_matching": True}
                ],
                actions=["quarantine", "investigate", "notify"],
                severity_threshold=ThreatLevel.CRITICAL,
                auto_response=True
            ),
            SecurityPolicy(
                name="Data_Leakage_Prevention",
                rules=[
                    {"type": "data_classification", "sensitive_data": True},
                    {"type": "egress_monitoring", "unauthorized_transfer": True},
                    {"type": "encryption", "dormant_data": True}
                ],
                actions=["encrypt", "block", "audit"],
                severity_threshold=ThreatLevel.HIGH,
                auto_response=True
            )
        ]
        
        for policy in policies:
            self.active_policies[policy.name] = policy
            logger.info(f"Loaded security policy: {policy.name}")
    
    async def analyze_advanced_threats(self, alerts: List[Dict]) -> List[Dict]:
        """Advanced threat analysis using multiple techniques"""
        advanced_threats = []
        
        # 1. Machine Learning Anomaly Detection
        ml_anomalies = await self._detect_ml_anomalies(alerts)
        advanced_threats.extend(ml_anomalies)
        
        # 2. Behavioral Analysis
        behavioral_threats = await self._analyze_behavioral_patterns(alerts)
        advanced_threats.extend(behavioral_threats)
        
        # 3. Threat Intelligence Correlation
        ti_threats = await self._correlate_with_threat_intelligence(alerts)
        advanced_threats.extend(ti_threats)
        
        # 4. Geographic Analysis
        geo_threats = await self._analyze_geographic_patterns(alerts)
        advanced_threats.extend(geo_threats)
        
        # 5. Temporal Pattern Analysis
        temporal_threats = await self._analyze_temporal_patterns(alerts)
        advanced_threats.extend(temporal_threats)
        
        return advanced_threats
    
    async def _detect_ml_anomalies(self, alerts: List[Dict]) -> List[Dict]:
        """Machine learning based anomaly detection"""
        anomalies = []
        
        # Feature extraction for ML
        features = []
        for alert in alerts:
            feature_vector = {
                'hour': datetime.fromisoformat(alert.get('timestamp', '')).hour,
                'severity_score': self._get_severity_numeric(alert.get('severity', 'medium')),
                'source_type': self._encode_source_type(alert.get('source', '')),
                'category': self._encode_category(alert.get('category', '')),
                'entity_count': len(alert.get('entities', [])),
                'risk_score': alert.get('risk_score', 0)
            }
            features.append(feature_vector)
        
        # Simple anomaly detection (in production, use actual ML models)
        if len(features) > 10:
            avg_risk = sum(f['risk_score'] for f in features) / len(features)
            std_risk = (sum((f['risk_score'] - avg_risk) ** 2 for f in features) / len(features)) ** 0.5
            
            for i, (alert, feature) in enumerate(zip(alerts, features)):
                if abs(feature['risk_score'] - avg_risk) > 2 * std_risk:
                    anomalies.append({
                        'type': 'ml_anomaly',
                        'alert_id': alert.get('_id'),
                        'description': f"ML anomaly detected: risk score {feature['risk_score']} deviates from norm",
                        'confidence': min(0.95, abs(feature['risk_score'] - avg_risk) / std_risk / 3),
                        'severity': 'high' if abs(feature['risk_score'] - avg_risk) > 3 * std_risk else 'medium',
                        'timestamp': datetime.utcnow().isoformat(),
                        'features': feature
                    })
        
        return anomalies
    
    async def _analyze_behavioral_patterns(self, alerts: List[Dict]) -> List[Dict]:
        """Behavioral pattern analysis"""
        behavioral_threats = []
        
        # Group by user/entity
        entity_behaviors = {}
        for alert in alerts:
            entities = alert.get('entities', [])
            for entity in entities:
                entity_id = f"{entity.get('type')}:{entity.get('value')}"
                if entity_id not in entity_behaviors:
                    entity_behaviors[entity_id] = []
                entity_behaviors[entity_id].append(alert)
        
        # Analyze each entity's behavior
        for entity_id, entity_alerts in entity_behaviors.items():
            if len(entity_alerts) < 3:  # Need sufficient data
                continue
            
            # Calculate behavioral metrics
            severity_trend = [self._get_severity_numeric(a.get('severity', 'medium')) for a in entity_alerts]
            time_pattern = [datetime.fromisoformat(a.get('timestamp', '')).hour for a in entity_alerts]
            category_diversity = len(set(a.get('category', '') for a in entity_alerts))
            
            # Detect anomalies
            avg_severity = sum(severity_trend) / len(severity_trend)
            recent_severity = severity_trend[-3:]  # Last 3 alerts
            
            if len(recent_severity) > 0:
                recent_avg = sum(recent_severity) / len(recent_severity)
                if recent_avg > avg_severity * 1.5:
                    behavioral_threats.append({
                        'type': 'behavioral_anomaly',
                        'entity_id': entity_id,
                        'description': f"Behavioral anomaly: escalating severity for {entity_id}",
                        'confidence': min(0.9, (recent_avg - avg_severity) / avg_severity),
                        'severity': 'high',
                        'timestamp': datetime.utcnow().isoformat(),
                        'metrics': {
                            'avg_severity': avg_severity,
                            'recent_avg_severity': recent_avg,
                            'category_diversity': category_diversity,
                            'alert_count': len(entity_alerts)
                        }
                    })
        
        return behavioral_threats
    
    async def _correlate_with_threat_intelligence(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts with threat intelligence feeds"""
        ti_threats = []
        
        # Mock threat intelligence data (in production, connect to real TI feeds)
        known_iocs = {
            'malicious_ips': ['192.168.1.100', '10.0.0.50', '172.16.0.25'],
            'malicious_domains': ['evil.com', 'malware.net', 'c2.example.com'],
            'malicious_hashes': ['a1b2c3d4e5f6', 'f6e5d4c3b2a1', 'xyz123abc456'],
            'attack_patterns': ['APT28', 'Carbanak', 'Conti', 'DarkSide']
        }
        
        for alert in alerts:
            raw_data = alert.get('raw_data', {})
            alert_ti_matches = []
            
            # Check IP addresses
            if 'source_ip' in raw_data:
                if raw_data['source_ip'] in known_iocs['malicious_ips']:
                    alert_ti_matches.append(f"Malicious IP: {raw_data['source_ip']}")
            
            # Check domains
            if 'domain' in raw_data:
                if raw_data['domain'] in known_iocs['malicious_domains']:
                    alert_ti_matches.append(f"Malicious domain: {raw_data['domain']}")
            
            # Check attack patterns
            if alert.get('source') in known_iocs['attack_patterns']:
                alert_ti_matches.append(f"Known attack pattern: {alert.get('source')}")
            
            if alert_ti_matches:
                ti_threats.append({
                    'type': 'threat_intelligence_match',
                    'alert_id': alert.get('_id'),
                    'description': f"Threat intelligence match: {', '.join(alert_ti_matches)}",
                    'confidence': 0.9,
                    'severity': 'critical',
                    'timestamp': datetime.utcnow().isoformat(),
                    'ti_matches': alert_ti_matches,
                    'ioc_data': raw_data
                })
        
        return ti_threats
    
    async def _analyze_geographic_patterns(self, alerts: List[Dict]) -> List[Dict]:
        """Geographic pattern analysis"""
        geo_threats = []
        
        # Group by geographic location
        geo_alerts = {}
        for alert in alerts:
            raw_data = alert.get('raw_data', {})
            country = raw_data.get('country', 'Unknown')
            if country not in geo_alerts:
                geo_alerts[country] = []
            geo_alerts[country].append(alert)
        
        # Detect geographic anomalies
        for country, country_alerts in geo_alerts.items():
            if len(country_alerts) > 5:  # Threshold for geographic anomaly
                severity_scores = [self._get_severity_numeric(a.get('severity', 'medium')) for a in country_alerts]
                avg_severity = sum(severity_scores) / len(severity_scores)
                
                if avg_severity > 6:  # High severity threshold
                    geo_threats.append({
                        'type': 'geographic_anomaly',
                        'location': country,
                        'description': f"High volume of severe alerts from {country}",
                        'confidence': min(0.85, len(country_alerts) / 20),
                        'severity': 'high' if avg_severity > 7 else 'medium',
                        'timestamp': datetime.utcnow().isoformat(),
                        'metrics': {
                            'alert_count': len(country_alerts),
                            'avg_severity': avg_severity,
                            'countries_involved': len(geo_alerts)
                        }
                    })
        
        return geo_threats
    
    async def _analyze_temporal_patterns(self, alerts: List[Dict]) -> List[Dict]:
        """Temporal pattern analysis"""
        temporal_threats = []
        
        # Group by time windows
        time_windows = {}
        for alert in alerts:
            timestamp = datetime.fromisoformat(alert.get('timestamp', ''))
            time_key = timestamp.strftime("%Y%m%d_%H%M")  # 1-minute windows
            if time_key not in time_windows:
                time_windows[time_key] = []
            time_windows[time_key].append(alert)
        
        # Detect temporal anomalies
        window_sizes = [len(alerts) for alerts in time_windows.values()]
        if len(window_sizes) > 10:
            avg_size = sum(window_sizes) / len(window_sizes)
            std_size = (sum((size - avg_size) ** 2 for size in window_sizes) / len(window_sizes)) ** 0.5
            
            for time_key, window_alerts in time_windows.items():
                if len(window_alerts) > avg_size + 2 * std_size:
                    temporal_threats.append({
                        'type': 'temporal_anomaly',
                        'time_window': time_key,
                        'description': f"Spike in alerts during time window {time_key}",
                        'confidence': min(0.9, (len(window_alerts) - avg_size) / std_size / 3),
                        'severity': 'high' if len(window_alerts) > avg_size + 3 * std_size else 'medium',
                        'timestamp': datetime.utcnow().isoformat(),
                        'metrics': {
                            'alert_count': len(window_alerts),
                            'avg_window_size': avg_size,
                            'std_window_size': std_size
                        }
                    })
        
        return temporal_threats
    
    def _get_severity_numeric(self, severity: str) -> float:
        """Convert severity to numeric score"""
        severity_map = {
            'low': 2.5,
            'medium': 5.0,
            'high': 7.5,
            'critical': 9.0
        }
        return severity_map.get(severity, 5.0)
    
    def _encode_source_type(self, source: str) -> int:
        """Encode source type for ML features"""
        source_map = {
            'firewall': 1,
            'ids': 2,
            'siem': 3,
            'windows_logs': 4,
            'network_monitor': 5
        }
        return source_map.get(source.lower(), 0)
    
    def _encode_category(self, category: str) -> int:
        """Encode category for ML features"""
        category_map = {
            'malware': 1,
            'phishing': 2,
            'ddos': 3,
            'intrusion': 4,
            'data_breach': 5,
            'brute_force': 6,
            'reconnaissance': 7
        }
        return category_map.get(category.lower(), 0)
    
    async def execute_security_policy(self, policy_name: str, threat_data: Dict) -> Dict:
        """Execute security policy actions"""
        if policy_name not in self.active_policies:
            return {'status': 'error', 'message': 'Policy not found'}
        
        policy = self.active_policies[policy_name]
        actions_taken = []
        
        for action in policy.actions:
            try:
                if action == 'block':
                    result = await self._block_threat(threat_data)
                    actions_taken.append({'action': 'block', 'result': result})
                elif action == 'quarantine':
                    result = await self._quarantine_threat(threat_data)
                    actions_taken.append({'action': 'quarantine', 'result': result})
                elif action == 'encrypt':
                    result = await self._encrypt_sensitive_data(threat_data)
                    actions_taken.append({'action': 'encrypt', 'result': result})
                elif action == 'alert':
                    result = await self._send_security_alert(threat_data, policy_name)
                    actions_taken.append({'action': 'alert', 'result': result})
                elif action == 'log':
                    result = await self._log_security_event(threat_data, policy_name)
                    actions_taken.append({'action': 'log', 'result': result})
            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")
                actions_taken.append({'action': action, 'result': 'failed', 'error': str(e)})
        
        return {
            'status': 'success',
            'policy': policy_name,
            'threat_id': threat_data.get('alert_id'),
            'actions_taken': actions_taken,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _block_threat(self, threat_data: Dict) -> Dict:
        """Block identified threat"""
        # Implement actual blocking logic
        return {'status': 'blocked', 'method': 'firewall_rule', 'duration': '24h'}
    
    async def _quarantine_threat(self, threat_data: Dict) -> Dict:
        """Quarantine affected systems"""
        # Implement quarantine logic
        return {'status': 'quarantined', 'systems': ['workstation-01', 'server-02']}
    
    async def _encrypt_sensitive_data(self, threat_data: Dict) -> Dict:
        """Encrypt sensitive data"""
        # Implement encryption logic
        return {'status': 'encrypted', 'files_count': 15, 'size_mb': 250}
    
    async def _send_security_alert(self, threat_data: Dict, policy_name: str) -> Dict:
        """Send security alert"""
        # Implement alert notification
        return {'status': 'alerted', 'channels': ['email', 'sms', 'slack']}
    
    async def _log_security_event(self, threat_data: Dict, policy_name: str) -> Dict:
        """Log security event"""
        # Implement secure logging
        return {'status': 'logged', 'log_id': f"sec_{datetime.utcnow().timestamp()}"}
