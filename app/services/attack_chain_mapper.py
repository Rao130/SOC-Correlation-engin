"""
Real-Time Attack Chain Mapping Engine
MITRE ATT&CK based attack path reconstruction and visualization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import networkx as nx
import json
from enum import Enum

logger = logging.getLogger(__name__)

class AttackStage(Enum):
    """MITRE ATT&CK attack stages"""
    RECONNAISSANCE = "reconnaissance"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DEFENSE_EVASION = "defense_evasion"
    CREDENTIAL_ACCESS = "credential_access"
    DISCOVERY = "discovery"
    LATERAL_MOVEMENT = "lateral_movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command_and_control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

@dataclass
class AttackChainNode:
    """Single node in attack chain"""
    node_id: str
    alert_id: str
    stage: AttackStage
    timestamp: datetime
    technique_id: str
    technique_name: str
    source_ip: str
    target_ip: str
    user: str
    asset: str
    confidence: float
    description: str
    related_alerts: List[str] = field(default_factory=list)

@dataclass
class AttackChain:
    """Complete attack chain representation"""
    chain_id: str
    attacker_id: Optional[str]
    start_time: datetime
    end_time: datetime
    duration: timedelta
    stages: List[AttackStage]
    nodes: List[AttackChainNode]
    attack_graph: nx.DiGraph
    confidence_score: float
    severity: str
    threat_actor: Optional[str]
    malware_family: Optional[str]
    affected_assets: Set[str]
    business_impact: str
    containment_status: str
    mitigation_recommendations: List[str]

class AttackChainMapper:
    """Real-time attack chain reconstruction engine"""
    
    def __init__(self):
        self.attack_chains = {}
        self.active_chains = {}
        self.mitre_mapping = self._load_mitre_mapping()
        self.stage_transitions = self._load_stage_transitions()
        self.technique_patterns = self._load_technique_patterns()
        self.chain_timeout = timedelta(hours=24)
        self.min_chain_confidence = 0.6
        
    def _load_mitre_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Load MITRE ATT&CK technique mapping"""
        return {
            # Reconnaissance
            'reconnaissance': {
                'techniques': {
                    'T1595': 'Active Scanning',
                    'T1592': 'Gather Victim Host Information',
                    'T1590': 'Gather Victim Network Information',
                    'T1589': 'Gather Victim Identity Information'
                },
                'indicators': ['port_scan', 'network_discovery', 'dns_enumeration', 'whois_lookup'],
                'confidence_threshold': 0.5
            },
            # Initial Access
            'initial_access': {
                'techniques': {
                    'T1190': 'Exploit Public-Facing Application',
                    'T1078': 'Valid Accounts',
                    'T1566': 'Phishing',
                    'T1193': 'Spearphishing Attachment',
                    'T1078': 'Valid Accounts'
                },
                'indicators': ['exploit_attempt', 'phishing', 'brute_force', 'credential_stuffing'],
                'confidence_threshold': 0.7
            },
            # Execution
            'execution': {
                'techniques': {
                    'T1059': 'Command and Scripting Interpreter',
                    'T1053': 'Scheduled Task',
                    'T1064': 'Scripting',
                    'T1204': 'User Execution'
                },
                'indicators': ['powershell', 'cmd', 'script_execution', 'scheduled_task'],
                'confidence_threshold': 0.6
            },
            # Persistence
            'persistence': {
                'techniques': {
                    'T1543': 'Create or Modify System Process',
                    'T1050': 'New Service',
                    'T1547': 'Boot or Logon Autostart Execution',
                    'T1136': 'Create Account'
                },
                'indicators': ['service_creation', 'registry_modification', 'startup_folder', 'new_account'],
                'confidence_threshold': 0.7
            },
            # Privilege Escalation
            'privilege_escalation': {
                'techniques': {
                    'T1068': 'Exploitation for Privilege Escalation',
                    'T1548': 'Abuse Elevation Control Mechanism',
                    'T1134': 'Access Token Manipulation',
                    'T1078': 'Valid Accounts'
                },
                'indicators': ['privilege_escalation', 'sudo', 'runas', 'token_manipulation'],
                'confidence_threshold': 0.8
            },
            # Lateral Movement
            'lateral_movement': {
                'techniques': {
                    'T1021': 'Remote Services',
                    'T1570': 'Lateral Tool Transfer',
                    'T1539': 'Steal Web Session Cookie',
                    'T1550': 'Use Alternate Authentication Material'
                },
                'indicators': ['smb', 'rpc', 'winrm', 'rdp', 'ssh', 'psexec'],
                'confidence_threshold': 0.7
            },
            # Collection
            'collection': {
                'techniques': {
                    'T1005': 'Data from Local System',
                    'T1113': 'Screen Capture',
                    'T1125': 'Video Capture',
                    'T1119': 'Automated Collection'
                },
                'indicators': ['file_access', 'screenshot', 'clipboard_access', 'data_collection'],
                'confidence_threshold': 0.6
            },
            # Command and Control
            'command_and_control': {
                'techniques': {
                    'T1071': 'Application Layer Protocol',
                    'T1090': 'Proxy',
                    'T1095': 'Non-Application Layer Protocol',
                    'T1102': 'Web Service'
                },
                'indicators': ['c2_communication', 'dns_tunneling', 'http_c2', 'beaconing'],
                'confidence_threshold': 0.8
            },
            # Exfiltration
            'exfiltration': {
                'techniques': {
                    'T1041': 'Exfiltration Over C2 Channel',
                    'T1567': 'Exfiltration Over Web Service',
                    'T1020': 'Automated Exfiltration',
                    'T1048': 'Exfiltration Over Alternative Protocol'
                },
                'indicators': ['data_exfiltration', 'ftp_upload', 'http_post_large', 'dns_exfil'],
                'confidence_threshold': 0.9
            },
            # Impact
            'impact': {
                'techniques': {
                    'T1485': 'Data Destruction',
                    'T1486': 'Data Encrypted for Impact',
                    'T1491': 'Defacement',
                    'T1499': 'Endpoint Denial of Service'
                },
                'indicators': ['data_deletion', 'ransomware', 'website_defacement', 'dos_attack'],
                'confidence_threshold': 0.9
            }
        }
    
    def _load_stage_transitions(self) -> Dict[str, List[str]]:
        """Load valid stage transitions based on MITRE ATT&CK"""
        return {
            AttackStage.RECONNAISSANCE.value: [AttackStage.INITIAL_ACCESS.value],
            AttackStage.INITIAL_ACCESS.value: [AttackStage.EXECUTION.value, AttackStage.PERSISTENCE.value],
            AttackStage.EXECUTION.value: [AttackStage.PERSISTENCE.value, AttackStage.PRIVILEGE_ESCALATION.value],
            AttackStage.PERSISTENCE.value: [AttackStage.PRIVILEGE_ESCALATION.value, AttackStage.DEFENSE_EVASION.value],
            AttackStage.PRIVILEGE_ESCALATION.value: [AttackStage.DEFENSE_EVASION.value, AttackStage.CREDENTIAL_ACCESS.value],
            AttackStage.DEFENSE_EVASION.value: [AttackStage.CREDENTIAL_ACCESS.value, AttackStage.DISCOVERY.value],
            AttackStage.CREDENTIAL_ACCESS.value: [AttackStage.DISCOVERY.value, AttackStage.LATERAL_MOVEMENT.value],
            AttackStage.DISCOVERY.value: [AttackStage.LATERAL_MOVEMENT.value, AttackStage.COLLECTION.value],
            AttackStage.LATERAL_MOVEMENT.value: [AttackStage.COLLECTION.value, AttackStage.COMMAND_AND_CONTROL.value],
            AttackStage.COLLECTION.value: [AttackStage.COMMAND_AND_CONTROL.value, AttackStage.EXFILTRATION.value],
            AttackStage.COMMAND_AND_CONTROL.value: [AttackStage.EXFILTRATION.value, AttackStage.IMPACT.value],
            AttackStage.EXFILTRATION.value: [AttackStage.IMPACT.value]
        }
    
    def _load_technique_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load technique detection patterns"""
        return {
            'port_scan': {
                'stage': AttackStage.RECONNAISSANCE,
                'technique_id': 'T1595',
                'confidence': 0.7,
                'keywords': ['port scan', 'network scan', 'service discovery']
            },
            'phishing': {
                'stage': AttackStage.INITIAL_ACCESS,
                'technique_id': 'T1566',
                'confidence': 0.8,
                'keywords': ['phishing', 'spear phishing', 'email attack']
            },
            'brute_force': {
                'stage': AttackStage.INITIAL_ACCESS,
                'technique_id': 'T1110',
                'confidence': 0.6,
                'keywords': ['brute force', 'password guess', 'login attempt']
            },
            'powershell': {
                'stage': AttackStage.EXECUTION,
                'technique_id': 'T1059',
                'confidence': 0.7,
                'keywords': ['powershell', 'ps1', 'script execution']
            },
            'privilege_escalation': {
                'stage': AttackStage.PRIVILEGE_ESCALATION,
                'technique_id': 'T1068',
                'confidence': 0.8,
                'keywords': ['privilege escalation', 'sudo', 'runas', 'admin']
            },
            'lateral_movement': {
                'stage': AttackStage.LATERAL_MOVEMENT,
                'technique_id': 'T1021',
                'confidence': 0.7,
                'keywords': ['lateral movement', 'smb', 'rpc', 'remote']
            },
            'data_exfiltration': {
                'stage': AttackStage.EXFILTRATION,
                'technique_id': 'T1567',
                'confidence': 0.9,
                'keywords': ['data exfiltration', 'data theft', 'upload']
            },
            'ransomware': {
                'stage': AttackStage.IMPACT,
                'technique_id': 'T1486',
                'confidence': 0.95,
                'keywords': ['ransomware', 'encryption', 'data locked']
            }
        }
    
    async def map_attack_chains(self, alerts: List[Dict[str, Any]]) -> List[AttackChain]:
        """
        Map alerts to attack chains in real-time
        """
        try:
            logger.info(f"🔗 Mapping {len(alerts)} alerts to attack chains")
            
            # Convert alerts to attack nodes
            attack_nodes = await self._alerts_to_nodes(alerts)
            
            # Group nodes by potential attacker/session
            session_groups = self._group_by_session(attack_nodes)
            
            # Build attack chains for each session
            attack_chains = []
            for session_id, session_nodes in session_groups.items():
                chain = await self._build_attack_chain(session_id, session_nodes)
                if chain and chain.confidence_score >= self.min_chain_confidence:
                    attack_chains.append(chain)
            
            # Update active chains
            await self._update_active_chains(attack_chains)
            
            # Clean up old chains
            await self._cleanup_old_chains()
            
            logger.info(f"✅ Mapped {len(attack_chains)} attack chains")
            return attack_chains
            
        except Exception as e:
            logger.error(f"❌ Attack chain mapping failed: {e}")
            return []
    
    async def _alerts_to_nodes(self, alerts: List[Dict[str, Any]]) -> List[AttackChainNode]:
        """Convert alerts to attack chain nodes"""
        nodes = []
        
        for alert in alerts:
            stage = await self._classify_attack_stage(alert)
            if not stage:
                continue
            
            technique_info = self._get_technique_info(alert, stage)
            
            node = AttackChainNode(
                node_id=f"node_{alert.get('_id', '')}",
                alert_id=alert.get('_id', ''),
                stage=stage,
                timestamp=self._parse_timestamp(alert.get('timestamp')),
                technique_id=technique_info['id'],
                technique_name=technique_info['name'],
                source_ip=alert.get('source_ip', ''),
                target_ip=alert.get('destination_ip', ''),
                user=alert.get('user', ''),
                asset=alert.get('target_asset', ''),
                confidence=technique_info['confidence'],
                description=alert.get('description', ''),
                related_alerts=[alert.get('_id', '')]
            )
            
            nodes.append(node)
        
        return nodes
    
    async def _classify_attack_stage(self, alert: Dict[str, Any]) -> Optional[AttackStage]:
        """Classify alert to MITRE ATT&CK stage"""
        category = alert.get('category', '').lower()
        title = alert.get('title', '').lower()
        description = alert.get('description', '').lower()
        
        # Combine all text for analysis
        text = f"{category} {title} {description}"
        
        # Check against technique patterns
        for pattern_name, pattern_info in self.technique_patterns.items():
            keywords = pattern_info['keywords']
            if any(keyword in text for keyword in keywords):
                return pattern_info['stage']
        
        # Fallback to category mapping
        category_mapping = {
            'reconnaissance': AttackStage.RECONNAISSANCE,
            'initial_access': AttackStage.INITIAL_ACCESS,
            'execution': AttackStage.EXECUTION,
            'persistence': AttackStage.PERSISTENCE,
            'privilege_escalation': AttackStage.PRIVILEGE_ESCALATION,
            'lateral_movement': AttackStage.LATERAL_MOVEMENT,
            'collection': AttackStage.COLLECTION,
            'command_and_control': AttackStage.COMMAND_AND_CONTROL,
            'exfiltration': AttackStage.EXFILTRATION,
            'impact': AttackStage.IMPACT
        }
        
        return category_mapping.get(category)
    
    def _get_technique_info(self, alert: Dict[str, Any], stage: AttackStage) -> Dict[str, str]:
        """Get MITRE technique information"""
        stage_info = self.mitre_mapping.get(stage.value, {})
        techniques = stage_info.get('techniques', {})
        
        # Default technique for the stage
        if techniques:
            technique_id, technique_name = list(techniques.items())[0]
        else:
            technique_id, technique_name = 'T0000', 'Unknown'
        
        confidence = stage_info.get('confidence_threshold', 0.5)
        
        return {
            'id': technique_id,
            'name': technique_name,
            'confidence': confidence
        }
    
    def _group_by_session(self, nodes: List[AttackChainNode]) -> Dict[str, List[AttackChainNode]]:
        """Group attack nodes by attacker session"""
        session_groups = defaultdict(list)
        
        for node in nodes:
            # Group by source IP, user, or similar characteristics
            session_key = self._generate_session_key(node)
            session_groups[session_key].append(node)
        
        return session_groups
    
    def _generate_session_key(self, node: AttackChainNode) -> str:
        """Generate session key for grouping"""
        # Priority: user > source_ip > target_asset
        if node.user:
            return f"user_{node.user}"
        elif node.source_ip:
            return f"ip_{node.source_ip}"
        elif node.asset:
            return f"asset_{node.asset}"
        else:
            return f"unknown_{node.node_id}"
    
    async def _build_attack_chain(self, session_id: str, nodes: List[AttackChainNode]) -> Optional[AttackChain]:
        """Build attack chain from session nodes"""
        if len(nodes) < 2:
            return None
        
        # Sort nodes by timestamp
        nodes.sort(key=lambda x: x.timestamp)
        
        # Build attack graph
        attack_graph = nx.DiGraph()
        
        # Add nodes to graph
        for node in nodes:
            attack_graph.add_node(node.node_id, **{
                'stage': node.stage.value,
                'timestamp': node.timestamp,
                'technique': node.technique_name,
                'confidence': node.confidence
            })
        
        # Add edges based on temporal and logical connections
        for i in range(len(nodes) - 1):
            current_node = nodes[i]
            next_node = nodes[i + 1]
            
            # Check if transition is valid
            if self._is_valid_transition(current_node.stage, next_node.stage):
                attack_graph.add_edge(current_node.node_id, next_node.node_id, 
                    weight=self._calculate_transition_weight(current_node, next_node))
        
        # Calculate chain metrics
        stages = [node.stage for node in nodes]
        start_time = nodes[0].timestamp
        end_time = nodes[-1].timestamp
        duration = end_time - start_time
        
        # Calculate confidence score
        confidence_score = self._calculate_chain_confidence(nodes, attack_graph)
        
        # Determine severity
        severity = self._calculate_chain_severity(nodes)
        
        # Identify threat actor and malware
        threat_actor = self._identify_threat_actor(nodes)
        malware_family = self._identify_malware_family(nodes)
        
        # Get affected assets
        affected_assets = {node.asset for node in nodes if node.asset}
        
        # Assess business impact
        business_impact = self._assess_business_impact(nodes, severity)
        
        # Generate mitigation recommendations
        recommendations = self._generate_mitigation_recommendations(nodes, stages)
        
        return AttackChain(
            chain_id=f"chain_{session_id}_{int(start_time.timestamp())}",
            attacker_id=session_id,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            stages=stages,
            nodes=nodes,
            attack_graph=attack_graph,
            confidence_score=confidence_score,
            severity=severity,
            threat_actor=threat_actor,
            malware_family=malware_family,
            affected_assets=affected_assets,
            business_impact=business_impact,
            containment_status="active",
            mitigation_recommendations=recommendations
        )
    
    def _is_valid_transition(self, from_stage: AttackStage, to_stage: AttackStage) -> bool:
        """Check if stage transition is valid"""
        valid_transitions = self.stage_transitions.get(from_stage.value, [])
        return to_stage.value in valid_transitions
    
    def _calculate_transition_weight(self, from_node: AttackChainNode, to_node: AttackChainNode) -> float:
        """Calculate weight for transition between nodes"""
        # Base weight on temporal proximity
        time_diff = (to_node.timestamp - from_node.timestamp).total_seconds()
        
        # Closer in time = higher weight
        if time_diff < 300:  # 5 minutes
            temporal_weight = 1.0
        elif time_diff < 3600:  # 1 hour
            temporal_weight = 0.8
        elif time_diff < 86400:  # 1 day
            temporal_weight = 0.6
        else:
            temporal_weight = 0.4
        
        # Adjust for logical progression
        stage_progression = self._get_stage_progression_score(from_node.stage, to_node.stage)
        
        return temporal_weight * stage_progression
    
    def _get_stage_progression_score(self, from_stage: AttackStage, to_stage: AttackStage) -> float:
        """Get score for stage progression"""
        # Define stage order for progression scoring
        stage_order = [
            AttackStage.RECONNAISSANCE,
            AttackStage.INITIAL_ACCESS,
            AttackStage.EXECUTION,
            AttackStage.PERSISTENCE,
            AttackStage.PRIVILEGE_ESCALATION,
            AttackStage.DEFENSE_EVASION,
            AttackStage.CREDENTIAL_ACCESS,
            AttackStage.DISCOVERY,
            AttackStage.LATERAL_MOVEMENT,
            AttackStage.COLLECTION,
            AttackStage.COMMAND_AND_CONTROL,
            AttackStage.EXFILTRATION,
            AttackStage.IMPACT
        ]
        
        try:
            from_index = stage_order.index(from_stage)
            to_index = stage_order.index(to_stage)
            
            if to_index > from_index:
                return 1.0  # Forward progression
            elif to_index == from_index:
                return 0.5  # Same stage
            else:
                return 0.3  # Backward progression (less likely)
        except ValueError:
            return 0.5
    
    def _calculate_chain_confidence(self, nodes: List[AttackChainNode], graph: nx.DiGraph) -> float:
        """Calculate overall confidence score for attack chain"""
        if not nodes:
            return 0.0
        
        # Average node confidence
        node_confidence = sum(node.confidence for node in nodes) / len(nodes)
        
        # Graph connectivity score
        if len(nodes) > 1:
            connectivity = len(graph.edges()) / (len(nodes) - 1)
        else:
            connectivity = 0.0
        
        # Temporal consistency score
        temporal_score = self._calculate_temporal_consistency(nodes)
        
        # Stage progression score
        stage_score = self._calculate_stage_progression(nodes)
        
        # Weighted combination
        overall_confidence = (
            node_confidence * 0.4 +
            connectivity * 0.2 +
            temporal_score * 0.2 +
            stage_score * 0.2
        )
        
        return min(overall_confidence, 1.0)
    
    def _calculate_temporal_consistency(self, nodes: List[AttackChainNode]) -> float:
        """Calculate temporal consistency score"""
        if len(nodes) < 2:
            return 1.0
        
        # Check if timestamps are reasonable
        time_gaps = []
        for i in range(len(nodes) - 1):
            gap = (nodes[i + 1].timestamp - nodes[i].timestamp).total_seconds()
            time_gaps.append(gap)
        
        # Penalize very large gaps
        avg_gap = sum(time_gaps) / len(time_gaps)
        
        if avg_gap < 3600:  # Less than 1 hour average
            return 1.0
        elif avg_gap < 86400:  # Less than 1 day average
            return 0.8
        else:
            return 0.6
    
    def _calculate_stage_progression(self, nodes: List[AttackChainNode]) -> float:
        """Calculate stage progression score"""
        if len(nodes) < 2:
            return 1.0
        
        progression_count = 0
        total_transitions = len(nodes) - 1
        
        for i in range(total_transitions):
            if self._is_valid_transition(nodes[i].stage, nodes[i + 1].stage):
                progression_count += 1
        
        return progression_count / total_transitions if total_transitions > 0 else 0.0
    
    def _calculate_chain_severity(self, nodes: List[AttackChainNode]) -> str:
        """Calculate overall severity of attack chain"""
        stage_severity = {
            AttackStage.RECONNAISSANCE: 'low',
            AttackStage.INITIAL_ACCESS: 'medium',
            AttackStage.EXECUTION: 'medium',
            AttackStage.PERSISTENCE: 'high',
            AttackStage.PRIVILEGE_ESCALATION: 'high',
            AttackStage.DEFENSE_EVASION: 'high',
            AttackStage.CREDENTIAL_ACCESS: 'high',
            AttackStage.DISCOVERY: 'medium',
            AttackStage.LATERAL_MOVEMENT: 'high',
            AttackStage.COLLECTION: 'high',
            AttackStage.COMMAND_AND_CONTROL: 'high',
            AttackStage.EXFILTRATION: 'critical',
            AttackStage.IMPACT: 'critical'
        }
        
        # Get highest severity stage
        severities = [stage_severity.get(node.stage, 'medium') for node in nodes]
        
        if 'critical' in severities:
            return 'critical'
        elif 'high' in severities:
            return 'high'
        elif 'medium' in severities:
            return 'medium'
        else:
            return 'low'
    
    def _identify_threat_actor(self, nodes: List[AttackChainNode]) -> Optional[str]:
        """Identify potential threat actor"""
        # This would integrate with threat intelligence
        # For now, return based on patterns
        stages = [node.stage for node in nodes]
        
        if AttackStage.EXFILTRATION in stages and AttackStage.LATERAL_MOVEMENT in stages:
            return "APT"
        elif AttackStage.RANSOMWARE in stages:
            return "Ransomware Group"
        else:
            return None
    
    def _identify_malware_family(self, nodes: List[AttackChainNode]) -> Optional[str]:
        """Identify potential malware family"""
        # Extract from alert descriptions
        for node in nodes:
            description = node.description.lower()
            if 'emotet' in description:
                return 'Emotet'
            elif 'trickbot' in description:
                return 'TrickBot'
            elif 'wannacry' in description:
                return 'WannaCry'
            elif 'ryuk' in description:
                return 'Ryuk'
        
        return None
    
    def _assess_business_impact(self, nodes: List[AttackChainNode], severity: str) -> str:
        """Assess business impact"""
        critical_assets = {'domain_controller', 'database_server', 'file_server'}
        
        affected_assets = {node.asset for node in nodes if node.asset}
        
        if any(asset in critical_assets for asset in affected_assets):
            return 'critical'
        elif severity == 'critical':
            return 'high'
        elif severity == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _generate_mitigation_recommendations(self, nodes: List[AttackChainNode], stages: List[AttackStage]) -> List[str]:
        """Generate mitigation recommendations"""
        recommendations = []
        
        # Stage-specific recommendations
        stage_recommendations = {
            AttackStage.INITIAL_ACCESS: [
                "Block malicious IPs",
                "Enhance authentication",
                "Update security controls"
            ],
            AttackStage.LATERAL_MOVEMENT: [
                "Segment network",
                "Monitor internal traffic",
                "Review access controls"
            ],
            AttackStage.EXFILTRATION: [
                "Block data transfers",
                "Monitor egress traffic",
                "Enable DLP controls"
            ],
            AttackStage.IMPACT: [
                "Isolate affected systems",
                "Activate incident response",
                "Engage management"
            ]
        }
        
        for stage in set(stages):
            recommendations.extend(stage_recommendations.get(stage, []))
        
        return list(set(recommendations))  # Remove duplicates
    
    def _parse_timestamp(self, timestamp: Any) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        elif isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return datetime.now()
        else:
            return datetime.now()
    
    async def _update_active_chains(self, new_chains: List[AttackChain]):
        """Update active attack chains"""
        for chain in new_chains:
            self.active_chains[chain.chain_id] = chain
    
    async def _cleanup_old_chains(self):
        """Clean up old inactive chains"""
        current_time = datetime.now()
        expired_chains = []
        
        for chain_id, chain in self.active_chains.items():
            if current_time - chain.end_time > self.chain_timeout:
                expired_chains.append(chain_id)
        
        for chain_id in expired_chains:
            del self.active_chains[chain_id]
        
        if expired_chains:
            logger.info(f"🧹 Cleaned up {len(expired_chains)} expired attack chains")
    
    async def get_attack_chain_summary(self) -> Dict[str, Any]:
        """Get summary of active attack chains"""
        if not self.active_chains:
            return {
                'total_chains': 0,
                'active_chains': 0,
                'severity_distribution': {},
                'stage_distribution': {},
                'threat_actors': {}
            }
        
        chains = list(self.active_chains.values())
        
        summary = {
            'total_chains': len(chains),
            'active_chains': len([c for c in chains if c.containment_status == 'active']),
            'severity_distribution': {},
            'stage_distribution': {},
            'threat_actors': {},
            'average_confidence': sum(c.confidence_score for c in chains) / len(chains),
            'critical_chains': [c for c in chains if c.severity == 'critical']
        }
        
        # Calculate distributions
        for chain in chains:
            # Severity distribution
            severity = chain.severity
            summary['severity_distribution'][severity] = summary['severity_distribution'].get(severity, 0) + 1
            
            # Stage distribution
            for stage in chain.stages:
                stage_name = stage.value
                summary['stage_distribution'][stage_name] = summary['stage_distribution'].get(stage_name, 0) + 1
            
            # Threat actors
            if chain.threat_actor:
                actor = chain.threat_actor
                summary['threat_actors'][actor] = summary['threat_actors'].get(actor, 0) + 1
        
        return summary
    
    def visualize_attack_chain(self, chain: AttackChain) -> Dict[str, Any]:
        """Generate attack chain visualization data"""
        visualization = {
            'nodes': [],
            'edges': [],
            'metadata': {
                'chain_id': chain.chain_id,
                'confidence': chain.confidence_score,
                'severity': chain.severity,
                'duration': str(chain.duration),
                'threat_actor': chain.threat_actor,
                'malware_family': chain.malware_family
            }
        }
        
        # Add nodes
        for node in chain.nodes:
            visualization['nodes'].append({
                'id': node.node_id,
                'label': node.technique_name,
                'stage': node.stage.value,
                'timestamp': node.timestamp.isoformat(),
                'confidence': node.confidence,
                'technique_id': node.technique_id,
                'description': node.description
            })
        
        # Add edges
        for edge in chain.attack_graph.edges():
            source, target = edge
            edge_data = chain.attack_graph[source][target]
            visualization['edges'].append({
                'source': source,
                'target': target,
                'weight': edge_data.get('weight', 0.5)
            })
        
        return visualization

# Global attack chain mapper
attack_chain_mapper = AttackChainMapper()
