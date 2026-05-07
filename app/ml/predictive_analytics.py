"""
Predictive Analytics System for SOC Correlation Engine
Implements threat prediction, trend analysis, and risk forecasting
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import logging

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """Advanced predictive analytics for security operations"""
    
    def __init__(self):
        self.models = {
            'alert_volume': RandomForestRegressor(n_estimators=100, random_state=42),
            'threat_trends': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'risk_forecast': LinearRegression(),
            'severity_prediction': RandomForestRegressor(n_estimators=50, random_state=42)
        }
        self.scalers = {}
        self.is_trained = False
        self.feature_columns = {}
        
    def extract_temporal_features(self, alerts: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract temporal features for prediction"""
        df = pd.DataFrame(alerts)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create temporal features
        features = pd.DataFrame()
        features['hour'] = df['timestamp'].dt.hour
        features['day_of_week'] = df['timestamp'].dt.dayofweek
        features['day_of_month'] = df['timestamp'].dt.day
        features['month'] = df['timestamp'].dt.month
        features['quarter'] = df['timestamp'].dt.quarter
        
        # Lag features
        for lag in [1, 6, 12, 24, 48]:  # hours
            features[f'alerts_{lag}h_ago'] = df.groupby(df['timestamp'].dt.floor('H')).size().shift(lag)
        
        # Rolling statistics
        hourly_counts = df.groupby(df['timestamp'].dt.floor('H')).size()
        for window in [6, 12, 24]:  # hours
            features[f'rolling_mean_{window}h'] = hourly_counts.rolling(window).mean()
            features[f'rolling_std_{window}h'] = hourly_counts.rolling(window).std()
        
        # Severity distribution
        severity_counts = df.groupby([df['timestamp'].dt.floor('H'), 'severity']).size().unstack(fill_value=0)
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in severity_counts.columns:
                features[f'severity_{severity}_count'] = severity_counts[severity]
        
        return features.fillna(0)
    
    def extract_threat_features(self, alerts: List[Dict[str, Any]]) -> pd.DataFrame:
        """Extract threat-related features for prediction"""
        df = pd.DataFrame(alerts)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        features = pd.DataFrame()
        
        # Category trends
        category_counts = df.groupby([df['timestamp'].dt.floor('H'), 'category']).size().unstack(fill_value=0)
        for category in ['access', 'network', 'endpoint', 'identity', 'audit', 'threat', 'uba']:
            if category in category_counts.columns:
                features[f'category_{category}_count'] = category_counts[category]
        
        # Source trends
        source_counts = df.groupby([df['timestamp'].dt.floor('H'), 'source']).size().unstack(fill_value=0)
        top_sources = source_counts.sum().nlargest(5).index
        for source in top_sources:
            features[f'source_{source}_count'] = source_counts[source]
        
        # Entity-based features
        features['unique_entities'] = df.groupby(df['timestamp'].dt.floor('H')).apply(
            lambda x: len(set([e for entities in x['entities'] for e in entities]))
        )
        
        # Geographic features
        features['unique_countries'] = df.groupby(df['timestamp'].dt.floor('H')).apply(
            lambda x: len(set([loc.get('country') for loc in x['location'] if loc and loc.get('country')]))
        )
        
        return features.fillna(0)
    
    def train_predictive_models(self, alerts: List[Dict[str, Any]], prediction_horizon: int = 24) -> Dict[str, Any]:
        """Train predictive models for various metrics"""
        try:
            if len(alerts) < 100:
                return {'status': 'insufficient_data', 'message': 'Need at least 100 alerts for training'}
            
            # Prepare training data
            temporal_features = self.extract_temporal_features(alerts)
            threat_features = self.extract_threat_features(alerts)
            
            # Combine features
            X = pd.concat([temporal_features, threat_features], axis=1)
            
            # Target variables
            hourly_alerts = pd.DataFrame(alerts)
            hourly_alerts['timestamp'] = pd.to_datetime(hourly_alerts['timestamp'])
            y_volume = hourly_alerts.groupby(hourly_alerts['timestamp'].dt.floor('H')).size()
            
            # Align features and targets
            X = X.reindex(y_volume.index).fillna(0)
            
            # Split data
            split_point = int(len(X) * 0.8)
            X_train, X_test = X[:split_point], X[split_point:]
            y_train, y_test = y_volume[:split_point], y_volume[split_point:]
            
            results = {}
            
            # Train alert volume prediction
            self._train_and_evaluate_model(
                self.models['alert_volume'], 
                X_train, y_train, X_test, y_test,
                'alert_volume', results
            )
            
            # Train threat trend prediction
            self._train_and_evaluate_model(
                self.models['threat_trends'],
                X_train, y_train, X_test, y_test,
                'threat_trends', results
            )
            
            # Train risk forecast
            risk_scores = self._calculate_risk_scores(alerts)
            y_risk = pd.Series(risk_scores, index=y_volume.index)
            y_risk_train, y_risk_test = y_risk[:split_point], y_risk[split_point:]
            
            self._train_and_evaluate_model(
                self.models['risk_forecast'],
                X_train, y_risk_train, X_test, y_risk_test,
                'risk_forecast', results
            )
            
            self.is_trained = True
            logger.info("Predictive models trained successfully")
            
            return {
                'status': 'success',
                'models_trained': list(self.models.keys()),
                'training_results': results,
                'prediction_horizon_hours': prediction_horizon
            }
            
        except Exception as e:
            logger.error(f"Error training predictive models: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def predict_alert_volume(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """Predict alert volume for future hours"""
        if not self.is_trained:
            return []
        
        try:
            # Get latest features
            predictions = []
            current_time = datetime.now()
            
            for hour in range(1, hours_ahead + 1):
                future_time = current_time + timedelta(hours=hour)
                
                # Create features for future time
                features = self._create_future_features(future_time)
                
                # Make prediction
                volume_pred = self.models['alert_volume'].predict([features])[0]
                volume_pred = max(0, int(volume_pred))  # Ensure non-negative
                
                # Predict severity distribution
                severity_dist = self._predict_severity_distribution(features, volume_pred)
                
                # Predict risk level
                risk_pred = self.models['risk_forecast'].predict([features])[0]
                risk_pred = max(0, min(100, risk_pred))  # Clamp to 0-100
                
                predictions.append({
                    'timestamp': future_time.isoformat(),
                    'predicted_volume': volume_pred,
                    'severity_distribution': severity_dist,
                    'predicted_risk_score': risk_pred,
                    'confidence': self._calculate_prediction_confidence(features),
                    'hour_ahead': hour
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting alert volume: {e}")
            return []
    
    def predict_threat_trends(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """Predict threat trends for future days"""
        if not self.is_trained:
            return []
        
        try:
            trends = []
            current_time = datetime.now()
            
            for day in range(1, days_ahead + 1):
                future_date = current_time + timedelta(days=day)
                
                # Aggregate hourly predictions for the day
                day_predictions = []
                for hour in range(24):
                    future_time = future_date.replace(hour=hour)
                    features = self._create_future_features(future_time)
                    trend_pred = self.models['threat_trends'].predict([features])[0]
                    day_predictions.append(max(0, trend_pred))
                
                daily_total = sum(day_predictions)
                
                # Predict top threat categories
                top_threats = self._predict_top_threats(future_date)
                
                trends.append({
                    'date': future_date.date().isoformat(),
                    'predicted_alerts': int(daily_total),
                    'top_threat_categories': top_threats,
                    'risk_level': self._calculate_daily_risk_level(daily_total),
                    'trend_direction': self._calculate_trend_direction(day_predictions)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error predicting threat trends: {e}")
            return []
    
    def _train_and_evaluate_model(self, model, X_train, y_train, X_test, y_test, model_name, results):
        """Train and evaluate a single model"""
        try:
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Store scaler
            self.scalers[model_name] = scaler
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            
            results[model_name] = {
                'mae': mae,
                'mse': mse,
                'rmse': rmse,
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training {model_name}: {e}")
            results[model_name] = {'error': str(e)}
    
    def _calculate_risk_scores(self, alerts: List[Dict[str, Any]]) -> List[float]:
        """Calculate risk scores for alerts"""
        risk_scores = []
        for alert in alerts:
            severity_weight = {'low': 1, 'medium': 3, 'high': 7, 'critical': 10}
            severity = alert.get('severity', 'medium').lower()
            
            confidence = alert.get('confidence', 0.5)
            entity_count = len(alert.get('entities', []))
            
            risk_score = severity_weight.get(severity, 3) * confidence * (1 + entity_count * 0.1)
            risk_scores.append(min(100, risk_score))
        
        return risk_scores
    
    def _create_future_features(self, future_time: datetime) -> np.ndarray:
        """Create feature vector for future time prediction"""
        # This is a simplified version - in production, you'd use more sophisticated feature engineering
        features = [
            future_time.hour,
            future_time.weekday(),
            future_time.day,
            future_time.month,
            future_time.quarter,
            # Add lag features (would need historical data)
            0, 0, 0, 0, 0,  # alerts_1h_ago, alerts_6h_ago, etc.
            # Add rolling features (would need historical data)
            0, 0, 0, 0, 0, 0,  # rolling_mean/std
            # Add severity counts (would need historical data)
            0, 0, 0, 0,  # severity counts
            # Add threat features (would need historical data)
            0, 0, 0, 0, 0, 0, 0,  # category counts
            0, 0, 0, 0, 0,  # source counts
            0,  # unique_entities
            0,  # unique_countries
        ]
        
        return np.array(features)
    
    def _predict_severity_distribution(self, features: np.ndarray, total_alerts: int) -> Dict[str, int]:
        """Predict distribution of alert severities"""
        # Simplified distribution - could be enhanced with separate models
        base_dist = {'critical': 0.1, 'high': 0.2, 'medium': 0.4, 'low': 0.3}
        
        # Adjust based on risk prediction
        risk_pred = self.models['risk_forecast'].predict([features])[0]
        if risk_pred > 70:
            base_dist['critical'] = 0.2
            base_dist['high'] = 0.3
            base_dist['medium'] = 0.3
            base_dist['low'] = 0.2
        
        return {k: int(v * total_alerts) for k, v in base_dist.items()}
    
    def _calculate_prediction_confidence(self, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        # Simplified confidence calculation
        return min(0.95, 0.5 + (len(features) * 0.01))
    
    def _predict_top_threats(self, future_date: datetime) -> List[str]:
        """Predict top threat categories for a future date"""
        # Simplified prediction based on patterns
        weekday_threats = ['network', 'endpoint', 'access']
        weekend_threats = ['threat', 'uba']
        
        if future_date.weekday() < 5:
            return weekday_threats
        else:
            return weekend_threats
    
    def _calculate_daily_risk_level(self, predicted_alerts: int) -> str:
        """Calculate risk level based on predicted alert volume"""
        if predicted_alerts > 100:
            return 'critical'
        elif predicted_alerts > 50:
            return 'high'
        elif predicted_alerts > 20:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_trend_direction(self, hourly_predictions: List[float]) -> str:
        """Calculate trend direction from hourly predictions"""
        if len(hourly_predictions) < 2:
            return 'stable'
        
        first_half = np.mean(hourly_predictions[:len(hourly_predictions)//2])
        second_half = np.mean(hourly_predictions[len(hourly_predictions)//2:])
        
        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'
