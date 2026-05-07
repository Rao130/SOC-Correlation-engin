"""
Advanced Anomaly Detection System for SOC Correlation Engine
Implements multiple anomaly detection algorithms for security event analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Advanced anomaly detection system with multiple algorithms"""
    
    def __init__(self):
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
        self.pca = PCA(n_components=0.95)
        self.is_trained = False
        self.feature_columns = []
        
    def extract_features(self, alerts: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract numerical features from security alerts"""
        features = []
        
        for alert in alerts:
            feature_vector = {
                # Temporal features
                'hour_of_day': datetime.fromisoformat(alert.get('timestamp', datetime.now().isoformat())).hour,
                'day_of_week': datetime.fromisoformat(alert.get('timestamp', datetime.now().isoformat())).weekday(),
                
                # Severity and confidence
                'severity_numeric': self._severity_to_numeric(alert.get('severity', 'medium')),
                'confidence': alert.get('confidence', 0.5),
                
                # Entity-based features
                'entity_count': len(alert.get('entities', [])),
                'source_ip_count': len(set([e.get('ip') for e in alert.get('entities', []) if e.get('ip')])),
                
                # Category features (one-hot encoded)
                'category_access': 1 if alert.get('category') == 'access' else 0,
                'category_network': 1 if alert.get('category') == 'network' else 0,
                'category_endpoint': 1 if alert.get('category') == 'endpoint' else 0,
                'category_identity': 1 if alert.get('category') == 'identity' else 0,
                'category_audit': 1 if alert.get('category') == 'audit' else 0,
                'category_threat': 1 if alert.get('category') == 'threat' else 0,
                'category_uba': 1 if alert.get('category') == 'uba' else 0,
                
                # Geographic features
                'has_location': 1 if alert.get('location') else 0,
                'country_count': len(set([e.get('country') for e in alert.get('entities', []) if e.get('country')])),
                
                # Behavioral features
                'is_repeated_pattern': self._is_repeated_pattern(alert),
                'time_since_last_alert': self._calculate_time_since_last_alert(alert, alerts),
            }
            features.append(feature_vector)
        
        df = pd.DataFrame(features)
        self.feature_columns = df.columns.tolist()
        return df.fillna(0)
    
    def train(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train anomaly detection models"""
        try:
            features_df = self.extract_features(alerts)
            
            if len(features_df) < 10:
                logger.warning("Insufficient data for training anomaly detection")
                return {'status': 'insufficient_data', 'message': 'Need at least 10 alerts'}
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features_df)
            
            # Apply PCA for dimensionality reduction
            pca_features = self.pca.fit_transform(scaled_features)
            
            # Train models
            results = {}
            
            # Train Isolation Forest
            self.models['isolation_forest'].fit(pca_features)
            if_scores = self.models['isolation_forest'].score_samples(pca_features)
            results['isolation_forest'] = {
                'mean_score': np.mean(if_scores),
                'std_score': np.std(if_scores),
                'outlier_count': np.sum(if_scores < -0.5)
            }
            
            # Train DBSCAN
            db_labels = self.models['dbscan'].fit_predict(pca_features)
            results['dbscan'] = {
                'n_clusters': len(set(db_labels)) - (1 if -1 in db_labels else 0),
                'n_noise': list(db_labels).count(-1),
                'silhouette_score': self._calculate_silhouette_score(pca_features, db_labels)
            }
            
            self.is_trained = True
            logger.info(f"Anomaly detection models trained on {len(alerts)} alerts")
            
            return {
                'status': 'success',
                'models_trained': list(self.models.keys()),
                'feature_count': len(self.feature_columns),
                'training_results': results
            }
            
        except Exception as e:
            logger.error(f"Error training anomaly detection: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def detect_anomalies(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in new alerts"""
        if not self.is_trained:
            logger.warning("Models not trained yet")
            return []
        
        try:
            features_df = self.extract_features(alerts)
            scaled_features = self.scaler.transform(features_df)
            pca_features = self.pca.transform(scaled_features)
            
            anomalies = []
            
            # Isolation Forest anomalies
            if_scores = self.models['isolation_forest'].score_samples(pca_features)
            if_predictions = self.models['isolation_forest'].predict(pca_features)
            
            # DBSCAN anomalies
            db_labels = self.models['dbscan'].fit_predict(pca_features)
            
            for i, alert in enumerate(alerts):
                anomaly_score = {
                    'alert_id': alert.get('_id', i),
                    'timestamp': alert.get('timestamp'),
                    'severity': alert.get('severity'),
                    'category': alert.get('category'),
                    
                    # Isolation Forest results
                    'isolation_score': float(if_scores[i]),
                    'isolation_anomaly': if_predictions[i] == -1,
                    
                    # DBSCAN results
                    'dbscan_cluster': int(db_labels[i]),
                    'dbscan_anomaly': db_labels[i] == -1,
                    
                    # Combined anomaly score
                    'combined_score': self._calculate_combined_anomaly_score(
                        if_scores[i], db_labels[i]
                    ),
                    
                    # Anomaly reasons
                    'anomaly_reasons': self._identify_anomaly_reasons(
                        alert, if_scores[i], db_labels[i]
                    )
                }
                
                # Only include alerts with significant anomaly scores
                if anomaly_score['combined_score'] > 0.7:
                    anomalies.append(anomaly_score)
            
            return sorted(anomalies, key=lambda x: x['combined_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Convert severity levels to numeric values"""
        severity_map = {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        return severity_map.get(severity.lower(), 2)
    
    def _is_repeated_pattern(self, alert: Dict[str, Any]) -> int:
        """Check if alert follows a repeated pattern"""
        # Simplified pattern detection - can be enhanced
        return 1 if alert.get('confidence', 0) > 0.8 else 0
    
    def _calculate_time_since_last_alert(self, alert: Dict[str, Any], all_alerts: List[Dict]) -> float:
        """Calculate time difference from previous similar alert"""
        try:
            current_time = datetime.fromisoformat(alert.get('timestamp', datetime.now().isoformat()))
            similar_alerts = [a for a in all_alerts 
                            if a.get('category') == alert.get('category') 
                            and a.get('source') == alert.get('source')
                            and a != alert]
            
            if similar_alerts:
                last_alert_time = max([datetime.fromisoformat(a.get('timestamp', datetime.now().isoformat())) 
                                      for a in similar_alerts])
                return (current_time - last_alert_time).total_seconds() / 3600  # hours
            return 24.0  # Default to 24 hours if no similar alerts
        except:
            return 24.0
    
    def _calculate_silhouette_score(self, features: np.ndarray, labels: np.ndarray) -> float:
        """Calculate silhouette score for clustering quality"""
        try:
            from sklearn.metrics import silhouette_score
            if len(set(labels)) > 1 and -1 not in labels:
                return silhouette_score(features, labels)
        except:
            pass
        return 0.0
    
    def _calculate_combined_anomaly_score(self, isolation_score: float, dbscan_label: int) -> float:
        """Calculate combined anomaly score from multiple models"""
        # Normalize isolation score (lower = more anomalous)
        isolation_anomaly = max(0, -isolation_score)
        
        # DBSCAN anomaly (label -1 = anomaly)
        dbscan_anomaly = 1.0 if dbscan_label == -1 else 0.0
        
        # Weighted combination
        combined = (isolation_anomaly * 0.6) + (dbscan_anomaly * 0.4)
        return min(1.0, combined)
    
    def _identify_anomaly_reasons(self, alert: Dict[str, Any], isolation_score: float, dbscan_label: int) -> List[str]:
        """Identify specific reasons for anomaly"""
        reasons = []
        
        if isolation_score < -0.5:
            reasons.append("Unusual pattern detected by isolation forest")
        
        if dbscan_label == -1:
            reasons.append("Does not belong to any normal cluster")
        
        if alert.get('severity') == 'critical':
            reasons.append("Critical severity alert")
        
        if alert.get('confidence', 0) > 0.9:
            reasons.append("High confidence unusual activity")
        
        return reasons if reasons else ["General anomaly detected"]
