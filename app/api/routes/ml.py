"""
ML API Routes for SOC Correlation Engine
Integrates anomaly detection, predictive analytics, and threat hunting
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.logging import logger
from app.ml.anomaly_detector import AnomalyDetector
from app.ml.predictive_analytics import PredictiveAnalytics
from app.ml.threat_hunting import ThreatHunter

router = APIRouter()

# Global ML instances
anomaly_detector = AnomalyDetector()
predictive_analytics = PredictiveAnalytics()
threat_hunter = ThreatHunter()

@router.post("/train")
async def train_ml_models(
    background_tasks: BackgroundTasks,
    model_type: str = "all",
    limit: int = 1000,
    db = Depends(get_db)
):
    """Train ML models with historical alert data"""
    try:
        # Fetch training data
        file_db = db.get_database()
        if file_db is not None:
            collection = file_db.alerts
            alerts_cursor = collection.find().sort("timestamp", -1).limit(limit)
            alerts = []
            
            async for alert in alerts_cursor:
                # Convert ObjectId to string
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            if len(alerts) < 100:
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least 100 alerts, got {len(alerts)}",
                    "alerts_count": len(alerts)
                }
            
            results = {}
            
            # Train anomaly detection
            if model_type in ["all", "anomaly"]:
                anomaly_result = anomaly_detector.train(alerts)
                results["anomaly_detection"] = anomaly_result
            
            # Train predictive analytics
            if model_type in ["all", "predictive"]:
                predictive_result = predictive_analytics.train_predictive_models(alerts)
                results["predictive_analytics"] = predictive_result
            
            return {
                "status": "success",
                "message": "ML models trained successfully",
                "alerts_used": len(alerts),
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {"status": "error", "message": "Database connection failed"}
    
    except Exception as e:
        logger.error(f"Error training ML models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect-anomalies")
async def detect_anomalies(
    hours_back: int = 24,
    limit: int = 100,
    db = Depends(get_db)
):
    """Detect anomalies in recent alerts"""
    try:
        if not anomaly_detector.is_trained:
            return {
                "status": "not_trained",
                "message": "Anomaly detector not trained yet",
                "action": "Call /train endpoint first"
            }
        
        # Fetch recent alerts
        file_db = db.get_database()
        if file_db is not None:
            collection = file_db.alerts
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            alerts_cursor = collection.find({
                "timestamp": {"$gte": cutoff_time}
            }).sort("timestamp", -1).limit(limit)
            
            alerts = []
            async for alert in alerts_cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            anomalies = anomaly_detector.detect_anomalies(alerts)
            
            return {
                "status": "success",
                "alerts_analyzed": len(alerts),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies,
                "time_window_hours": hours_back,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {"status": "error", "message": "Database connection failed"}
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-volume")
async def predict_alert_volume(hours_ahead: int = 24):
    """Predict alert volume for future hours"""
    try:
        if not predictive_analytics.is_trained:
            return {
                "status": "not_trained",
                "message": "Predictive models not trained yet",
                "action": "Call /train endpoint first"
            }
        
        predictions = predictive_analytics.predict_alert_volume(hours_ahead)
        
        return {
            "status": "success",
            "predictions": predictions,
            "hours_predicted": hours_ahead,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error predicting alert volume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict-trends")
async def predict_threat_trends(days_ahead: int = 7):
    """Predict threat trends for future days"""
    try:
        if not predictive_analytics.is_trained:
            return {
                "status": "not_trained",
                "message": "Predictive models not trained yet",
                "action": "Call /train endpoint first"
            }
        
        trends = predictive_analytics.predict_threat_trends(days_ahead)
        
        return {
            "status": "success",
            "trends": trends,
            "days_predicted": days_ahead,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error predicting threat trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hunt-threats")
async def hunt_threats(
    hours_back: int = 24,
    limit: int = 1000,
    db = Depends(get_db)
):
    """Run automated threat hunting"""
    try:
        # Fetch recent alerts
        file_db = db.get_database()
        if file_db is not None:
            collection = file_db.alerts
            
            # Calculate cutoff time
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            alerts_cursor = collection.find({
                "timestamp": {"$gte": cutoff_time}
            }).sort("timestamp", -1).limit(limit)
            
            alerts = []
            async for alert in alerts_cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            threats = threat_hunter.hunt_for_threats(alerts, hours_back)
            report = threat_hunter.generate_threat_report(threats)
            
            return {
                "status": "success",
                "alerts_analyzed": len(alerts),
                "threats_found": len(threats),
                "threats": threats[:10],  # Return top 10 threats
                "report": report,
                "time_window_hours": hours_back,
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            return {"status": "error", "message": "Database connection failed"}
    
    except Exception as e:
        logger.error(f"Error hunting threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_ml_status():
    """Get status of all ML components"""
    return {
        "anomaly_detector": {
            "is_trained": anomaly_detector.is_trained,
            "models": list(anomaly_detector.models.keys()),
            "feature_count": len(anomaly_detector.feature_columns)
        },
        "predictive_analytics": {
            "is_trained": predictive_analytics.is_trained,
            "models": list(predictive_analytics.models.keys()),
            "feature_count": len(predictive_analytics.feature_columns)
        },
        "threat_hunting": {
            "rules_count": len(threat_hunter.hunting_rules),
            "threat_patterns": len(threat_hunter.threat_patterns),
            "mitre_mapping": len(threat_hunter.mitre_attck_mapping)
        },
        "timestamp": datetime.now().isoformat()
    }

@router.post("/retrain")
async def retrain_models(
    background_tasks: BackgroundTasks,
    model_type: str = "all",
    db = Depends(get_db)
):
    """Retrain ML models with latest data"""
    try:
        # Schedule retraining in background
        background_tasks.add_task(
            _retrain_models_background,
            model_type=model_type,
            db=db
        )
        
        return {
            "status": "initiated",
            "message": f"Model retraining started for {model_type}",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error initiating model retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _retrain_models_background(model_type: str, db):
    """Background task for model retraining"""
    try:
        logger.info(f"Starting background retraining for {model_type}")
        
        # Fetch latest data
        file_db = db.get_database()
        if file_db is not None:
            collection = file_db.alerts
            alerts_cursor = collection.find().sort("timestamp", -1).limit(5000)
            alerts = []
            
            async for alert in alerts_cursor:
                alert['_id'] = str(alert['_id'])
                alerts.append(alert)
            
            # Retrain models
            if model_type in ["all", "anomaly"]:
                anomaly_detector.train(alerts)
            
            if model_type in ["all", "predictive"]:
                predictive_analytics.train_predictive_models(alerts)
            
            logger.info(f"Background retraining completed for {model_type}")
    
    except Exception as e:
        logger.error(f"Error in background retraining: {e}")

@router.get("/models/info")
async def get_models_info():
    """Get detailed information about ML models"""
    return {
        "anomaly_detection": {
            "algorithms": ["Isolation Forest", "DBSCAN"],
            "features": [
                "Temporal features (hour, day, month)",
                "Severity and confidence metrics",
                "Entity-based features",
                "Category one-hot encoding",
                "Geographic features",
                "Behavioral patterns"
            ],
            "output": "Anomaly scores and classification"
        },
        "predictive_analytics": {
            "algorithms": [
                "Random Forest", 
                "Gradient Boosting", 
                "Linear Regression"
            ],
            "features": [
                "Temporal patterns and trends",
                "Historical alert volumes",
                "Severity distribution",
                "Category trends",
                "Source patterns",
                "Geographic distribution"
            ],
            "outputs": [
                "Alert volume predictions",
                "Threat trend forecasts",
                "Risk level predictions"
            ]
        },
        "threat_hunting": {
            "rules": list(threat_hunter.hunting_rules.keys()),
            "patterns": list(threat_hunter.threat_patterns.keys()),
            "mitre_framework": "MITRE ATT&CK",
            "outputs": [
                "Automated threat detection",
                "Investigation recommendations",
                "Threat reports"
            ]
        }
    }
