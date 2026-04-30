"""
Advanced User Behavior Analytics (UBA) Engine
Detects anomalous user behavior patterns and potential insider threats
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict, Counter
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import json

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BehaviorType(Enum):
    LOGIN = "login"
    FILE_ACCESS = "file_access"
    DATA_TRANSFER = "data_transfer"
    APPLICATION_USAGE = "application_usage"
    NETWORK_ACCESS = "network_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    EMAIL_ACTIVITY = "email_activity"
    API_ACCESS = "api_access"

@dataclass
class UserBehavior:
    """User behavior data point"""
    user_id: str
    timestamp: datetime
    behavior_type: BehaviorType
    action: str
    resource: str
    source_ip: str
    device: str
    location: str
    success: bool
    risk_score: float
    metadata: Dict[str, Any]

@dataclass
class BehaviorPattern:
    """Learned behavior pattern for a user"""
    user_id: str
    behavior_type: BehaviorType
    normal_hours: List[int]
    normal_days: List[int]
    typical_locations: List[str]
    typical_devices: List[str]
    typical_actions: List[str]
    frequency_pattern: Dict[str, float]
    last_updated: datetime

@dataclass
class AnomalyAlert:
    """Behavior anomaly alert"""
    id: str
    user_id: str
    timestamp: datetime
    behavior_type: BehaviorType
    anomaly_type: str
    risk_level: RiskLevel
    risk_score: float
    description: str
    details: Dict[str, Any]
    baseline_pattern: Dict[str, Any]
    current_behavior: Dict[str, Any]

class UBAEngine:
    """Advanced User Behavior Analytics Engine"""
    
    def __init__(self):
        self.behavior_patterns = {}
        self.anomaly_alerts = []
        self.user_profiles = {}
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8,
            'critical': 0.9
        }
        self.models = {
            'isolation_forest': IsolationForest(
                contamination=0.1,
                random_state=42,
                n_estimators=100
            ),
            'dbscan': DBSCAN(
                eps=0.5,
                min_samples=5,
                metric='euclidean'
            )
        }
        self.scaler = StandardScaler()
        self.is_trained = False
    
    async def process_behavior_event(self, event: Dict[str, Any]) -> Optional[AnomalyAlert]:
        """Process a single behavior event and detect anomalies"""
        try:
            # Convert to UserBehavior object
            behavior = self._parse_behavior_event(event)
            
            # Get or create user pattern
            pattern = await self._get_or_create_pattern(behavior.user_id, behavior.behavior_type)
            
            # Detect anomalies
            anomaly = await self._detect_anomaly(behavior, pattern)
            
            # Update pattern with new behavior
            await self._update_pattern(pattern, behavior)
            
            if anomaly:
                self.anomaly_alerts.append(anomaly)
                logger.warning(f"Behavior anomaly detected for user {behavior.user_id}: {anomaly.description}")
                return anomaly
            
            return None
        except Exception as e:
            logger.error(f"Error processing behavior event: {e}")
            return None
    
    def _parse_behavior_event(self, event: Dict[str, Any]) -> UserBehavior:
        """Parse raw event into UserBehavior object"""
        return UserBehavior(
            user_id=event.get('user_id', 'unknown'),
            timestamp=datetime.fromisoformat(event.get('timestamp', datetime.now().isoformat())),
            behavior_type=BehaviorType(event.get('behavior_type', 'login')),
            action=event.get('action', 'unknown'),
            resource=event.get('resource', 'unknown'),
            source_ip=event.get('source_ip', 'unknown'),
            device=event.get('device', 'unknown'),
            location=event.get('location', 'unknown'),
            success=event.get('success', True),
            risk_score=0.0,
            metadata=event.get('metadata', {})
        )
    
    async def _get_or_create_pattern(self, user_id: str, behavior_type: BehaviorType) -> BehaviorPattern:
        """Get existing pattern or create new one"""
        pattern_key = f"{user_id}_{behavior_type.value}"
        
        if pattern_key not in self.behavior_patterns:
            pattern = BehaviorPattern(
                user_id=user_id,
                behavior_type=behavior_type,
                normal_hours=[],
                normal_days=[],
                typical_locations=[],
                typical_devices=[],
                typical_actions=[],
                frequency_pattern={},
                last_updated=datetime.now()
            )
            self.behavior_patterns[pattern_key] = pattern
        else:
            pattern = self.behavior_patterns[pattern_key]
        
        return pattern
    
    async def _detect_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect anomalies in user behavior"""
        anomalies = []
        
        # Time-based anomaly detection
        time_anomaly = self._detect_time_anomaly(behavior, pattern)
        if time_anomaly:
            anomalies.append(time_anomaly)
        
        # Location-based anomaly detection
        location_anomaly = self._detect_location_anomaly(behavior, pattern)
        if location_anomaly:
            anomalies.append(location_anomaly)
        
        # Device-based anomaly detection
        device_anomaly = self._detect_device_anomaly(behavior, pattern)
        if device_anomaly:
            anomalies.append(device_anomaly)
        
        # Action-based anomaly detection
        action_anomaly = self._detect_action_anomaly(behavior, pattern)
        if action_anomaly:
            anomalies.append(action_anomaly)
        
        # Frequency-based anomaly detection
        frequency_anomaly = self._detect_frequency_anomaly(behavior, pattern)
        if frequency_anomaly:
            anomalies.append(frequency_anomaly)
        
        # Return highest risk anomaly
        if anomalies:
            return max(anomalies, key=lambda x: x.risk_score)
        
        return None
    
    def _detect_time_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect time-based anomalies"""
        current_hour = behavior.timestamp.hour
        current_day = behavior.timestamp.weekday()
        
        # Check if this is an unusual time
        if pattern.normal_hours:
            hour_deviation = abs(current_hour - np.mean(pattern.normal_hours))
            hour_std = np.std(pattern.normal_hours) if len(pattern.normal_hours) > 1 else 1
            
            if hour_deviation > 2 * hour_std:
                risk_score = min(0.8, hour_deviation / (3 * hour_std))
                return AnomalyAlert(
                    id=f"time_{behavior.user_id}_{datetime.now().timestamp()}",
                    user_id=behavior.user_id,
                    timestamp=behavior.timestamp,
                    behavior_type=behavior.behavior_type,
                    anomaly_type="unusual_time",
                    risk_level=self._get_risk_level(risk_score),
                    risk_score=risk_score,
                    description=f"User activity detected at unusual time: {current_hour}:00",
                    details={
                        "current_hour": current_hour,
                        "normal_hours": pattern.normal_hours,
                        "hour_deviation": hour_deviation
                    },
                    baseline_pattern={"normal_hours": pattern.normal_hours},
                    current_behavior={"hour": current_hour, "day": current_day}
                )
        
        return None
    
    def _detect_location_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect location-based anomalies"""
        if pattern.typical_locations and behavior.location not in pattern.typical_locations:
            # Check if it's a completely new location
            location_counts = Counter(pattern.typical_locations)
            total_locations = sum(location_counts.values())
            
            # Higher risk if it's a completely new location
            risk_score = 0.7 if behavior.location not in location_counts else 0.4
            
            return AnomalyAlert(
                id=f"location_{behavior.user_id}_{datetime.now().timestamp()}",
                user_id=behavior.user_id,
                timestamp=behavior.timestamp,
                behavior_type=behavior.behavior_type,
                anomaly_type="unusual_location",
                risk_level=self._get_risk_level(risk_score),
                risk_score=risk_score,
                description=f"User activity detected from unusual location: {behavior.location}",
                details={
                    "current_location": behavior.location,
                    "typical_locations": pattern.typical_locations,
                    "source_ip": behavior.source_ip
                },
                baseline_pattern={"typical_locations": pattern.typical_locations},
                current_behavior={"location": behavior.location, "source_ip": behavior.source_ip}
            )
        
        return None
    
    def _detect_device_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect device-based anomalies"""
        if pattern.typical_devices and behavior.device not in pattern.typical_devices:
            device_counts = Counter(pattern.typical_devices)
            total_devices = sum(device_counts.values())
            
            # Higher risk if it's a completely new device
            risk_score = 0.6 if behavior.device not in device_counts else 0.3
            
            return AnomalyAlert(
                id=f"device_{behavior.user_id}_{datetime.now().timestamp()}",
                user_id=behavior.user_id,
                timestamp=behavior.timestamp,
                behavior_type=behavior.behavior_type,
                anomaly_type="unusual_device",
                risk_level=self._get_risk_level(risk_score),
                risk_score=risk_score,
                description=f"User activity detected from unusual device: {behavior.device}",
                details={
                    "current_device": behavior.device,
                    "typical_devices": pattern.typical_devices
                },
                baseline_pattern={"typical_devices": pattern.typical_devices},
                current_behavior={"device": behavior.device}
            )
        
        return None
    
    def _detect_action_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect action-based anomalies"""
        if pattern.typical_actions and behavior.action not in pattern.typical_actions:
            action_counts = Counter(pattern.typical_actions)
            total_actions = sum(action_counts.values())
            
            # Higher risk for privileged or sensitive actions
            sensitive_actions = ['delete', 'download', 'export', 'admin', 'sudo', 'privilege']
            is_sensitive = any(keyword in behavior.action.lower() for keyword in sensitive_actions)
            
            base_risk = 0.5
            if is_sensitive:
                base_risk = 0.8
            
            risk_score = base_risk if behavior.action not in action_counts else base_risk * 0.6
            
            return AnomalyAlert(
                id=f"action_{behavior.user_id}_{datetime.now().timestamp()}",
                user_id=behavior.user_id,
                timestamp=behavior.timestamp,
                behavior_type=behavior.behavior_type,
                anomaly_type="unusual_action",
                risk_level=self._get_risk_level(risk_score),
                risk_score=risk_score,
                description=f"User performed unusual action: {behavior.action}",
                details={
                    "current_action": behavior.action,
                    "typical_actions": pattern.typical_actions,
                    "resource": behavior.resource,
                    "is_sensitive": is_sensitive
                },
                baseline_pattern={"typical_actions": pattern.typical_actions},
                current_behavior={"action": behavior.action, "resource": behavior.resource}
            )
        
        return None
    
    def _detect_frequency_anomaly(self, behavior: UserBehavior, pattern: BehaviorPattern) -> Optional[AnomalyAlert]:
        """Detect frequency-based anomalies"""
        current_date = behavior.timestamp.date()
        action_key = f"{behavior.behavior_type.value}_{behavior.action}"
        
        # Check if user is performing actions at unusual frequency
        if pattern.frequency_pattern:
            expected_frequency = pattern.frequency_pattern.get(action_key, 0)
            
            # For simplicity, we'll check if this is the first occurrence of this action today
            # In a real implementation, you'd track daily frequencies
            if expected_frequency > 0:
                # Simulate frequency check
                recent_actions = [a for a in self.anomaly_alerts 
                                if a.user_id == behavior.user_id 
                                and a.behavior_type == behavior.behavior_type
                                and (datetime.now() - a.timestamp).total_seconds() < 3600]  # Last hour
                
                if len(recent_actions) > expected_frequency * 2:  # More than 2x normal frequency
                    risk_score = min(0.9, len(recent_actions) / (expected_frequency * 3))
                    
                    return AnomalyAlert(
                        id=f"frequency_{behavior.user_id}_{datetime.now().timestamp()}",
                        user_id=behavior.user_id,
                        timestamp=behavior.timestamp,
                        behavior_type=behavior.behavior_type,
                        anomaly_type="unusual_frequency",
                        risk_level=self._get_risk_level(risk_score),
                        risk_score=risk_score,
                        description=f"User performing actions at unusual frequency: {len(recent_actions)} actions in last hour",
                        details={
                            "current_frequency": len(recent_actions),
                            "expected_frequency": expected_frequency,
                            "action": behavior.action
                        },
                        baseline_pattern={"expected_frequency": expected_frequency},
                        current_behavior={"frequency": len(recent_actions), "action": behavior.action}
                    )
        
        return None
    
    async def _update_pattern(self, pattern: BehaviorPattern, behavior: UserBehavior):
        """Update behavior pattern with new data"""
        # Update time patterns
        pattern.normal_hours.append(behavior.timestamp.hour)
        pattern.normal_days.append(behavior.timestamp.weekday())
        
        # Keep only last 100 entries for each pattern
        if len(pattern.normal_hours) > 100:
            pattern.normal_hours = pattern.normal_hours[-100:]
        if len(pattern.normal_days) > 100:
            pattern.normal_days = pattern.normal_days[-100:]
        
        # Update location patterns
        if behavior.location not in pattern.typical_locations:
            pattern.typical_locations.append(behavior.location)
        # Keep only top 10 most common locations
        location_counts = Counter(pattern.typical_locations)
        pattern.typical_locations = [loc for loc, _ in location_counts.most_common(10)]
        
        # Update device patterns
        if behavior.device not in pattern.typical_devices:
            pattern.typical_devices.append(behavior.device)
        # Keep only top 10 most common devices
        device_counts = Counter(pattern.typical_devices)
        pattern.typical_devices = [dev for dev, _ in device_counts.most_common(10)]
        
        # Update action patterns
        if behavior.action not in pattern.typical_actions:
            pattern.typical_actions.append(behavior.action)
        # Keep only top 20 most common actions
        action_counts = Counter(pattern.typical_actions)
        pattern.typical_actions = [act for act, _ in action_counts.most_common(20)]
        
        # Update frequency patterns
        action_key = f"{behavior.behavior_type.value}_{behavior.action}"
        pattern.frequency_pattern[action_key] = pattern.frequency_pattern.get(action_key, 0) + 1
        
        pattern.last_updated = datetime.now()
        
        # Store updated pattern
        pattern_key = f"{pattern.user_id}_{pattern.behavior_type.value}"
        self.behavior_patterns[pattern_key] = pattern
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if risk_score >= self.risk_thresholds['critical']:
            return RiskLevel.CRITICAL
        elif risk_score >= self.risk_thresholds['high']:
            return RiskLevel.HIGH
        elif risk_score >= self.risk_thresholds['medium']:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    async def analyze_user_risk(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze overall risk for a specific user"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get recent anomalies for this user
            user_anomalies = [
                alert for alert in self.anomaly_alerts
                if alert.user_id == user_id and alert.timestamp >= cutoff_date
            ]
            
            if not user_anomalies:
                return {
                    "user_id": user_id,
                    "risk_level": RiskLevel.LOW.value,
                    "risk_score": 0.1,
                    "anomaly_count": 0,
                    "risk_factors": [],
                    "recommendations": ["Continue normal monitoring"]
                }
            
            # Calculate risk metrics
            risk_scores = [alert.risk_score for alert in user_anomalies]
            avg_risk_score = np.mean(risk_scores)
            max_risk_score = max(risk_scores)
            
            # Count anomaly types
            anomaly_types = Counter([alert.anomaly_type for alert in user_anomalies])
            behavior_types = Counter([alert.behavior_type.value for alert in user_anomalies])
            
            # Determine overall risk level
            overall_risk_level = self._get_risk_level(avg_risk_score)
            
            # Identify risk factors
            risk_factors = []
            if max_risk_score >= 0.8:
                risk_factors.append("High-risk anomalies detected")
            if len(user_anomalies) > 10:
                risk_factors.append("High frequency of anomalies")
            if 'unusual_location' in anomaly_types:
                risk_factors.append("Access from unusual locations")
            if 'unusual_action' in anomaly_types:
                risk_factors.append("Performance of unusual actions")
            if 'privilege_escalation' in behavior_types:
                risk_factors.append("Privilege escalation activities")
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(
                overall_risk_level, anomaly_types, behavior_types
            )
            
            return {
                "user_id": user_id,
                "risk_level": overall_risk_level.value,
                "risk_score": avg_risk_score,
                "max_risk_score": max_risk_score,
                "anomaly_count": len(user_anomalies),
                "anomaly_types": dict(anomaly_types),
                "behavior_types": dict(behavior_types),
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "analysis_period_days": days
            }
        except Exception as e:
            logger.error(f"Error analyzing user risk: {e}")
            return {"error": str(e)}
    
    def _generate_risk_recommendations(
        self, 
        risk_level: RiskLevel, 
        anomaly_types: Counter, 
        behavior_types: Counter
    ) -> List[str]:
        """Generate risk-based recommendations"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate investigation required",
                "Consider temporary access restriction",
                "Review recent activities thoroughly"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "Enhanced monitoring recommended",
                "Review user access permissions",
                "Consider additional authentication requirements"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Continue monitoring user activities",
                "Review recent anomaly patterns",
                "Consider security awareness reminder"
            ])
        else:
            recommendations.append("Continue normal monitoring")
        
        # Specific recommendations based on anomaly types
        if 'unusual_location' in anomaly_types:
            recommendations.append("Implement location-based access controls")
        
        if 'unusual_device' in anomaly_types:
            recommendations.append("Implement device-based access controls")
        
        if 'unusual_action' in anomaly_types:
            recommendations.append("Review and restrict sensitive actions")
        
        if 'privilege_escalation' in behavior_types:
            recommendations.append("Review privilege escalation policies")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def get_organization_risk_overview(self) -> Dict[str, Any]:
        """Get organization-wide risk overview"""
        try:
            if not self.anomaly_alerts:
                return {
                    "total_users": 0,
                    "high_risk_users": 0,
                    "total_anomalies": 0,
                    "risk_distribution": {},
                    "trending_anomalies": {},
                    "recommendations": ["No user behavior data available"]
                }
            
            # Get unique users
            unique_users = set(alert.user_id for alert in self.anomaly_alerts)
            
            # Get recent anomalies (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_anomalies = [
                alert for alert in self.anomaly_alerts
                if alert.timestamp >= cutoff_date
            ]
            
            # Calculate risk distribution
            risk_distribution = Counter([alert.risk_level.value for alert in recent_anomalies])
            
            # Get trending anomaly types
            trending_anomalies = Counter([alert.anomaly_type for alert in recent_anomalies])
            
            # Identify high-risk users (users with high/medium risk anomalies)
            high_risk_users = set()
            for alert in recent_anomalies:
                if alert.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    high_risk_users.add(alert.user_id)
            
            # Generate organization recommendations
            recommendations = self._generate_org_recommendations(risk_distribution, trending_anomalies)
            
            return {
                "total_users": len(unique_users),
                "high_risk_users": len(high_risk_users),
                "total_anomalies": len(recent_anomalies),
                "risk_distribution": dict(risk_distribution),
                "trending_anomalies": dict(trending_anomalies),
                "high_risk_user_list": list(high_risk_users)[:10],  # Top 10
                "recommendations": recommendations,
                "analysis_period_days": 7
            }
        except Exception as e:
            logger.error(f"Error getting organization risk overview: {e}")
            return {"error": str(e)}
    
    def _generate_org_recommendations(
        self, 
        risk_distribution: Counter, 
        trending_anomalies: Counter
    ) -> List[str]:
        """Generate organization-level recommendations"""
        recommendations = []
        
        total_anomalies = sum(risk_distribution.values())
        
        if total_anomalies > 100:
            recommendations.append("High volume of anomalies - consider reviewing security policies")
        
        if risk_distribution.get('critical', 0) > 5:
            recommendations.append("Multiple critical anomalies - immediate investigation required")
        
        if risk_distribution.get('high', 0) > 20:
            recommendations.append("Elevated number of high-risk anomalies - enhance monitoring")
        
        # Specific recommendations based on trending anomalies
        if 'unusual_location' in trending_anomalies and trending_anomalies['unusual_location'] > 10:
            recommendations.append("Implement stronger location-based access controls")
        
        if 'unusual_device' in trending_anomalies and trending_anomalies['unusual_device'] > 10:
            recommendations.append("Enhance device management and monitoring")
        
        if 'unusual_action' in trending_anomalies and trending_anomalies['unusual_action'] > 15:
            recommendations.append("Review and restrict sensitive user actions")
        
        if not recommendations:
            recommendations.append("Continue current monitoring practices")
        
        return recommendations
    
    def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get learned patterns for a specific user"""
        try:
            user_patterns = {}
            
            for pattern_key, pattern in self.behavior_patterns.items():
                if pattern.user_id == user_id:
                    user_patterns[pattern.behavior_type.value] = {
                        "normal_hours": pattern.normal_hours,
                        "normal_days": pattern.normal_days,
                        "typical_locations": pattern.typical_locations,
                        "typical_devices": pattern.typical_devices,
                        "typical_actions": pattern.typical_actions,
                        "frequency_pattern": pattern.frequency_pattern,
                        "last_updated": pattern.last_updated.isoformat()
                    }
            
            return {
                "user_id": user_id,
                "patterns": user_patterns,
                "total_patterns": len(user_patterns)
            }
        except Exception as e:
            logger.error(f"Error getting user patterns: {e}")
            return {"error": str(e)}
    
    def get_recent_anomalies(
        self, 
        hours: int = 24, 
        risk_level: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent anomalies with optional filtering"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            filtered_anomalies = [
                alert for alert in self.anomaly_alerts
                if alert.timestamp >= cutoff_time
            ]
            
            # Apply filters
            if risk_level:
                filtered_anomalies = [
                    alert for alert in filtered_anomalies
                    if alert.risk_level.value == risk_level
                ]
            
            if user_id:
                filtered_anomalies = [
                    alert for alert in filtered_anomalies
                    if alert.user_id == user_id
                ]
            
            # Sort by timestamp (newest first)
            filtered_anomalies.sort(key=lambda x: x.timestamp, reverse=True)
            
            # Convert to response format
            return [
                {
                    "id": alert.id,
                    "user_id": alert.user_id,
                    "timestamp": alert.timestamp.isoformat(),
                    "behavior_type": alert.behavior_type.value,
                    "anomaly_type": alert.anomaly_type,
                    "risk_level": alert.risk_level.value,
                    "risk_score": alert.risk_score,
                    "description": alert.description,
                    "details": alert.details,
                    "baseline_pattern": alert.baseline_pattern,
                    "current_behavior": alert.current_behavior
                }
                for alert in filtered_anomalies
            ]
        except Exception as e:
            logger.error(f"Error getting recent anomalies: {e}")
            return []

# Global UBA engine instance
uba_engine = UBAEngine()
