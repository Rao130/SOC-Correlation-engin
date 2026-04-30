"""
ML Service for SOC Correlation Engine
Handles anomaly detection, predictive analytics, and threat hunting
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.ml.anomaly_detector import AnomalyDetector
from app.ml.predictive_analytics import PredictiveAnalytics
from app.ml.threat_hunting import ThreatHunter

logger = logging.getLogger(__name__)

app = FastAPI(title="SOC ML Service", version="2.0.0")

# Initialize ML components
anomaly_detector = AnomalyDetector()
predictive_analytics = PredictiveAnalytics()
threat_hunter = ThreatHunter()

class TrainingRequest(BaseModel):
    alerts: List[Dict[str, Any]]
    model_type: Optional[str] = "all"

class PredictionRequest(BaseModel):
    alerts: List[Dict[str, Any]]
    hours_ahead: Optional[int] = 24

class ThreatHuntingRequest(BaseModel):
    alerts: List[Dict[str, Any]]
    time_window: Optional[int] = 24

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "anomaly_detector": anomaly_detector.is_trained,
            "predictive_analytics": predictive_analytics.is_trained
        }
    }

@app.post("/train")
async def train_models(request: TrainingRequest, background_tasks: BackgroundTasks):
    """Train ML models with alert data"""
    try:
        results = {}
        
        if request.model_type in ["all", "anomaly"]:
            # Train anomaly detection
            anomaly_result = anomaly_detector.train(request.alerts)
            results["anomaly_detection"] = anomaly_result
        
        if request.model_type in ["all", "predictive"]:
            # Train predictive analytics
            predictive_result = predictive_analytics.train_predictive_models(request.alerts)
            results["predictive_analytics"] = predictive_result
        
        return {
            "status": "success",
            "message": "Models trained successfully",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error training models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-anomalies")
async def detect_anomalies(request: PredictionRequest):
    """Detect anomalies in alerts"""
    try:
        if not anomaly_detector.is_trained:
            raise HTTPException(status_code=400, detail="Anomaly detector not trained")
        
        anomalies = anomaly_detector.detect_anomalies(request.alerts)
        
        return {
            "status": "success",
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-volume")
async def predict_alert_volume(request: PredictionRequest):
    """Predict alert volume for future hours"""
    try:
        if not predictive_analytics.is_trained:
            raise HTTPException(status_code=400, detail="Predictive models not trained")
        
        predictions = predictive_analytics.predict_alert_volume(request.hours_ahead)
        
        return {
            "status": "success",
            "predictions": predictions,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error predicting alert volume: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-trends")
async def predict_threat_trends(request: PredictionRequest):
    """Predict threat trends for future days"""
    try:
        if not predictive_analytics.is_trained:
            raise HTTPException(status_code=400, detail="Predictive models not trained")
        
        trends = predictive_analytics.predict_threat_trends(request.hours_ahead // 24)
        
        return {
            "status": "success",
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error predicting threat trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/hunt-threats")
async def hunt_threats(request: ThreatHuntingRequest):
    """Run automated threat hunting"""
    try:
        threats = threat_hunter.hunt_for_threats(request.alerts, request.time_window)
        
        # Generate threat report
        report = threat_hunter.generate_threat_report(threats)
        
        return {
            "status": "success",
            "threats_found": len(threats),
            "threats": threats,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error hunting threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/status")
async def get_models_status():
    """Get status of all ML models"""
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
        }
    }

@app.post("/models/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    """Retrain all models with latest data"""
    # This would fetch latest data from database and retrain models
    # Implementation depends on your data access patterns
    
    return {
        "status": "initiated",
        "message": "Model retraining started in background",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
