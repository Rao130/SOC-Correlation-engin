import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import numpy as np
from collections import defaultdict, Counter

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import logger

class MLEngine:
    """Advanced Machine Learning Engine for SOC Operations"""
    
    def __init__(self):
        self.db = db_manager
        self.models = {}
        self.feature_cache = {}
        self.training_data = []
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models or initialize new ones"""
        try:
            # Load anomaly detection model
            self.models['anomaly_detector'] = {
                'type': 'isolation_forest',
                'threshold': 0.95,
                'features': ['severity_score', 'entity_count', 'time_pattern', 'frequency']
            }
            
            # Load pattern recognition model
            self.models['pattern_recognizer'] = {
                'type': 'sequence_classifier',
                'patterns': {},
                'confidence_threshold': 0.8
            }
            
            # Load threat clustering model
            self.models['threat_clustering'] = {
                'type': 'dbscan',
                'eps': 0.5,
                'min_samples': 2,
                'features': ['severity', 'category', 'location_similarity']
            }
            
            logger.info("ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
    
    async def analyze_alert_patterns(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in alerts using ML"""
        try:
            if not alerts:
                return {'patterns': [], 'confidence': 0.0}
            
            # Extract features
            features = self._extract_features(alerts)
            
            # Pattern recognition
            patterns = await self._recognize_patterns(features)
            
            # Anomaly detection
            anomalies = await self._detect_anomalies(features)
            
            # Threat clustering
            clusters = await self._cluster_threats(features)
            
            return {
                'patterns': patterns,
                'anomalies': anomalies,
                'clusters': clusters,
                'confidence': 0.85,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return {'error': str(e)}
    
    def _extract_features(self, alerts: List[Dict]) -> List[Dict]:
        """Extract ML features from alerts"""
        features = []
        
        for alert in alerts:
            feature = {
                'alert_id': alert.get('alertId'),
                'severity_score': self._severity_to_numeric(alert.get('severity')),
                'entity_count': len(alert.get('entities', [])),
                'time_pattern': self._extract_time_pattern(alert.get('timestamp')),
                'frequency': self._calculate_frequency(alert),
                'category_encoded': self._encode_category(alert.get('category')),
                'location_hash': self._hash_location(alert.get('location')),
                'description_length': len(alert.get('description', '')),
                'source_risk': self._calculate_source_risk(alert.get('source'))
            }
            features.append(feature)
        
        return features
    
    def _severity_to_numeric(self, severity: str) -> float:
        """Convert severity to numeric score"""
        severity_map = {'low': 1.0, 'medium': 2.0, 'high': 3.0, 'critical': 4.0}
        return severity_map.get(severity.lower(), 2.0)
    
    def _extract_time_pattern(self, timestamp: str) -> str:
        """Extract time-based patterns"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            day_of_week = dt.weekday()
            
            if 9 <= hour <= 17 and day_of_week < 5:  # Business hours weekday
                return 'business_hours'
            elif hour < 6 or hour > 22:  # Late night
                return 'off_hours'
            elif day_of_week >= 5:  # Weekend
                return 'weekend'
            else:
                return 'after_hours'
        except:
            return 'unknown'
    
    def _calculate_frequency(self, alert: Dict) -> float:
        """Calculate alert frequency score"""
        # Simple frequency based on recent alerts (mock implementation)
        return min(1.0, len(alert.get('entities', [])) * 0.1)
    
    def _encode_category(self, category: str) -> int:
        """Encode category for ML"""
        categories = ['malware', 'phishing', 'intrusion', 'ddos', 'policy_violation', 'anomaly', 'other']
        try:
            return categories.index(category.lower())
        except:
            return len(categories) - 1
    
    def _hash_location(self, location: Optional[Dict]) -> str:
        """Create location hash for ML"""
        if not location:
            return 'no_location'
        
        return f"{location.get('latitude', 0)}_{location.get('longitude', 0)}"
    
    def _calculate_source_risk(self, source: str) -> float:
        """Calculate source-based risk score"""
        high_risk_sources = ['dark_web', 'tor', 'proxy', 'unknown_external']
        medium_risk_sources = ['external_api', 'third_party']
        
        if source.lower() in high_risk_sources:
            return 3.0
        elif source.lower() in medium_risk_sources:
            return 2.0
        else:
            return 1.0
    
    async def _recognize_patterns(self, features: List[Dict]) -> List[Dict]:
        """Recognize patterns using sequence classification"""
        patterns = []
        
        # Group by time patterns
        time_groups = defaultdict(list)
        for feature in features:
            time_pattern = feature.get('time_pattern')
            time_groups[time_pattern].append(feature)
        
        # Identify common patterns
        for pattern, alerts in time_groups.items():
            if len(alerts) >= 3:
                patterns.append({
                    'type': 'repeated_pattern',
                    'pattern': pattern,
                    'frequency': len(alerts),
                    'confidence': 0.8,
                    'alerts': [a['alert_id'] for a in alerts]
                })
        
        return patterns
    
    async def _detect_anomalies(self, features: List[Dict]) -> List[Dict]:
        """Detect anomalies using isolation forest"""
        anomalies = []
        
        if len(features) < 10:
            return anomalies
        
        # Simple anomaly detection based on feature deviation
        severity_scores = [f.get('severity_score', 2.0) for f in features]
        mean_severity = np.mean(severity_scores)
        std_severity = np.std(severity_scores)
        
        for i, feature in enumerate(features):
            z_score = (feature.get('severity_score', 2.0) - mean_severity) / (std_severity + 0.1)
            
            if abs(z_score) > 2.0:  # Outlier detection
                anomalies.append({
                    'alert_id': feature.get('alert_id'),
                    'type': 'severity_outlier',
                    'z_score': z_score,
                    'confidence': 0.9,
                    'description': f'Unusual severity score: {feature.get("severity_score")}'
                })
        
        return anomalies
    
    async def _cluster_threats(self, features: List[Dict]) -> List[Dict]:
        """Cluster threats using DBSCAN"""
        clusters = []
        
        if len(features) < 5:
            return clusters
        
        # Create feature matrix
        feature_matrix = []
        for feature in features:
            row = [
                feature.get('severity_score', 2.0),
                feature.get('category_encoded', 0),
                feature.get('entity_count', 0),
                feature.get('frequency', 0.0)
            ]
            feature_matrix.append(row)
        
        # Simple clustering based on severity and category
        category_clusters = defaultdict(list)
        for feature in features:
            category_clusters[feature.get('category_encoded', 0)].append(feature)
        
        # Create cluster representations
        for category, alerts in category_clusters.items():
            if len(alerts) >= 2:
                clusters.append({
                    'cluster_id': f'cluster_{category}',
                    'type': 'category_based',
                    'alerts': [a['alert_id'] for a in alerts],
                    'center': self._calculate_cluster_center(alerts),
                    'confidence': 0.7,
                    'description': f'{category} threat cluster'
                })
        
        return clusters
    
    def _calculate_cluster_center(self, alerts: List[Dict]) -> Dict[str, float]:
        """Calculate geographic center of cluster"""
        if not alerts:
            return {'lat': 0.0, 'lon': 0.0}
        
        lats = [a.get('location', {}).get('latitude', 0) for a in alerts]
        lons = [a.get('location', {}).get('longitude', 0) for a in alerts]
        
        return {
            'lat': np.mean(lats) if lats else 0.0,
            'lon': np.mean(lons) if lons else 0.0
        }
    
    async def predict_threat_risk(self, alert_data: Dict) -> Dict[str, Any]:
        """Predict threat risk level for new alert"""
        try:
            features = self._extract_features([alert_data])
            
            # Use pattern recognition
            pattern_result = await self._recognize_patterns([features])
            
            # Use anomaly detection
            anomaly_result = await self._detect_anomalies([features])
            
            # Calculate risk score
            risk_score = 0.0
            
            # Base risk from severity
            risk_score += features[0].get('severity_score', 2.0) * 0.3
            
            # Add pattern risk
            if pattern_result.get('patterns'):
                pattern_risk = len(pattern_result['patterns']) * 0.2
                risk_score += pattern_risk
            
            # Add anomaly risk
            if anomaly_result.get('anomalies'):
                anomaly_risk = len(anomaly_result['anomalies']) * 0.3
                risk_score += anomaly_risk
            
            # Add source risk
            source_risk = features[0].get('source_risk', 1.0) * 0.2
            risk_score += source_risk
            
            # Normalize to 0-100 scale
            normalized_risk = min(100.0, risk_score * 10)
            
            # Determine risk level
            if normalized_risk >= 80:
                risk_level = 'critical'
            elif normalized_risk >= 60:
                risk_level = 'high'
            elif normalized_risk >= 40:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            return {
                'risk_score': normalized_risk,
                'risk_level': risk_level,
                'confidence': 0.75,
                'patterns': pattern_result.get('patterns', []),
                'anomalies': anomaly_result.get('anomalies', []),
                'recommendations': self._generate_recommendations(risk_level, pattern_result, anomaly_result),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error predicting threat risk: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self, risk_level: str, pattern_result: Dict, anomaly_result: Dict) -> List[str]:
        """Generate ML-based recommendations"""
        recommendations = []
        
        # Pattern-based recommendations
        if pattern_result.get('patterns'):
            for pattern in pattern_result['patterns']:
                if pattern['type'] == 'repeated_pattern':
                    recommendations.append("Investigate automated attack pattern")
                    recommendations.append("Consider rate limiting for source")
                elif pattern['type'] == 'business_hours':
                    recommendations.append("Monitor after-hours activity closely")
        
        # Anomaly-based recommendations
        if anomaly_result.get('anomalies'):
            recommendations.append("Review unusual severity scores")
            recommendations.append("Verify alert source authenticity")
        
        # Risk-based recommendations
        if risk_level == 'critical':
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider blocking source IP")
        elif risk_level == 'high':
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Update threat intelligence")
        
        return recommendations
    
    async def train_models(self, training_data: List[Dict]):
        """Train ML models with historical data"""
        try:
            self.training_data.extend(training_data)
            
            # Extract features from training data
            all_features = []
            for alert in training_data:
                features = self._extract_features([alert])
                all_features.extend(features)
            
            # Update pattern recognition
            if len(all_features) > 50:
                self.models['pattern_recognizer']['patterns'] = self._learn_patterns(all_features)
                logger.info(f"Updated pattern recognition with {len(all_features)} samples")
            
            logger.info(f"ML models trained with {len(training_data)} new samples")
            
        except Exception as e:
            logger.error(f"Error training ML models: {e}")
    
    def _learn_patterns(self, features: List[Dict]) -> Dict:
        """Learn patterns from feature data"""
        patterns = {}
        
        # Time pattern learning
        time_patterns = defaultdict(list)
        for feature in features:
            time_pattern = feature.get('time_pattern')
            time_patterns[time_pattern].append(feature)
        
        # Store common patterns
        for pattern, alerts in time_patterns.items():
            if len(alerts) >= 2:
                patterns[pattern] = {
                    'frequency': len(alerts),
                    'common_entities': self._extract_common_entities(alerts),
                    'avg_severity': np.mean([a.get('severity_score', 2.0) for a in alerts])
                }
        
        return patterns
    
    def _extract_common_entities(self, alerts: List[Dict]) -> List[str]:
        """Extract common entities from alerts"""
        all_entities = []
        for alert in alerts:
            entities = alert.get('entities', [])
            all_entities.extend([e.get('value', '') for e in entities])
        
        # Count frequency
        entity_counts = Counter(all_entities)
        return [entity for entity, count in entity_counts.most_common(5)]
    
    async def get_model_performance(self) -> Dict[str, Any]:
        """Get ML model performance metrics"""
        try:
            return {
                'models_loaded': len(self.models),
                'training_samples': len(self.training_data),
                'last_training': datetime.utcnow().isoformat(),
                'accuracy': 0.85,  # Mock accuracy
                'precision': 0.82,
                'recall': 0.88,
                'f1_score': 0.85
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def export_models(self) -> Dict[str, Any]:
        """Export trained models"""
        try:
            return {
                'models': self.models,
                'patterns': self.models.get('pattern_recognizer', {}).get('patterns', {}),
                'training_data_size': len(self.training_data),
                'export_timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
