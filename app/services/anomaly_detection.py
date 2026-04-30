"""
Advanced Anomaly Detection Engine
Machine Learning based behavioral anomaly detection for zero-day threats
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import joblib
import json
from collections import defaultdict, deque
from enum import Enum
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Types of anomalies that can be detected"""
    TEMPORAL = "temporal"
    BEHAVIORAL = "behavioral"
    NETWORK = "network"
    SYSTEM = "system"
    USER = "user"
    DATA_ACCESS = "data_access"
    PROCESS = "process"
    AUTHENTICATION = "authentication"

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    detection_id: str
    anomaly_type: AnomalyType
    severity: str
    confidence_score: float
    anomaly_score: float
    description: str
    affected_entities: List[str]
    indicators: List[str]
    baseline_deviation: float
    timestamp: datetime
    context: Dict[str, Any]
    recommended_actions: List[str]
    false_positive_probability: float

class AnomalyDetectionEngine:
    """Advanced ML-based anomaly detection engine"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.models = {}
        self.scalers = {}
        self.baselines = {}
        self.detection_history = deque(maxlen=10000)
        self.entity_profiles = defaultdict(dict)
        self.training_data = defaultdict(list)
        self.min_samples_for_training = 100
        self.anomaly_thresholds = {
            AnomalyType.TEMPORAL: 0.15,
            AnomalyType.BEHAVIORAL: 0.2,
            AnomalyType.NETWORK: 0.25,
            AnomalyType.SYSTEM: 0.3,
            AnomalyType.USER: 0.2,
            AnomalyType.DATA_ACCESS: 0.25,
            AnomalyType.PROCESS: 0.3,
            AnomalyType.AUTHENTICATION: 0.15
        }
        
    async def detect_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """
        Perform comprehensive anomaly detection on events
        """
        try:
            logger.info(f"🔍 Starting anomaly detection on {len(events)} events")
            
            all_detections = []
            
            # 1. Temporal Anomaly Detection
            temporal_detections = await self._detect_temporal_anomalies(events)
            all_detections.extend(temporal_detections)
            
            # 2. Behavioral Anomaly Detection
            behavioral_detections = await self._detect_behavioral_anomalies(events)
            all_detections.extend(behavioral_detections)
            
            # 3. Network Anomaly Detection
            network_detections = await self._detect_network_anomalies(events)
            all_detections.extend(network_detections)
            
            # 4. System Anomaly Detection
            system_detections = await self._detect_system_anomalies(events)
            all_detections.extend(system_detections)
            
            # 5. User Anomaly Detection
            user_detections = await self._detect_user_anomalies(events)
            all_detections.extend(user_detections)
            
            # 6. Data Access Anomaly Detection
            data_detections = await self._detect_data_access_anomalies(events)
            all_detections.extend(data_detections)
            
            # 7. Process Anomaly Detection
            process_detections = await self._detect_process_anomalies(events)
            all_detections.extend(process_detections)
            
            # 8. Authentication Anomaly Detection
            auth_detections = await self._detect_authentication_anomalies(events)
            all_detections.extend(auth_detections)
            
            # Filter and rank detections
            filtered_detections = self._filter_detections(all_detections)
            
            # Update baselines and models
            await self._update_baselines(events)
            
            logger.info(f"✅ Detected {len(filtered_detections)} anomalies")
            return filtered_detections
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {e}")
            return []
    
    async def _detect_temporal_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect temporal pattern anomalies"""
        detections = []
        
        # Group events by hour and day
        temporal_patterns = defaultdict(list)
        for event in events:
            timestamp = self._parse_timestamp(event.get('timestamp'))
            hour_key = timestamp.hour
            day_key = timestamp.weekday()
            temporal_patterns[f"{day_key}_{hour_key}"].append(event)
        
        # Detect unusual time patterns
        for time_key, time_events in temporal_patterns.items():
            if len(time_events) > 0:
                anomaly_score = self._calculate_temporal_anomaly_score(time_events)
                
                if anomaly_score > self.anomaly_thresholds[AnomalyType.TEMPORAL]:
                    detection = AnomalyDetection(
                        detection_id=f"temporal_{time_key}_{int(datetime.now().timestamp())}",
                        anomaly_type=AnomalyType.TEMPORAL,
                        severity=self._determine_severity(anomaly_score),
                        confidence_score=0.8,
                        anomaly_score=anomaly_score,
                        description=f"Unusual activity detected at {time_key}: {len(time_events)} events",
                        affected_entities=[event.get('source_ip', 'unknown') for event in time_events],
                        indicators=['unusual_timing', 'pattern_deviation'],
                        baseline_deviation=anomaly_score,
                        timestamp=datetime.now(),
                        context={'time_pattern': time_key, 'event_count': len(time_events)},
                        recommended_actions=['monitor_time_pattern', 'investigate_source'],
                        false_positive_probability=0.2
                    )
                    detections.append(detection)
        
        return detections
    
    async def _detect_behavioral_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect behavioral anomalies"""
        detections = []
        
        # Group events by entity (user, IP, etc.)
        entity_events = defaultdict(list)
        for event in events:
            entity = event.get('user') or event.get('source_ip') or 'unknown'
            entity_events[entity].append(event)
        
        # Analyze each entity's behavior
        for entity, entity_event_list in entity_events.items():
            if len(entity_event_list) >= 5:  # Minimum events for analysis
                anomaly_score = await self._calculate_behavioral_anomaly_score(entity, entity_event_list)
                
                if anomaly_score > self.anomaly_thresholds[AnomalyType.BEHAVIORAL]:
                    detection = AnomalyDetection(
                        detection_id=f"behavioral_{entity}_{int(datetime.now().timestamp())}",
                        anomaly_type=AnomalyType.BEHAVIORAL,
                        severity=self._determine_severity(anomaly_score),
                        confidence_score=0.85,
                        anomaly_score=anomaly_score,
                        description=f"Behavioral anomaly detected for {entity}: deviation score {anomaly_score:.2f}",
                        affected_entities=[entity],
                        indicators=['behavioral_deviation', 'pattern_anomaly'],
                        baseline_deviation=anomaly_score,
                        timestamp=datetime.now(),
                        context={'entity': entity, 'event_count': len(entity_event_list)},
                        recommended_actions=['investigate_entity_behavior', 'enhance_monitoring'],
                        false_positive_probability=0.15
                    )
                    detections.append(detection)
        
        return detections
    
    async def _detect_network_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect network traffic anomalies"""
        detections = []
        
        # Extract network events
        network_events = [e for e in events if e.get('source_ip') and e.get('destination_ip')]
        
        if len(network_events) < 10:
            return detections
        
        # Analyze network patterns
        network_features = []
        for event in network_events:
            features = self._extract_network_features(event)
            network_features.append(features)
        
        # Use Isolation Forest for anomaly detection
        if len(network_features) >= self.min_samples_for_training:
            model_key = 'network_isolation_forest'
            
            if model_key not in self.models:
                # Train new model
                self._train_network_model(network_features)
            
            # Detect anomalies
            anomaly_scores = self.models[model_key].predict(network_features)
            
            for i, (event, score) in enumerate(zip(network_events, anomaly_scores)):
                if score < 0:  # Anomaly detected
                    anomaly_score = abs(score)
                    
                    if anomaly_score > self.anomaly_thresholds[AnomalyType.NETWORK]:
                        detection = AnomalyDetection(
                            detection_id=f"network_{i}_{int(datetime.now().timestamp())}",
                            anomaly_type=AnomalyType.NETWORK,
                            severity=self._determine_severity(anomaly_score),
                            confidence_score=0.9,
                            anomaly_score=anomaly_score,
                            description=f"Network traffic anomaly: {event.get('source_ip')} → {event.get('destination_ip')}",
                            affected_entities=[event.get('source_ip'), event.get('destination_ip')],
                            indicators=['network_anomaly', 'traffic_deviation'],
                            baseline_deviation=anomaly_score,
                            timestamp=datetime.now(),
                            context={'protocol': event.get('protocol'), 'bytes': event.get('bytes', 0)},
                            recommended_actions=['analyze_network_flow', 'check_malicious_connections'],
                            false_positive_probability=0.1
                        )
                        detections.append(detection)
        
        return detections
    
    async def _detect_system_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect system-level anomalies"""
        detections = []
        
        # Group events by system/host
        system_events = defaultdict(list)
        for event in events:
            system = event.get('hostname') or event.get('target_asset') or 'unknown'
            system_events[system].append(event)
        
        # Analyze each system
        for system, sys_events in system_events.items():
            if len(sys_events) >= 3:
                anomaly_score = self._calculate_system_anomaly_score(sys_events)
                
                if anomaly_score > self.anomaly_thresholds[AnomalyType.SYSTEM]:
                    detection = AnomalyDetection(
                        detection_id=f"system_{system}_{int(datetime.now().timestamp())}",
                        anomaly_type=AnomalyType.SYSTEM,
                        severity=self._determine_severity(anomaly_score),
                        confidence_score=0.75,
                        anomaly_score=anomaly_score,
                        description=f"System anomaly detected on {system}",
                        affected_entities=[system],
                        indicators=['system_deviation', 'resource_anomaly'],
                        baseline_deviation=anomaly_score,
                        timestamp=datetime.now(),
                        context={'system': system, 'event_types': [e.get('category') for e in sys_events]},
                        recommended_actions=['check_system_health', 'review_system_logs'],
                        false_positive_probability=0.25
                    )
                    detections.append(detection)
        
        return detections
    
    async def _detect_user_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect user behavior anomalies"""
        detections = []
        
        # Group events by user
        user_events = defaultdict(list)
        for event in events:
            user = event.get('user')
            if user:
                user_events[user].append(event)
        
        # Analyze each user's behavior
        for user, user_event_list in user_events.items():
            if len(user_event_list) >= 5:
                anomaly_score = await self._calculate_user_anomaly_score(user, user_event_list)
                
                if anomaly_score > self.anomaly_thresholds[AnomalyType.USER]:
                    detection = AnomalyDetection(
                        detection_id=f"user_{user}_{int(datetime.now().timestamp())}",
                        anomaly_type=AnomalyType.USER,
                        severity=self._determine_severity(anomaly_score),
                        confidence_score=0.8,
                        anomaly_score=anomaly_score,
                        description=f"User behavior anomaly detected for {user}",
                        affected_entities=[user],
                        indicators=['user_anomaly', 'behavior_deviation'],
                        baseline_deviation=anomaly_score,
                        timestamp=datetime.now(),
                        context={'user': user, 'activity_count': len(user_event_list)},
                        recommended_actions=['investigate_user_activity', 'review_access_patterns'],
                        false_positive_probability=0.2
                    )
                    detections.append(detection)
        
        return detections
    
    async def _detect_data_access_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect data access anomalies"""
        detections = []
        
        # Extract data access events
        data_events = [e for e in events if e.get('category') in ['data_access', 'file_access', 'database_access']]
        
        if len(data_events) < 5:
            return detections
        
        # Analyze data access patterns
        for event in data_events:
            anomaly_score = self._calculate_data_access_anomaly_score(event)
            
            if anomaly_score > self.anomaly_thresholds[AnomalyType.DATA_ACCESS]:
                detection = AnomalyDetection(
                    detection_id=f"data_access_{event.get('_id', 'unknown')}_{int(datetime.now().timestamp())}",
                    anomaly_type=AnomalyType.DATA_ACCESS,
                    severity=self._determine_severity(anomaly_score),
                    confidence_score=0.85,
                    anomaly_score=anomaly_score,
                    description=f"Data access anomaly: {event.get('description', 'Unknown data access')}",
                    affected_entities=[event.get('user', 'unknown'), event.get('source_ip', 'unknown')],
                    indicators=['data_anomaly', 'access_deviation'],
                    baseline_deviation=anomaly_score,
                    timestamp=datetime.now(),
                    context={'file_path': event.get('file_path'), 'access_type': event.get('access_type')},
                    recommended_actions=['review_data_access', 'check_data_integrity'],
                    false_positive_probability=0.15
                )
                detections.append(detection)
        
        return detections
    
    async def _detect_process_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect process execution anomalies"""
        detections = []
        
        # Extract process events
        process_events = [e for e in events if e.get('category') == 'process_execution']
        
        if len(process_events) < 3:
            return detections
        
        # Group by process name
        process_groups = defaultdict(list)
        for event in process_events:
            process = event.get('process_name', 'unknown')
            process_groups[process].append(event)
        
        # Analyze each process
        for process, proc_events in process_groups.items():
            anomaly_score = self._calculate_process_anomaly_score(proc_events)
            
            if anomaly_score > self.anomaly_thresholds[AnomalyType.PROCESS]:
                detection = AnomalyDetection(
                    detection_id=f"process_{process}_{int(datetime.now().timestamp())}",
                    anomaly_type=AnomalyType.PROCESS,
                    severity=self._determine_severity(anomaly_score),
                    confidence_score=0.7,
                    anomaly_score=anomaly_score,
                    description=f"Process execution anomaly: {process}",
                    affected_entities=[event.get('hostname', 'unknown') for event in proc_events],
                    indicators=['process_anomaly', 'execution_deviation'],
                    baseline_deviation=anomaly_score,
                    timestamp=datetime.now(),
                    context={'process': process, 'execution_count': len(proc_events)},
                    recommended_actions=['analyze_process', 'check_malware_indicators'],
                    false_positive_probability=0.3
                )
                detections.append(detection)
        
        return detections
    
    async def _detect_authentication_anomalies(self, events: List[Dict[str, Any]]) -> List[AnomalyDetection]:
        """Detect authentication anomalies"""
        detections = []
        
        # Extract authentication events
        auth_events = [e for e in events if e.get('category') in ['authentication', 'login', 'logout']]
        
        if len(auth_events) < 5:
            return detections
        
        # Group by user
        auth_by_user = defaultdict(list)
        for event in auth_events:
            user = event.get('user')
            if user:
                auth_by_user[user].append(event)
        
        # Analyze authentication patterns
        for user, user_auth_events in auth_by_user.items():
            anomaly_score = self._calculate_authentication_anomaly_score(user_auth_events)
            
            if anomaly_score > self.anomaly_thresholds[AnomalyType.AUTHENTICATION]:
                detection = AnomalyDetection(
                    detection_id=f"auth_{user}_{int(datetime.now().timestamp())}",
                    anomaly_type=AnomalyType.AUTHENTICATION,
                    severity=self._determine_severity(anomaly_score),
                    confidence_score=0.9,
                    anomaly_score=anomaly_score,
                    description=f"Authentication anomaly detected for {user}",
                    affected_entities=[user],
                    indicators=['auth_anomaly', 'login_deviation'],
                    baseline_deviation=anomaly_score,
                    timestamp=datetime.now(),
                    context={'user': user, 'auth_events': len(user_auth_events)},
                    recommended_actions=['review_auth_logs', 'check_account_compromise'],
                    false_positive_probability=0.1
                )
                detections.append(detection)
        
        return detections
    
    def _calculate_temporal_anomaly_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate temporal anomaly score"""
        if len(events) == 0:
            return 0.0
        
        # Get historical baseline for this time period
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        time_key = f"{current_day}_{current_hour}"
        
        baseline_count = self.baselines.get(f"temporal_{time_key}", {}).get('avg_count', 5)
        current_count = len(events)
        
        # Calculate deviation
        if baseline_count == 0:
            return 0.0
        
        deviation = abs(current_count - baseline_count) / baseline_count
        
        # Cap at 1.0
        return min(deviation, 1.0)
    
    async def _calculate_behavioral_anomaly_score(self, entity: str, events: List[Dict[str, Any]]) -> float:
        """Calculate behavioral anomaly score for entity"""
        # Extract behavioral features
        features = []
        for event in events:
            feature_vector = [
                self._get_hour_of_day(event.get('timestamp')),
                self._get_day_of_week(event.get('timestamp')),
                len(event.get('description', '')),
                event.get('severity', 'medium') == 'high',
                event.get('category', 'unknown') == 'malware'
            ]
            features.append(feature_vector)
        
        if len(features) < 5:
            return 0.0
        
        # Use Isolation Forest for anomaly detection
        model_key = f"behavioral_{entity}"
        
        if model_key not in self.models:
            # Train model if enough data
            if len(self.training_data[entity]) >= self.min_samples_for_training:
                self._train_behavioral_model(entity, self.training_data[entity])
            else:
                # Store for training
                self.training_data[entity].extend(features)
                return 0.0
        
        # Detect anomalies
        try:
            anomaly_scores = self.models[model_key].predict(features)
            anomaly_count = sum(1 for score in anomaly_scores if score < 0)
            return anomaly_count / len(features)
        except:
            return 0.0
    
    def _extract_network_features(self, event: Dict[str, Any]) -> List[float]:
        """Extract network features for ML"""
        features = [
            self._ip_to_numeric(event.get('source_ip', '0.0.0.0')),
            self._ip_to_numeric(event.get('destination_ip', '0.0.0.0')),
            self._protocol_to_numeric(event.get('protocol', 'unknown')),
            float(event.get('bytes', 0)),
            float(event.get('packets', 0)),
            self._get_hour_of_day(event.get('timestamp')),
            self._get_day_of_week(event.get('timestamp'))
        ]
        return features
    
    def _train_network_model(self, features: List[List[float]]):
        """Train network anomaly detection model"""
        try:
            # Scale features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
            
            # Train Isolation Forest
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(scaled_features)
            
            # Store model and scaler
            self.models['network_isolation_forest'] = model
            self.scalers['network_scaler'] = scaler
            
            logger.info("✅ Network anomaly detection model trained")
        except Exception as e:
            logger.error(f"❌ Failed to train network model: {e}")
    
    def _train_behavioral_model(self, entity: str, features: List[List[float]]):
        """Train behavioral anomaly detection model"""
        try:
            # Scale features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(features)
            
            # Train Isolation Forest
            model = IsolationForest(contamination=0.1, random_state=42)
            model.fit(scaled_features)
            
            # Store model and scaler
            model_key = f"behavioral_{entity}"
            self.models[model_key] = model
            self.scalers[f"{model_key}_scaler"] = scaler
            
            logger.info(f"✅ Behavioral model trained for {entity}")
        except Exception as e:
            logger.error(f"❌ Failed to train behavioral model for {entity}: {e}")
    
    def _calculate_system_anomaly_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate system anomaly score"""
        # Simple heuristic based on event types and severity
        high_severity_count = sum(1 for e in events if e.get('severity') == 'high')
        total_events = len(events)
        
        if total_events == 0:
            return 0.0
        
        severity_ratio = high_severity_count / total_events
        
        # Check for unusual event types
        unusual_categories = ['malware', 'privilege_escalation', 'data_exfiltration']
        unusual_count = sum(1 for e in events if e.get('category') in unusual_categories)
        unusual_ratio = unusual_count / total_events
        
        return (severity_ratio + unusual_ratio) / 2
    
    async def _calculate_user_anomaly_score(self, user: str, events: List[Dict[str, Any]]) -> float:
        """Calculate user anomaly score"""
        # Get user baseline
        user_baseline = self.entity_profiles.get(user, {})
        
        # Calculate current metrics
        current_metrics = {
            'avg_hour': np.mean([self._get_hour_of_day(e.get('timestamp')) for e in events]),
            'unique_ips': len(set(e.get('source_ip') for e in events)),
            'high_severity_ratio': sum(1 for e in events if e.get('severity') == 'high') / len(events),
            'event_types': len(set(e.get('category') for e in events))
        }
        
        # Calculate deviation from baseline
        if not user_baseline:
            # First time seeing this user, establish baseline
            self.entity_profiles[user] = current_metrics
            return 0.0
        
        deviations = []
        for key, current_value in current_metrics.items():
            baseline_value = user_baseline.get(key, 0)
            if baseline_value > 0:
                deviation = abs(current_value - baseline_value) / baseline_value
                deviations.append(deviation)
        
        return np.mean(deviations) if deviations else 0.0
    
    def _calculate_data_access_anomaly_score(self, event: Dict[str, Any]) -> float:
        """Calculate data access anomaly score"""
        # Check for unusual access patterns
        file_path = event.get('file_path', '')
        access_type = event.get('access_type', '')
        user = event.get('user', '')
        
        anomaly_score = 0.0
        
        # Unusual file extensions
        sensitive_extensions = ['.conf', '.key', '.pem', '.db', '.sql']
        if any(file_path.endswith(ext) for ext in sensitive_extensions):
            anomaly_score += 0.3
        
        # Unusual access types
        if access_type in ['delete', 'modify', 'execute']:
            anomaly_score += 0.2
        
        # Check time of access
        hour = self._get_hour_of_day(event.get('timestamp'))
        if hour >= 22 or hour <= 6:  # Unusual hours
            anomaly_score += 0.2
        
        return min(anomaly_score, 1.0)
    
    def _calculate_process_anomaly_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate process anomaly score"""
        # Check for suspicious process characteristics
        anomaly_indicators = 0
        
        for event in events:
            process_name = event.get('process_name', '').lower()
            command_line = event.get('command_line', '').lower()
            
            # Suspicious process names
            suspicious_processes = ['powershell', 'cmd', 'wmic', 'net', 'reg']
            if any(proc in process_name for proc in suspicious_processes):
                anomaly_indicators += 1
            
            # Suspicious command line arguments
            suspicious_args = ['-enc', '-nop', 'bypass', 'hidden', 'base64']
            if any(arg in command_line for arg in suspicious_args):
                anomaly_indicators += 1
        
        return anomaly_indicators / len(events) if events else 0.0
    
    def _calculate_authentication_anomaly_score(self, events: List[Dict[str, Any]]) -> float:
        """Calculate authentication anomaly score"""
        # Check for failed logins, unusual locations, etc.
        failed_logins = sum(1 for e in events if e.get('status') == 'failed')
        total_logins = len(events)
        
        if total_logins == 0:
            return 0.0
        
        failed_ratio = failed_logins / total_logins
        
        # Check for unusual login times
        unusual_hours = sum(1 for e in events if self._get_hour_of_day(e.get('timestamp')) >= 22)
        unusual_ratio = unusual_hours / total_logins
        
        return (failed_ratio + unusual_ratio) / 2
    
    def _filter_detections(self, detections: List[AnomalyDetection]) -> List[AnomalyDetection]:
        """Filter and rank anomaly detections"""
        # Sort by confidence and severity
        filtered = []
        
        for detection in detections:
            # Filter out low confidence detections
            if detection.confidence_score < 0.6:
                continue
            
            # Filter out high false positive probability
            if detection.false_positive_probability > 0.4:
                continue
            
            filtered.append(detection)
        
        # Sort by anomaly score (descending)
        filtered.sort(key=lambda x: x.anomaly_score, reverse=True)
        
        # Return top 50 detections
        return filtered[:50]
    
    async def _update_baselines(self, events: List[Dict[str, Any]]):
        """Update baselines with new event data"""
        # Update temporal baselines
        for event in events:
            timestamp = self._parse_timestamp(event.get('timestamp'))
            hour_key = timestamp.hour
            day_key = timestamp.weekday()
            time_key = f"{day_key}_{hour_key}"
            
            if f"temporal_{time_key}" not in self.baselines:
                self.baselines[f"temporal_{time_key}"] = {'total_count': 0, 'avg_count': 0}
            
            self.baselines[f"temporal_{time_key}"]['total_count'] += 1
            
            # Update average
            total = self.baselines[f"temporal_{time_key}"]['total_count']
            self.baselines[f"temporal_{time_key}"]['avg_count'] = total / max(1, len(self.baselines))
    
    def _determine_severity(self, anomaly_score: float) -> str:
        """Determine severity from anomaly score"""
        if anomaly_score >= 0.8:
            return 'critical'
        elif anomaly_score >= 0.6:
            return 'high'
        elif anomaly_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
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
    
    def _get_hour_of_day(self, timestamp: Any) -> int:
        """Get hour of day from timestamp"""
        dt = self._parse_timestamp(timestamp)
        return dt.hour
    
    def _get_day_of_week(self, timestamp: Any) -> int:
        """Get day of week from timestamp"""
        dt = self._parse_timestamp(timestamp)
        return dt.weekday()
    
    def _ip_to_numeric(self, ip: str) -> float:
        """Convert IP address to numeric value"""
        try:
            parts = ip.split('.')
            if len(parts) == 4:
                return sum(int(part) * (256 ** (3 - i)) for i, part in enumerate(parts))
        except:
            pass
        return 0.0
    
    def _protocol_to_numeric(self, protocol: str) -> float:
        """Convert protocol to numeric value"""
        protocol_mapping = {
            'tcp': 1.0, 'udp': 2.0, 'icmp': 3.0, 'http': 4.0, 'https': 5.0,
            'ftp': 6.0, 'ssh': 7.0, 'smb': 8.0, 'rdp': 9.0
        }
        return protocol_mapping.get(protocol.lower(), 0.0)
    
    async def get_anomaly_summary(self, detections: List[AnomalyDetection]) -> Dict[str, Any]:
        """Generate anomaly detection summary"""
        if not detections:
            return {
                'total_anomalies': 0,
                'anomaly_types': {},
                'severity_distribution': {},
                'high_confidence_anomalies': 0
            }
        
        summary = {
            'total_anomalies': len(detections),
            'anomaly_types': {},
            'severity_distribution': {},
            'average_confidence': sum(d.confidence_score for d in detections) / len(detections),
            'average_anomaly_score': sum(d.anomaly_score for d in detections) / len(detections),
            'high_confidence_anomalies': len([d for d in detections if d.confidence_score > 0.8]),
            'critical_anomalies': len([d for d in detections if d.severity == 'critical'])
        }
        
        # Calculate distributions
        for detection in detections:
            # Anomaly types
            anomaly_type = detection.anomaly_type.value
            summary['anomaly_types'][anomaly_type] = summary['anomaly_types'].get(anomaly_type, 0) + 1
            
            # Severity distribution
            severity = detection.severity
            summary['severity_distribution'][severity] = summary['severity_distribution'].get(severity, 0) + 1
        
        return summary

# Global anomaly detection engine
anomaly_detection_engine = AnomalyDetectionEngine()
