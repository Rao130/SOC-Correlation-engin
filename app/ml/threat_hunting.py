"""
Automated Threat Hunting System for SOC Correlation Engine
Implements intelligent threat hunting algorithms and automated investigation workflows
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
import re
import hashlib
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

class ThreatHunter:
    """Automated threat hunting system with advanced detection algorithms"""
    
    def __init__(self):
        self.hunting_rules = self._initialize_hunting_rules()
        self.threat_patterns = self._initialize_threat_patterns()
        self.mitre_attck_mapping = self._initialize_mitre_mapping()
        self.investigation_queue = []
        
    def _initialize_hunting_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize automated threat hunting rules"""
        return {
            'lateral_movement': {
                'name': 'Potential Lateral Movement',
                'description': 'Detects suspicious lateral movement patterns',
                'severity': 'high',
                'mitre_tactics': ['TA0008'],  # Lateral Movement
                'indicators': [
                    'multiple_failed_logins',
                    'unusual_admin_access',
                    'remote_execution_attempts'
                ]
            },
            'data_exfiltration': {
                'name': 'Potential Data Exfiltration',
                'description': 'Detects patterns suggesting data theft',
                'severity': 'critical',
                'mitre_tactics': ['TA0010'],  # Exfiltration
                'indicators': [
                    'large_file_transfers',
                    'unusual_network_connections',
                    'sensitive_access_patterns'
                ]
            },
            'privilege_escalation': {
                'name': 'Privilege Escalation Attempts',
                'description': 'Detects attempts to gain elevated privileges',
                'severity': 'high',
                'mitre_tactics': ['TA0004'],  # Privilege Escalation
                'indicators': [
                    'sudo_usage_patterns',
                    'service_account_abuse',
                    'registry_modifications'
                ]
            },
            'persistence_mechanisms': {
                'name': 'Persistence Mechanisms',
                'description': 'Detects malware persistence techniques',
                'severity': 'medium',
                'mitre_tactics': ['TA0003'],  # Persistence
                'indicators': [
                    'scheduled_task_creation',
                    'startup_modifications',
                    'service_installation'
                ]
            },
            'command_and_control': {
                'name': 'Command and Control Communication',
                'description': 'Detects C2 communication patterns',
                'severity': 'high',
                'mitre_tactics': ['TA0011'],  # Command and Control
                'indicators': [
                    'beaconing_patterns',
                    'dns_tunneling',
                    'unusual_ports'
                ]
            }
        }
    
    def _initialize_threat_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known threat patterns and signatures"""
        return {
            'brute_force': {
                'pattern': r'(?i)(failed|login|authentication).*\d+.*times',
                'time_window': timedelta(minutes=5),
                'threshold': 5,
                'severity': 'medium'
            },
            'port_scan': {
                'pattern': r'(?i)(port.*scan|connection.*attempt)',
                'time_window': timedelta(minutes=1),
                'threshold': 10,
                'severity': 'low'
            },
            'malware_execution': {
                'pattern': r'(?i)(malware|virus|trojan).*detected',
                'time_window': timedelta(minutes=1),
                'threshold': 1,
                'severity': 'critical'
            },
            'data_access': {
                'pattern': r'(?i)(sensitive.*data|confidential.*information).*access',
                'time_window': timedelta(hours=1),
                'threshold': 3,
                'severity': 'high'
            }
        }
    
    def _initialize_mitre_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize MITRE ATT&CK framework mapping"""
        return {
            'TA0001': {  # Initial Access
                'name': 'Initial Access',
                'techniques': ['T1078', 'T1190', 'T1133'],
                'description': 'Adversary trying to get into your network'
            },
            'TA0002': {  # Execution
                'name': 'Execution',
                'techniques': ['T1059', 'T1203', 'T1055'],
                'description': 'Running malicious code'
            },
            'TA0003': {  # Persistence
                'name': 'Persistence',
                'techniques': ['T1053', 'T1543', 'T1547'],
                'description': 'Maintaining presence in the network'
            },
            'TA0004': {  # Privilege Escalation
                'name': 'Privilege Escalation',
                'techniques': ['T1068', 'T1548', 'T1484'],
                'description': 'Gaining higher-level permissions'
            },
            'TA0005': {  # Defense Evasion
                'name': 'Defense Evasion',
                'techniques': ['T1027', 'T1140', 'T1562'],
                'description': 'Avoiding detection'
            },
            'TA0006': {  # Credential Access
                'name': 'Credential Access',
                'techniques': ['T1003', 'T1110', 'T1555'],
                'description': 'Stealing account credentials'
            },
            'TA0007': {  # Discovery
                'name': 'Discovery',
                'techniques': ['T1018', 'T1082', 'T1046'],
                'description': 'Learning about the environment'
            },
            'TA0008': {  # Lateral Movement
                'name': 'Lateral Movement',
                'techniques': ['T1021', 'T1570', 'T1020'],
                'description': 'Moving through the network'
            },
            'TA0009': {  # Collection
                'name': 'Collection',
                'techniques': ['T1113', 'T1115', 'T1560'],
                'description': 'Gathering data of interest'
            },
            'TA0010': {  # Exfiltration
                'name': 'Exfiltration',
                'techniques': ['T1041', 'T1567', 'T1020'],
                'description': 'Stealing data'
            },
            'TA0011': {  # Command and Control
                'name': 'Command and Control',
                'techniques': ['T1071', 'T1105', 'T1095'],
                'description': 'Communicating with infrastructure'
            }
        }
    
    def hunt_for_threats(self, alerts: List[Dict[str, Any]], time_window: int = 24) -> List[Dict[str, Any]]:
        """Main threat hunting function"""
        if not alerts:
            return []
        
        threats_found = []
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(alerts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter by time window
        cutoff_time = datetime.now() - timedelta(hours=time_window)
        df = df[df['timestamp'] >= cutoff_time]
        
        # Run different hunting algorithms
        threats_found.extend(self._hunt_lateral_movement(df))
        threats_found.extend(self._hunt_data_exfiltration(df))
        threats_found.extend(self._hunt_privilege_escalation(df))
        threats_found.extend(self._hunt_persistence_mechanisms(df))
        threats_found.extend(self._hunt_command_control(df))
        threats_found.extend(self._hunt_pattern_based(df))
        threats_found.extend(self._hunt_anomaly_based(df))
        
        # Prioritize and rank threats
        threats_found = self._prioritize_threats(threats_found)
        
        # Generate investigation recommendations
        for threat in threats_found:
            threat['investigation_steps'] = self._generate_investigation_steps(threat)
        
        logger.info(f"Threat hunting completed: {len(threats_found)} threats found")
        return threats_found
    
    def _hunt_lateral_movement(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Hunt for lateral movement patterns"""
        threats = []
        
        # Check for multiple failed logins from different sources
        failed_logins = df[df['description'].str.contains('failed|login', case=False, na=False)]
        
        if len(failed_logins) > 0:
            # Group by source IP
            source_counts = failed_logins.groupby('source').size()
            suspicious_sources = source_counts[source_counts > 3]
            
            for source, count in suspicious_sources.items():
                threats.append({
                    'type': 'lateral_movement',
                    'rule': 'multiple_failed_logins',
                    'severity': 'high',
                    'confidence': min(0.9, 0.3 + (count * 0.1)),
                    'source': source,
                    'count': count,
                    'indicators': failed_logins[failed_logins['source'] == source].to_dict('records'),
                    'mitre_tactics': ['TA0008'],
                    'techniques': ['T1021', 'T1570'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return threats
    
    def _hunt_data_exfiltration(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Hunt for data exfiltration patterns"""
        threats = []
        
        # Check for large data transfers
        data_access = df[df['description'].str.contains('data|file|transfer', case=False, na=False)]
        
        if len(data_access) > 0:
            # Look for patterns in time
            data_access['hour'] = data_access['timestamp'].dt.hour
            unusual_hours = data_access[(data_access['hour'] < 6) | (data_access['hour'] > 22)]
            
            if len(unusual_hours) > 0:
                threats.append({
                    'type': 'data_exfiltration',
                    'rule': 'unusual_time_access',
                    'severity': 'high',
                    'confidence': 0.7,
                    'count': len(unusual_hours),
                    'indicators': unusual_hours.to_dict('records'),
                    'mitre_tactics': ['TA0010'],
                    'techniques': ['T1041', 'T1567'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return threats
    
    def _hunt_privilege_escalation(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Hunt for privilege escalation attempts"""
        threats = []
        
        # Check for admin access patterns
        admin_access = df[df['description'].str.contains('admin|privilege|sudo', case=False, na=False)]
        
        if len(admin_access) > 0:
            # Group by user/entity
            entity_counts = admin_access.groupby('entities').size()
            suspicious_entities = entity_counts[entity_counts > 5]
            
            for entity, count in suspicious_entities.items():
                threats.append({
                    'type': 'privilege_escalation',
                    'rule': 'excessive_admin_access',
                    'severity': 'high',
                    'confidence': min(0.8, 0.4 + (count * 0.08)),
                    'entity': entity,
                    'count': count,
                    'indicators': admin_access[admin_access['entities'] == entity].to_dict('records'),
                    'mitre_tactics': ['TA0004'],
                    'techniques': ['T1068', 'T1548'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return threats
    
    def _hunt_persistence_mechanisms(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Hunt for persistence mechanisms"""
        threats = []
        
        # Check for scheduled tasks or services
        persistence = df[df['description'].str.contains('task|service|startup|registry', case=False, na=False)]
        
        if len(persistence) > 0:
            threats.append({
                'type': 'persistence_mechanisms',
                'rule': 'suspicious_persistence',
                'severity': 'medium',
                'confidence': 0.6,
                'count': len(persistence),
                'indicators': persistence.to_dict('records'),
                'mitre_tactics': ['TA0003'],
                'techniques': ['T1053', 'T1543'],
                'timestamp': datetime.now().isoformat()
            })
        
        return threats
    
    def _hunt_command_control(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Hunt for command and control communication"""
        threats = []
        
        # Check for network connections to suspicious destinations
        network = df[df['category'] == 'network']
        
        if len(network) > 0:
            # Look for beaconing patterns (regular intervals)
            network['hour'] = network['timestamp'].dt.hour
            network['minute'] = network['timestamp'].dt.minute
            
            # Group by source and look for regular patterns
            for source in network['source'].unique():
                source_data = network[network['source'] == source]
                if len(source_data) > 5:
                    # Check for regular intervals
                    time_diffs = source_data['timestamp'].diff().dt.total_seconds()
                    regular_intervals = time_diffs[(time_diffs > 300) & (time_diffs < 1800)]  # 5-30 minutes
                    
                    if len(regular_intervals) > 3:
                        threats.append({
                            'type': 'command_and_control',
                            'rule': 'beaconing_pattern',
                            'severity': 'high',
                            'confidence': 0.8,
                            'source': source,
                            'interval_patterns': regular_intervals.tolist(),
                            'indicators': source_data.to_dict('records'),
                            'mitre_tactics': ['TA0011'],
                            'techniques': ['T1071', 'T1105'],
                            'timestamp': datetime.now().isoformat()
                        })
        
        return threats
    
    def _hunt_pattern_based(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Pattern-based threat hunting"""
        threats = []
        
        for pattern_name, pattern_info in self.threat_patterns.items():
            matching_alerts = df[df['description'].str.contains(pattern_info['pattern'], regex=True, na=False)]
            
            if len(matching_alerts) >= pattern_info['threshold']:
                threats.append({
                    'type': 'pattern_based',
                    'rule': pattern_name,
                    'severity': pattern_info['severity'],
                    'confidence': min(0.9, 0.5 + (len(matching_alerts) * 0.1)),
                    'count': len(matching_alerts),
                    'indicators': matching_alerts.to_dict('records'),
                    'pattern_matched': pattern_info['pattern'],
                    'timestamp': datetime.now().isoformat()
                })
        
        return threats
    
    def _hunt_anomaly_based(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Anomaly-based threat hunting"""
        threats = []
        
        # Statistical anomaly detection
        for category in df['category'].unique():
            category_data = df[df['category'] == category]
            
            if len(category_data) > 10:
                # Check for unusual spikes
                hourly_counts = category_data.groupby(category_data['timestamp'].dt.hour).size()
                mean_count = hourly_counts.mean()
                std_count = hourly_counts.std()
                
                # Look for hours with activity > 2 standard deviations above mean
                anomaly_hours = hourly_counts[hourly_counts > (mean_count + 2 * std_count)]
                
                for hour, count in anomaly_hours.items():
                    threats.append({
                        'type': 'anomaly_based',
                        'rule': 'unusual_activity_spike',
                        'severity': 'medium',
                        'confidence': 0.7,
                        'category': category,
                        'hour': hour,
                        'count': count,
                        'expected_range': f"{mean_count:.1f} ± {2*std_count:.1f}",
                        'indicators': category_data[category_data['timestamp'].dt.hour == hour].to_dict('records'),
                        'timestamp': datetime.now().isoformat()
                    })
        
        return threats
    
    def _prioritize_threats(self, threats: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize threats based on severity and confidence"""
        severity_weights = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        
        for threat in threats:
            threat['priority_score'] = (
                severity_weights.get(threat['severity'], 1) * threat['confidence']
            )
        
        return sorted(threats, key=lambda x: x['priority_score'], reverse=True)
    
    def _generate_investigation_steps(self, threat: Dict[str, Any]) -> List[str]:
        """Generate automated investigation steps"""
        steps = []
        
        if threat['type'] == 'lateral_movement':
            steps.extend([
                "Review source IP reputation and geolocation",
                "Check for successful logins from the same source",
                "Analyze affected user accounts for compromise",
                "Review network logs for lateral movement paths"
            ])
        
        elif threat['type'] == 'data_exfiltration':
            steps.extend([
                "Identify what data was accessed",
                "Check data transfer logs and destinations",
                "Review user permissions and access patterns",
                "Assess potential impact and data sensitivity"
            ])
        
        elif threat['type'] == 'privilege_escalation':
            steps.extend([
                "Review privilege escalation attempts",
                "Check for successful privilege elevation",
                "Analyze administrative account usage",
                "Review system logs for suspicious activities"
            ])
        
        elif threat['type'] == 'command_and_control':
            steps.extend([
                "Analyze network traffic patterns",
                "Check DNS queries for suspicious domains",
                "Review endpoint network connections",
                "Investigate potential malware infections"
            ])
        
        else:
            steps.extend([
                "Review threat indicators and context",
                "Analyze affected systems and users",
                "Check for related security events",
                "Assess potential impact and risk"
            ])
        
        return steps
    
    def generate_threat_report(self, threats: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive threat hunting report"""
        if not threats:
            return {
                'summary': 'No threats detected',
                'total_threats': 0,
                'high_priority_threats': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        # Analyze threat distribution
        threat_types = Counter([t['type'] for t in threats])
        severity_distribution = Counter([t['severity'] for t in threats])
        mitre_tactics = Counter([tactic for t in threats for tactic in t.get('mitre_tactics', [])])
        
        # Generate recommendations
        recommendations = self._generate_recommendations(threats)
        
        return {
            'summary': f'{len(threats)} threats detected',
            'total_threats': len(threats),
            'high_priority_threats': len([t for t in threats if t['severity'] in ['critical', 'high']]),
            'threat_distribution': dict(threat_types),
            'severity_distribution': dict(severity_distribution),
            'mitre_tactics': dict(mitre_tactics),
            'top_threats': threats[:5],
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, threats: List[Dict[str, Any]]) -> List[str]:
        """Generate security recommendations based on detected threats"""
        recommendations = []
        
        threat_types = set([t['type'] for t in threats])
        
        if 'lateral_movement' in threat_types:
            recommendations.append("Implement network segmentation to limit lateral movement")
            recommendations.append("Enhance monitoring of privileged account usage")
        
        if 'data_exfiltration' in threat_types:
            recommendations.append("Implement data loss prevention (DLP) controls")
            recommendations.append("Review and restrict data access permissions")
        
        if 'privilege_escalation' in threat_types:
            recommendations.append("Implement just-in-time privileged access management")
            recommendations.append("Enhance monitoring of privilege escalation attempts")
        
        if 'command_and_control' in threat_types:
            recommendations.append("Implement DNS filtering and monitoring")
            recommendations.append("Enhance endpoint detection and response capabilities")
        
        if 'persistence_mechanisms' in threat_types:
            recommendations.append("Implement application whitelisting")
            recommendations.append("Enhance monitoring of system modifications")
        
        # General recommendations
        recommendations.append("Review and update security policies and procedures")
        recommendations.append("Conduct security awareness training for relevant staff")
        
        return list(set(recommendations))  # Remove duplicates
