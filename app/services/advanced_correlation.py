"""
Advanced Multi-Dimensional Correlation Engine
Enterprise-grade threat correlation with AI/ML integration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import json
import networkx as nx
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class CorrelationResult:
    """Correlation analysis result"""
    correlation_id: str
    correlation_type: str
    confidence_score: float
    related_alerts: List[str]
    severity: str
    description: str
    attack_stage: Optional[str] = None
    threat_indicators: List[str] = None
    business_impact: str = "medium"

class AdvancedCorrelationEngine:
    """Enterprise-grade correlation engine with multiple analysis dimensions"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.correlation_rules = self._load_correlation_rules()
        self.network_graph = nx.DiGraph()
        self.entity_relationships = defaultdict(list)
        self.temporal_window = timedelta(hours=24)
        self.correlation_cache = {}
        
    def _load_correlation_rules(self) -> Dict[str, Any]:
        """Load advanced correlation rules"""
        return {
            'temporal': {
                'window_minutes': 30,
                'burst_threshold': 5,
                'pattern_types': ['brute_force', 'ddos', 'malware_campaign']
            },
            'network': {
                'same_subnet_threshold': 3,
                'lateral_movement_indicators': ['smb', 'rpc', 'winrm'],
                'data_exfil_protocols': ['ftp', 'sftp', 'http_large']
            },
            'behavioral': {
                'user_anomaly_threshold': 0.8,
                'unusual_time_range': (22, 6),  # 10PM to 6AM
                'privilege_escalation_indicators': ['sudo', 'runas', 'su']
            },
            'threat_intel': {
                'ioc_match_threshold': 0.7,
                'malware_families': ['emotet', 'trickbot', 'ryuk', 'wannacry'],
                'attack_attribution': ['apt28', 'apt29', ' Lazarus Group']
            },
            'asset_criticality': {
                'critical_assets': ['domain_controller', 'database_server', 'file_server'],
                'high_risk_ports': [22, 23, 3389, 5985],
                'sensitive_data_types': ['pii', 'phi', 'financial', 'intellectual_property']
            }
        }
    
    async def correlate_alerts(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """
        Perform multi-dimensional correlation analysis
        """
        try:
            logger.info(f"🔍 Starting advanced correlation on {len(alerts)} alerts")
            
            correlations = []
            
            # 1. Temporal Correlation
            temporal_correlations = await self._temporal_correlation(alerts)
            correlations.extend(temporal_correlations)
            
            # 2. Network Topology Correlation
            network_correlations = await self._network_correlation(alerts)
            correlations.extend(network_correlations)
            
            # 3. Behavioral Correlation
            behavioral_correlations = await self._behavioral_correlation(alerts)
            correlations.extend(behavioral_correlations)
            
            # 4. Threat Intelligence Correlation
            threatintel_correlations = await self._threat_intel_correlation(alerts)
            correlations.extend(threatintel_correlations)
            
            # 5. Asset Criticality Correlation
            asset_correlations = await self._asset_correlation(alerts)
            correlations.extend(asset_correlations)
            
            # 6. Cross-Dimensional Meta-Correlation
            meta_correlations = await self._meta_correlation(correlations)
            correlations.extend(meta_correlations)
            
            # Sort by confidence score
            correlations.sort(key=lambda x: x.confidence_score, reverse=True)
            
            logger.info(f"✅ Generated {len(correlations)} correlations")
            return correlations[:50]  # Return top 50 correlations
            
        except Exception as e:
            logger.error(f"❌ Correlation analysis failed: {e}")
            return []
    
    async def _temporal_correlation(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Time-based correlation analysis"""
        correlations = []
        
        # Group alerts by time windows
        time_groups = defaultdict(list)
        for alert in alerts:
            timestamp = alert.get('timestamp')
            if timestamp:
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_key = timestamp.replace(minute=0, second=0, microsecond=0)
                time_groups[time_key].append(alert)
        
        # Detect temporal patterns
        for time_key, group_alerts in time_groups.items():
            if len(group_alerts) >= self.correlation_rules['temporal']['burst_threshold']:
                # Check for specific attack patterns
                attack_types = Counter([alert.get('category', 'unknown') for alert in group_alerts])
                
                correlation_id = f"temporal_{int(time_key.timestamp())}"
                confidence = min(0.9, len(group_alerts) * 0.15)
                
                # Determine attack pattern
                dominant_attack = attack_types.most_common(1)[0][0] if attack_types else 'unknown'
                
                correlation = CorrelationResult(
                    correlation_id=correlation_id,
                    correlation_type="temporal_burst",
                    confidence_score=confidence,
                    related_alerts=[alert.get('_id', alert.get('alert_id', '')) for alert in group_alerts],
                    severity=self._calculate_severity(group_alerts),
                    description=f"Temporal burst detected: {len(group_alerts)} alerts in {dominant_attack} category",
                    attack_stage=self._map_attack_stage(dominant_attack),
                    threat_indicators=[f"burst_{dominant_attack}", f"time_window_{time_key}"]
                )
                
                correlations.append(correlation)
        
        return correlations
    
    async def _network_correlation(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Network topology and traffic correlation"""
        correlations = []
        
        # Build network graph
        self._build_network_graph(alerts)
        
        # Detect lateral movement patterns
        lateral_movements = self._detect_lateral_movement(alerts)
        correlations.extend(lateral_movements)
        
        # Detect data exfiltration patterns
        exfil_patterns = self._detect_data_exfiltration(alerts)
        correlations.extend(exfil_patterns)
        
        # Detect command and control communications
        c2_patterns = self._detect_c2_communications(alerts)
        correlations.extend(c2_patterns)
        
        return correlations
    
    async def _behavioral_correlation(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """User behavior and anomaly correlation"""
        correlations = []
        
        # Group by user/entity
        entity_groups = defaultdict(list)
        for alert in alerts:
            entity = alert.get('source_ip') or alert.get('user', 'unknown')
            entity_groups[entity].append(alert)
        
        # Analyze each entity's behavior
        for entity, entity_alerts in entity_groups.items():
            if len(entity_alerts) >= 3:  # Minimum alerts for behavioral analysis
                
                # Check for unusual time patterns
                time_anomalies = self._detect_time_anomalies(entity_alerts)
                if time_anomalies:
                    correlation = CorrelationResult(
                        correlation_id=f"behavior_time_{entity}_{len(entity_alerts)}",
                        correlation_type="behavioral_anomaly",
                        confidence_score=0.8,
                        related_alerts=[alert.get('_id', '') for alert in entity_alerts],
                        severity="high",
                        description=f"Unusual time-based activity detected for {entity}",
                        attack_stage="reconnaissance" if len(entity_alerts) < 5 else "persistence",
                        threat_indicators=["unusual_hours", "behavioral_deviation"]
                    )
                    correlations.append(correlation)
                
                # Check for privilege escalation
                privilege_escalation = self._detect_privilege_escalation(entity_alerts)
                if privilege_escalation:
                    correlation = CorrelationResult(
                        correlation_id=f"privilege_esc_{entity}",
                        correlation_type="privilege_escalation",
                        confidence_score=0.9,
                        related_alerts=[alert.get('_id', '') for alert in entity_alerts],
                        severity="critical",
                        description=f"Privilege escalation pattern detected for {entity}",
                        attack_stage="privilege_escalation",
                        threat_indicators=["privilege_escalation", "admin_access"]
                    )
                    correlations.append(correlation)
        
        return correlations
    
    async def _threat_intel_correlation(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Threat intelligence and IOC correlation"""
        correlations = []
        
        # Extract IOCs from alerts
        ioc_matches = await self._extract_and_match_iocs(alerts)
        
        # Group by threat actor/malware family
        threat_groups = defaultdict(list)
        for alert_id, ioc_data in ioc_matches.items():
            for ioc, threat_info in ioc_data.items():
                if threat_info:
                    threat_key = f"{threat_info.get('actor', 'unknown')}_{threat_info.get('malware', 'unknown')}"
                    threat_groups[threat_key].append(alert_id)
        
        # Create threat intelligence correlations
        for threat_key, related_alerts in threat_groups.items():
            if len(related_alerts) >= 2:
                actor, malware = threat_key.split('_', 1)
                
                correlation = CorrelationResult(
                    correlation_id=f"threatintel_{actor}_{malware}",
                    correlation_type="threat_intelligence_match",
                    confidence_score=0.85,
                    related_alerts=related_alerts,
                    severity="critical" if actor in ['apt28', 'apt29'] else "high",
                    description=f"Threat intelligence match: {actor} using {malware}",
                    attack_stage="initial_access",
                    threat_indicators=[f"actor_{actor}", f"malware_{malware}"]
                )
                correlations.append(correlation)
        
        return correlations
    
    async def _asset_correlation(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Asset criticality and vulnerability correlation"""
        correlations = []
        
        # Group by target asset
        asset_groups = defaultdict(list)
        for alert in alerts:
            target = alert.get('destination_ip') or alert.get('target_asset', 'unknown')
            asset_groups[target].append(alert)
        
        # Analyze critical asset targeting
        for asset, asset_alerts in asset_groups.items():
            if len(asset_alerts) >= 2:
                # Check if asset is critical
                is_critical = self._is_critical_asset(asset)
                
                if is_critical:
                    correlation = CorrelationResult(
                        correlation_id=f"critical_asset_{asset}",
                        correlation_type="critical_asset_targeting",
                        confidence_score=0.9,
                        related_alerts=[alert.get('_id', '') for alert in asset_alerts],
                        severity="critical",
                        description=f"Critical asset {asset} under attack",
                        attack_stage="initial_access",
                        business_impact="high",
                        threat_indicators=["critical_asset", "high_value_target"]
                    )
                    correlations.append(correlation)
        
        return correlations
    
    async def _meta_correlation(self, correlations: List[CorrelationResult]) -> List[CorrelationResult]:
        """Cross-dimensional meta-correlation analysis"""
        meta_correlations = []
        
        # Find overlapping alert sets across different correlation types
        correlation_groups = defaultdict(list)
        for corr in correlations:
            alert_set_key = tuple(sorted(corr.related_alerts))
            correlation_groups[alert_set_key].append(corr)
        
        # Create meta-correlations for overlapping patterns
        for alert_set, related_correlations in correlation_groups.items():
            if len(related_correlations) >= 3:  # Multiple correlation types for same alerts
                
                # Calculate combined confidence
                combined_confidence = sum(c.confidence_score for c in related_correlations) / len(related_correlations)
                
                # Determine dominant correlation types
                correlation_types = [c.correlation_type for c in related_correlations]
                
                meta_correlation = CorrelationResult(
                    correlation_id=f"meta_{hash(alert_set)}",
                    correlation_type="multi_dimensional",
                    confidence_score=min(0.95, combined_confidence * 1.2),
                    related_alerts=list(alert_set),
                    severity="critical",
                    description=f"Multi-dimensional threat: {', '.join(correlation_types)}",
                    attack_stage="advanced_persistent_threat",
                    business_impact="high",
                    threat_indicators=correlation_types
                )
                meta_correlations.append(meta_correlation)
        
        return meta_correlations
    
    def _build_network_graph(self, alerts: List[Dict[str, Any]]):
        """Build network topology graph from alerts"""
        self.network_graph.clear()
        
        for alert in alerts:
            source = alert.get('source_ip', 'unknown')
            target = alert.get('destination_ip', 'unknown')
            
            if source != 'unknown' and target != 'unknown':
                self.network_graph.add_edge(source, target, 
                    alert_type=alert.get('category'),
                    timestamp=alert.get('timestamp'),
                    severity=alert.get('severity'))
    
    def _detect_lateral_movement(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Detect lateral movement patterns"""
        correlations = []
        
        lateral_indicators = self.correlation_rules['network']['lateral_movement_indicators']
        lateral_alerts = [a for a in alerts if a.get('category') in lateral_indicators]
        
        if len(lateral_alerts) >= 2:
            correlation = CorrelationResult(
                correlation_id=f"lateral_movement_{len(lateral_alerts)}",
                correlation_type="lateral_movement",
                confidence_score=0.8,
                related_alerts=[alert.get('_id', '') for alert in lateral_alerts],
                severity="high",
                description=f"Lateral movement detected: {len(lateral_alerts)} indicators",
                attack_stage="lateral_movement",
                threat_indicators=["lateral_movement", "internal_network"]
            )
            correlations.append(correlation)
        
        return correlations
    
    def _detect_data_exfiltration(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Detect data exfiltration patterns"""
        correlations = []
        
        exfil_protocols = self.correlation_rules['network']['data_exfil_protocols']
        exfil_alerts = [a for a in alerts if a.get('protocol') in exfil_protocols or 
                       a.get('category') == 'data_exfiltration']
        
        if len(exfil_alerts) >= 1:
            correlation = CorrelationResult(
                correlation_id=f"data_exfil_{len(exfil_alerts)}",
                correlation_type="data_exfiltration",
                confidence_score=0.85,
                related_alerts=[alert.get('_id', '') for alert in exfil_alerts],
                severity="critical",
                description=f"Data exfiltration detected: {len(exfil_alerts)} events",
                attack_stage="exfiltration",
                business_impact="high",
                threat_indicators=["data_exfil", "data_breach"]
            )
            correlations.append(correlation)
        
        return correlations
    
    def _detect_c2_communications(self, alerts: List[Dict[str, Any]]) -> List[CorrelationResult]:
        """Detect command and control communications"""
        correlations = []
        
        c2_alerts = [a for a in alerts if a.get('category') in ['c2_communication', 'malware_c2']]
        
        if len(c2_alerts) >= 2:
            correlation = CorrelationResult(
                correlation_id=f"c2_comm_{len(c2_alerts)}",
                correlation_type="c2_communication",
                confidence_score=0.8,
                related_alerts=[alert.get('_id', '') for alert in c2_alerts],
                severity="high",
                description=f"C2 communications detected: {len(c2_alerts)} events",
                attack_stage="command_and_control",
                threat_indicators=["c2_communication", "malware_beaconing"]
            )
            correlations.append(correlation)
        
        return correlations
    
    def _detect_time_anomalies(self, alerts: List[Dict[str, Any]]) -> bool:
        """Detect unusual time-based activity patterns"""
        unusual_hours = self.correlation_rules['behavioral']['unusual_time_range']
        
        for alert in alerts:
            timestamp = alert.get('timestamp')
            if timestamp and isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    if unusual_hours[0] <= hour or hour <= unusual_hours[1]:
                        return True
                except:
                    continue
        
        return False
    
    def _detect_privilege_escalation(self, alerts: List[Dict[str, Any]]) -> bool:
        """Detect privilege escalation patterns"""
        escalation_indicators = self.correlation_rules['behavioral']['privilege_escalation_indicators']
        
        for alert in alerts:
            if alert.get('category') in escalation_indicators or \
               any(indicator in alert.get('description', '').lower() for indicator in escalation_indicators):
                return True
        
        return False
    
    async def _extract_and_match_iocs(self, alerts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Extract and match IOCs against threat intelligence"""
        ioc_matches = {}
        
        for alert in alerts:
            alert_id = alert.get('_id', '')
            alert_iocs = {}
            
            # Extract IPs, domains, hashes from alert
            source_ip = alert.get('source_ip')
            dest_ip = alert.get('destination_ip')
            domain = alert.get('domain')
            file_hash = alert.get('file_hash')
            
            # Mock threat intelligence matching (in real implementation, integrate with threat intel feeds)
            if source_ip and self._is_malicious_ip(source_ip):
                alert_iocs[source_ip] = {'actor': 'apt28', 'malware': 'trickbot'}
            
            if dest_ip and self._is_malicious_ip(dest_ip):
                alert_iocs[dest_ip] = {'actor': 'apt29', 'malware': 'emotet'}
            
            if domain and self._is_malicious_domain(domain):
                alert_iocs[domain] = {'actor': 'Lazarus Group', 'malware': 'wannacry'}
            
            if file_hash and self._is_malware_hash(file_hash):
                alert_iocs[file_hash] = {'actor': 'unknown', 'malware': 'ryuk'}
            
            if alert_iocs:
                ioc_matches[alert_id] = alert_iocs
        
        return ioc_matches
    
    def _is_malicious_ip(self, ip: str) -> bool:
        """Mock malicious IP check (integrate with real threat intel)"""
        # Mock malicious IPs for demonstration
        malicious_ips = ['192.168.1.100', '10.0.0.50', '172.16.0.25']
        return ip in malicious_ips
    
    def _is_malicious_domain(self, domain: str) -> bool:
        """Mock malicious domain check"""
        malicious_domains = ['malicious-site.com', 'c2-server.net', 'bad-domain.org']
        return domain in malicious_domains if domain else False
    
    def _is_malware_hash(self, file_hash: str) -> bool:
        """Mock malware hash check"""
        malware_hashes = ['a1b2c3d4e5f6', 'deadbeef1234', 'badhash5678']
        return file_hash in malware_hashes if file_hash else False
    
    def _is_critical_asset(self, asset: str) -> bool:
        """Check if asset is critical"""
        critical_assets = self.correlation_rules['asset_criticality']['critical_assets']
        return any(critical in asset.lower() for critical in critical_assets)
    
    def _calculate_severity(self, alerts: List[Dict[str, Any]]) -> str:
        """Calculate combined severity for alert group"""
        severities = [alert.get('severity', 'low') for alert in alerts]
        severity_counts = Counter(severities)
        
        if severity_counts.get('critical', 0) > 0:
            return 'critical'
        elif severity_counts.get('high', 0) >= 2:
            return 'critical'
        elif severity_counts.get('high', 0) > 0:
            return 'high'
        elif severity_counts.get('medium', 0) >= 3:
            return 'high'
        else:
            return 'medium'
    
    def _map_attack_stage(self, attack_type: str) -> str:
        """Map attack type to MITRE ATT&CK stage"""
        stage_mapping = {
            'brute_force': 'initial_access',
            'malware': 'execution',
            'data_exfiltration': 'exfiltration',
            'reconnaissance': 'reconnaissance',
            'lateral_movement': 'lateral_movement',
            'privilege_escalation': 'privilege_escalation',
            'persistence': 'persistence'
        }
        return stage_mapping.get(attack_type, 'unknown')
    
    async def get_correlation_summary(self, correlations: List[CorrelationResult]) -> Dict[str, Any]:
        """Generate correlation analysis summary"""
        summary = {
            'total_correlations': len(correlations),
            'correlation_types': Counter([c.correlation_type for c in correlations]),
            'severity_distribution': Counter([c.severity for c in correlations]),
            'attack_stages': Counter([c.attack_stage for c in correlations if c.attack_stage]),
            'high_confidence_correlations': [c for c in correlations if c.confidence_score > 0.8],
            'critical_correlations': [c for c in correlations if c.severity == 'critical']
        }
        
        return summary

# Global correlation engine instance
correlation_engine = AdvancedCorrelationEngine()
