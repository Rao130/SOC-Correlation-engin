"""
AI-Powered Threat Scoring Engine
Machine Learning based risk assessment and threat prioritization
"""

import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json
from app.core.database import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class ThreatScore:
    """Threat score result with detailed breakdown"""
    alert_id: str
    overall_score: float
    risk_level: str
    confidence: float
    score_breakdown: Dict[str, float]
    threat_indicators: List[str]
    business_impact: str
    recommended_actions: List[str]
    prediction_confidence: float

class ThreatScoringEngine:
    """AI-powered threat scoring with machine learning"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.scaler = StandardScaler()
        self.risk_model = None
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.feature_columns = [
            'severity_weight', 'asset_criticality', 'threat_intel_match',
            'behavior_anomaly', 'historical_patterns', 'network_risk',
            'time_anomaly', 'user_risk', 'system_risk', 'external_threats'
        ]
        self.model_path = "app/models/threat_scoring_model.pkl"
        self.scaler_path = "app/models/threat_scaler.pkl"
        self.threat_intelligence = self._load_threat_intelligence()
        self.asset_criticality = self._load_asset_criticality()
        self.user_behavior_baseline = {}
        
    def _load_threat_intelligence(self) -> Dict[str, Any]:
        """Load threat intelligence data"""
        return {
            'malicious_ips': {
                '192.168.1.100': {'actor': 'apt28', 'confidence': 0.9},
                '10.0.0.50': {'actor': 'apt29', 'confidence': 0.85},
                '172.16.0.25': {'actor': 'Lazarus', 'confidence': 0.8}
            },
            'malicious_domains': {
                'malicious-site.com': {'malware': 'trickbot', 'confidence': 0.95},
                'c2-server.net': {'malware': 'emotet', 'confidence': 0.9}
            },
            'malware_families': {
                'emotet': {'severity': 'critical', 'actor': 'apt28'},
                'trickbot': {'severity': 'high', 'actor': 'apt29'},
                'ryuk': {'severity': 'critical', 'actor': 'unknown'},
                'wannacry': {'severity': 'critical', 'actor': 'Lazarus'}
            },
            'attack_patterns': {
                'brute_force': {'mitigation_difficulty': 'low', 'impact': 'medium'},
                'spear_phishing': {'mitigation_difficulty': 'medium', 'impact': 'high'},
                'zero_day': {'mitigation_difficulty': 'high', 'impact': 'critical'}
            }
        }
    
    def _load_asset_criticality(self) -> Dict[str, float]:
        """Load asset criticality scores"""
        return {
            'domain_controller': 1.0,
            'database_server': 0.9,
            'file_server': 0.8,
            'web_server': 0.7,
            'workstation': 0.4,
            'mobile_device': 0.3
        }
    
    async def calculate_threat_score(self, alert: Dict[str, Any], context: Dict[str, Any] = None) -> ThreatScore:
        """
        Calculate comprehensive threat score using ML and rule-based analysis
        """
        try:
            logger.info(f"🎯 Calculating threat score for alert {alert.get('_id', 'unknown')}")
            
            # Extract features
            features = await self._extract_features(alert, context or {})
            
            # Calculate component scores
            severity_score = self._calculate_severity_score(alert)
            asset_score = self._calculate_asset_risk_score(alert)
            threat_intel_score = self._calculate_threat_intel_score(alert)
            behavior_score = self._calculate_behavior_score(alert, context)
            network_score = self._calculate_network_risk_score(alert)
            time_score = self._calculate_time_anomaly_score(alert)
            historical_score = self._calculate_historical_pattern_score(alert)
            
            # Combine scores using ML model
            feature_vector = np.array([
                severity_score, asset_score, threat_intel_score,
                behavior_score, network_score, time_score, historical_score,
                self._calculate_system_risk(alert),
                self._calculate_user_risk(alert),
                self._calculate_external_threat_score(alert)
            ]).reshape(1, -1)
            
            # Normalize features
            try:
                normalized_features = self.scaler.transform(feature_vector)
            except:
                # Fallback if scaler not trained
                normalized_features = feature_vector
            
            # Predict risk score
            if self.risk_model:
                risk_probability = self.risk_model.predict_proba(normalized_features)[0][1]
                overall_score = risk_probability * 100
            else:
                # Fallback to weighted average
                weights = [0.2, 0.15, 0.15, 0.15, 0.1, 0.1, 0.05, 0.05, 0.03, 0.02]
                overall_score = np.dot(weights, normalized_features[0]) * 100
            
            # Determine risk level
            risk_level = self._determine_risk_level(overall_score)
            
            # Generate score breakdown
            score_breakdown = {
                'severity': severity_score * 100,
                'asset_risk': asset_score * 100,
                'threat_intel': threat_intel_score * 100,
                'behavioral': behavior_score * 100,
                'network': network_score * 100,
                'temporal': time_score * 100,
                'historical': historical_score * 100
            }
            
            # Identify threat indicators
            threat_indicators = self._identify_threat_indicators(alert, features)
            
            # Assess business impact
            business_impact = self._assess_business_impact(alert, overall_score)
            
            # Generate recommended actions
            recommended_actions = self._generate_recommendations(risk_level, threat_indicators)
            
            # Calculate prediction confidence
            prediction_confidence = self._calculate_prediction_confidence(features)
            
            return ThreatScore(
                alert_id=alert.get('_id', ''),
                overall_score=round(overall_score, 2),
                risk_level=risk_level,
                confidence=round(prediction_confidence, 2),
                score_breakdown=score_breakdown,
                threat_indicators=threat_indicators,
                business_impact=business_impact,
                recommended_actions=recommended_actions,
                prediction_confidence=round(prediction_confidence, 2)
            )
            
        except Exception as e:
            logger.error(f"❌ Threat scoring failed: {e}")
            # Return default score
            return ThreatScore(
                alert_id=alert.get('_id', ''),
                overall_score=50.0,
                risk_level="medium",
                confidence=0.5,
                score_breakdown={},
                threat_indicators=["scoring_error"],
                business_impact="medium",
                recommended_actions=["investigate_manually"],
                prediction_confidence=0.5
            )
    
    async def _extract_features(self, alert: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
        """Extract ML features from alert and context"""
        features = {}
        
        # Basic alert features
        features['severity'] = self._severity_to_numeric(alert.get('severity', 'low'))
        features['category'] = self._category_to_numeric(alert.get('category', 'unknown'))
        features['confidence'] = float(alert.get('confidence', 0)) / 100
        
        # Network features
        features['source_ip_risk'] = self._get_ip_risk_score(alert.get('source_ip'))
        features['destination_ip_risk'] = self._get_ip_risk_score(alert.get('destination_ip'))
        features['protocol_risk'] = self._get_protocol_risk(alert.get('protocol'))
        
        # Time features
        features['hour_of_day'] = self._get_time_risk_score(alert.get('timestamp'))
        features['day_of_week'] = self._get_day_risk_score(alert.get('timestamp'))
        
        # Contextual features
        features['recent_similar_alerts'] = context.get('recent_similar_count', 0)
        features['user_risk_score'] = self._get_user_risk_score(alert.get('user'))
        features['asset_criticality'] = self._get_asset_criticality_score(alert.get('target_asset'))
        
        return features
    
    def _calculate_severity_score(self, alert: Dict[str, Any]) -> float:
        """Calculate severity-based score"""
        severity_weights = {'critical': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.3, 'info': 0.1}
        severity = alert.get('severity', 'low').lower()
        return severity_weights.get(severity, 0.3)
    
    def _calculate_asset_risk_score(self, alert: Dict[str, Any]) -> float:
        """Calculate asset risk score"""
        target = alert.get('destination_ip') or alert.get('target_asset', '')
        
        # Check if target is critical asset
        for asset_type, score in self.asset_criticality.items():
            if asset_type in target.lower():
                return score
        
        # Default risk based on IP range
        if target.startswith('192.168.') or target.startswith('10.') or target.startswith('172.'):
            return 0.5  # Internal network
        
        return 0.3  # Unknown/external
    
    def _calculate_threat_intel_score(self, alert: Dict[str, Any]) -> float:
        """Calculate threat intelligence match score"""
        score = 0.0
        
        # Check source IP
        source_ip = alert.get('source_ip')
        if source_ip in self.threat_intelligence['malicious_ips']:
            score = max(score, self.threat_intelligence['malicious_ips'][source_ip]['confidence'])
        
        # Check domain
        domain = alert.get('domain')
        if domain and domain in self.threat_intelligence['malicious_domains']:
            score = max(score, self.threat_intelligence['malicious_domains'][domain]['confidence'])
        
        # Check malware family
        malware = alert.get('malware_family')
        if malware in self.threat_intelligence['malware_families']:
            score = max(score, 0.8)  # High confidence for known malware
        
        return score
    
    def _calculate_behavior_score(self, alert: Dict[str, Any], context: Dict[str, Any]) -> float:
        """Calculate behavioral anomaly score"""
        score = 0.0
        
        # Check for unusual time
        timestamp = alert.get('timestamp')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                if hour >= 22 or hour <= 6:  # Unusual hours
                    score += 0.3
            except:
                pass
        
        # Check for privilege escalation
        if 'privilege' in alert.get('description', '').lower() or 'escalation' in alert.get('description', '').lower():
            score += 0.5
        
        # Check for failed login patterns
        if alert.get('category') == 'brute_force' or 'failed' in alert.get('title', '').lower():
            score += 0.4
        
        # Check context for anomalies
        if context.get('behavioral_anomaly_detected'):
            score += 0.6
        
        return min(score, 1.0)
    
    def _calculate_network_risk_score(self, alert: Dict[str, Any]) -> float:
        """Calculate network-based risk score"""
        score = 0.0
        
        # Check for lateral movement
        source_ip = alert.get('source_ip', '')
        dest_ip = alert.get('destination_ip', '')
        
        if source_ip.startswith('192.168.') and dest_ip.startswith('192.168.'):
            score += 0.3  # Internal to internal communication
        
        # Check for high-risk protocols
        protocol = alert.get('protocol', '').lower()
        high_risk_protocols = ['smb', 'rpc', 'winrm', 'rdp']
        if protocol in high_risk_protocols:
            score += 0.4
        
        # Check for data exfiltration indicators
        if alert.get('category') == 'data_exfiltration':
            score += 0.7
        
        return min(score, 1.0)
    
    def _calculate_time_anomaly_score(self, alert: Dict[str, Any]) -> float:
        """Calculate temporal anomaly score"""
        timestamp = alert.get('timestamp')
        if not timestamp:
            return 0.0
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Weekend activity
            if dt.weekday() >= 5:  # Saturday or Sunday
                return 0.3
            
            # Late night activity
            if dt.hour >= 22 or dt.hour <= 6:
                return 0.4
            
            return 0.0
        except:
            return 0.0
    
    def _calculate_historical_pattern_score(self, alert: Dict[str, Any]) -> float:
        """Calculate historical pattern matching score"""
        # This would integrate with historical data
        # For now, return based on alert frequency
        return 0.2  # Placeholder
    
    def _calculate_system_risk(self, alert: Dict[str, Any]) -> float:
        """Calculate system-level risk score"""
        return 0.3  # Placeholder
    
    def _calculate_user_risk(self, alert: Dict[str, Any]) -> float:
        """Calculate user-based risk score"""
        user = alert.get('user', '')
        if not user:
            return 0.0
        
        # Check if user is admin/higher privilege
        if any(admin in user.lower() for admin in ['admin', 'root', 'administrator']):
            return 0.7
        
        return 0.2
    
    def _calculate_external_threat_score(self, alert: Dict[str, Any]) -> float:
        """Calculate external threat level score"""
        return 0.3  # Placeholder
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _identify_threat_indicators(self, alert: Dict[str, Any], features: Dict[str, float]) -> List[str]:
        """Identify specific threat indicators"""
        indicators = []
        
        if features.get('severity', 0) > 0.8:
            indicators.append("high_severity")
        
        if alert.get('source_ip') in self.threat_intelligence['malicious_ips']:
            indicators.append("malicious_ip")
        
        if alert.get('category') == 'malware':
            indicators.append("malware_detected")
        
        if features.get('behavioral_anomaly', 0) > 0.5:
            indicators.append("behavioral_anomaly")
        
        if features.get('asset_risk', 0) > 0.8:
            indicators.append("critical_asset_targeted")
        
        return indicators
    
    def _assess_business_impact(self, alert: Dict[str, Any], score: float) -> str:
        """Assess business impact level"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, risk_level: str, indicators: List[str]) -> List[str]:
        """Generate recommended actions based on risk level and indicators"""
        recommendations = []
        
        if risk_level == "critical":
            recommendations.extend([
                "immediate_investigation",
                "isolate_affected_systems",
                "escalate_to_security_team",
                "enable_enhanced_monitoring"
            ])
        elif risk_level == "high":
            recommendations.extend([
                "priority_investigation",
                "review_related_alerts",
                "update_threat_intelligence"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "standard_investigation",
                "monitor_for_related_activity"
            ])
        else:
            recommendations.extend([
                "log_for_review",
                "continue_monitoring"
            ])
        
        # Add indicator-specific recommendations
        if "malicious_ip" in indicators:
            recommendations.append("block_malicious_ips")
        
        if "malware_detected" in indicators:
            recommendations.append("run_antivirus_scan")
        
        if "critical_asset_targeted" in indicators:
            recommendations.append("protect_critical_assets")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_prediction_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in prediction"""
        # Based on feature completeness and model confidence
        feature_count = len([v for v in features.values() if v is not None])
        max_features = len(features)
        
        if max_features == 0:
            return 0.0
        
        completeness = feature_count / max_features
        return min(completeness * 1.2, 1.0)  # Cap at 1.0
    
    def _severity_to_numeric(self, severity: str) -> float:
        """Convert severity to numeric"""
        mapping = {'critical': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.3, 'info': 0.1}
        return mapping.get(severity.lower(), 0.3)
    
    def _category_to_numeric(self, category: str) -> float:
        """Convert category to numeric risk score"""
        category_risks = {
            'malware': 0.9, 'data_exfiltration': 0.9, 'privilege_escalation': 0.8,
            'lateral_movement': 0.8, 'c2_communication': 0.7, 'brute_force': 0.6,
            'phishing': 0.6, 'reconnaissance': 0.4, 'anomaly': 0.5
        }
        return category_risks.get(category.lower(), 0.3)
    
    def _get_ip_risk_score(self, ip: str) -> float:
        """Get IP-based risk score"""
        if not ip:
            return 0.0
        
        # Check against threat intelligence
        if ip in self.threat_intelligence['malicious_ips']:
            return self.threat_intelligence['malicious_ips'][ip]['confidence']
        
        # Check if external IP
        if not (ip.startswith('192.168.') or ip.startswith('10.') or ip.startswith('172.')):
            return 0.4  # External IP has some risk
        
        return 0.1  # Internal IP, low risk
    
    def _get_protocol_risk_score(self, protocol: str) -> float:
        """Get protocol-based risk score"""
        if not protocol:
            return 0.0
        
        high_risk_protocols = {'smb': 0.7, 'rpc': 0.6, 'rdp': 0.8, 'winrm': 0.7}
        medium_risk_protocols = {'http': 0.3, 'https': 0.2, 'ftp': 0.5}
        
        return high_risk_protocols.get(protocol.lower(), 
                                      medium_risk_protocols.get(protocol.lower(), 0.1))
    
    def _get_time_risk_score(self, timestamp: str) -> float:
        """Get time-based risk score"""
        if not timestamp:
            return 0.0
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Risk score based on hour (higher for unusual hours)
            hour_risk = {
                0: 0.4, 1: 0.4, 2: 0.4, 3: 0.4, 4: 0.4, 5: 0.4, 6: 0.3,
                7: 0.1, 8: 0.1, 9: 0.1, 10: 0.1, 11: 0.1, 12: 0.1,
                13: 0.1, 14: 0.1, 15: 0.1, 16: 0.1, 17: 0.1, 18: 0.2,
                19: 0.2, 20: 0.3, 21: 0.3, 22: 0.4, 23: 0.4
            }
            
            return hour_risk.get(dt.hour, 0.1)
        except:
            return 0.0
    
    def _get_day_risk_score(self, timestamp: str) -> float:
        """Get day-based risk score"""
        if not timestamp:
            return 0.0
        
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Higher risk on weekends
            return 0.3 if dt.weekday() >= 5 else 0.1
        except:
            return 0.0
    
    def _get_user_risk_score(self, user: str) -> float:
        """Get user-based risk score"""
        if not user:
            return 0.0
        
        # Check for admin accounts
        admin_keywords = ['admin', 'administrator', 'root', 'sa']
        if any(keyword in user.lower() for keyword in admin_keywords):
            return 0.7
        
        return 0.2
    
    def _get_asset_criticality_score(self, asset: str) -> float:
        """Get asset criticality score"""
        if not asset:
            return 0.0
        
        asset_lower = asset.lower()
        for asset_type, score in self.asset_criticality.items():
            if asset_type in asset_lower:
                return score
        
        return 0.3
    
    async def train_model(self, training_data: List[Dict[str, Any]]):
        """Train the ML threat scoring model"""
        try:
            logger.info("🤖 Training threat scoring model...")
            
            # Prepare training data
            X, y = self._prepare_training_data(training_data)
            
            if len(X) < 100:
                logger.warning("⚠️ Insufficient training data, using default model")
                return
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.risk_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            
            self.risk_model.fit(X_train, y_train)
            
            # Train scaler
            self.scaler.fit(X_train)
            
            # Save model and scaler
            joblib.dump(self.risk_model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            # Evaluate model
            train_score = self.risk_model.score(X_train, y_train)
            test_score = self.risk_model.score(X_test, y_test)
            
            logger.info(f"✅ Model trained successfully")
            logger.info(f"📊 Training accuracy: {train_score:.3f}")
            logger.info(f"📊 Test accuracy: {test_score:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
    
    def _prepare_training_data(self, data: List[Dict[str, Any]]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare training data for ML model"""
        features = []
        labels = []
        
        for item in data:
            # Extract features (simplified for demo)
            feature_vector = [
                item.get('severity_weight', 0.5),
                item.get('asset_criticality', 0.5),
                item.get('threat_intel_match', 0.0),
                item.get('behavior_anomaly', 0.0),
                item.get('historical_patterns', 0.0),
                item.get('network_risk', 0.0),
                item.get('time_anomaly', 0.0),
                item.get('user_risk', 0.0),
                item.get('system_risk', 0.0),
                item.get('external_threats', 0.0)
            ]
            
            features.append(feature_vector)
            labels.append(item.get('is_threat', 0))  # Binary label
        
        return np.array(features), np.array(labels)
    
    async def load_model(self):
        """Load pre-trained model"""
        try:
            self.risk_model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            logger.info("✅ Threat scoring model loaded successfully")
        except FileNotFoundError:
            logger.warning("⚠️ No pre-trained model found, using rule-based scoring")
            self.risk_model = None

# Global threat scoring engine
threat_scoring_engine = ThreatScoringEngine()
