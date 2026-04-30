"""
Advanced Analytics API Routes
Enterprise-grade security analytics with AI/ML integration
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.core.database import get_db
from app.core.logging import logger
from app.services.advanced_correlation import correlation_engine
from app.services.threat_scoring import threat_scoring_engine
from app.services.attack_chain_mapper import attack_chain_mapper
from app.services.anomaly_detection import anomaly_detection_engine
from app.services.autonomous_response import autonomous_response_engine

router = APIRouter()

# Pydantic models for API
class AlertContext(BaseModel):
    alert_id: str
    severity: str
    category: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    user: Optional[str] = None
    target_asset: Optional[str] = None
    timestamp: datetime
    description: Optional[str] = None

class CorrelationRequest(BaseModel):
    alerts: List[AlertContext]
    context: Dict[str, Any] = {}

class ThreatScoringRequest(BaseModel):
    alerts: List[AlertContext]
    context: Dict[str, Any] = {}

class AutonomousResponseRequest(BaseModel):
    alerts: List[AlertContext]
    context: Dict[str, Any] = {}

@router.post("/correlations")
async def analyze_correlations(request: CorrelationRequest):
    """Perform advanced correlation analysis"""
    try:
        logger.info(f"🔍 Analyzing correlations for {len(request.alerts)} alerts")
        
        # Convert alerts to dict format
        alerts_dict = [alert.dict() for alert in request.alerts]
        
        # Perform correlation analysis
        correlations = await correlation_engine.correlate_alerts(alerts_dict)
        
        # Convert to response format
        correlation_results = []
        for corr in correlations:
            correlation_results.append({
                "correlation_id": corr.correlation_id,
                "correlation_type": corr.correlation_type,
                "confidence_score": corr.confidence_score,
                "related_alerts": corr.related_alerts,
                "severity": corr.severity,
                "description": corr.description,
                "attack_stage": corr.attack_stage,
                "threat_indicators": corr.threat_indicators,
                "business_impact": corr.business_impact,
                "timestamp": corr.timestamp.isoformat() if corr.timestamp else None
            })
        
        # Get summary
        summary = await correlation_engine.get_correlation_summary(correlations)
        
        return {
            "correlations": correlation_results,
            "summary": summary,
            "total_correlations": len(correlation_results),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Correlation analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Correlation analysis failed: {str(e)}")

@router.post("/threat-scores")
async def calculate_threat_scores(request: ThreatScoringRequest):
    """Calculate AI-powered threat scores"""
    try:
        logger.info(f"🎯 Calculating threat scores for {len(request.alerts)} alerts")
        
        threat_scores = []
        alerts_dict = [alert.dict() for alert in request.alerts]
        
        for alert in alerts_dict:
            score = await threat_scoring_engine.calculate_threat_score(alert, request.context)
            threat_scores.append({
                "alert_id": score.alert_id,
                "overall_score": score.overall_score,
                "risk_level": score.risk_level,
                "confidence": score.confidence,
                "score_breakdown": score.score_breakdown,
                "threat_indicators": score.threat_indicators,
                "business_impact": score.business_impact,
                "recommended_actions": score.recommended_actions,
                "prediction_confidence": score.prediction_confidence
            })
        
        # Calculate summary statistics
        if threat_scores:
            avg_score = sum(s["overall_score"] for s in threat_scores) / len(threat_scores)
            risk_distribution = {}
            for score in threat_scores:
                risk_level = score["risk_level"]
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
        else:
            avg_score = 0
            risk_distribution = {}
        
        return {
            "threat_scores": threat_scores,
            "summary": {
                "total_alerts": len(threat_scores),
                "average_score": round(avg_score, 2),
                "risk_distribution": risk_distribution,
                "high_risk_alerts": len([s for s in threat_scores if s["risk_level"] in ["critical", "high"]])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Threat scoring failed: {e}")
        raise HTTPException(status_code=500, detail=f"Threat scoring failed: {str(e)}")

@router.post("/attack-chains")
async def map_attack_chains(request: CorrelationRequest):
    """Map attack chains using MITRE ATT&CK framework"""
    try:
        logger.info(f"🔗 Mapping attack chains for {len(request.alerts)} alerts")
        
        alerts_dict = [alert.dict() for alert in request.alerts]
        attack_chains = await attack_chain_mapper.map_attack_chains(alerts_dict)
        
        # Convert to response format
        chain_results = []
        for chain in attack_chains:
            chain_data = {
                "chain_id": chain.chain_id,
                "attacker_id": chain.attacker_id,
                "start_time": chain.start_time.isoformat(),
                "end_time": chain.end_time.isoformat(),
                "duration": str(chain.duration),
                "stages": [stage.value for stage in chain.stages],
                "confidence_score": chain.confidence_score,
                "severity": chain.severity,
                "threat_actor": chain.threat_actor,
                "malware_family": chain.malware_family,
                "affected_assets": list(chain.affected_assets),
                "business_impact": chain.business_impact,
                "containment_status": chain.containment_status,
                "mitigation_recommendations": chain.mitigation_recommendations,
                "node_count": len(chain.nodes)
            }
            chain_results.append(chain_data)
        
        # Get summary
        summary = await attack_chain_mapper.get_attack_chain_summary()
        
        return {
            "attack_chains": chain_results,
            "summary": summary,
            "total_chains": len(chain_results),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Attack chain mapping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Attack chain mapping failed: {str(e)}")

@router.post("/anomaly-detection")
async def detect_anomalies(request: CorrelationRequest):
    """Perform advanced anomaly detection"""
    try:
        logger.info(f"🔍 Detecting anomalies for {len(request.alerts)} events")
        
        alerts_dict = [alert.dict() for alert in request.alerts]
        anomalies = await anomaly_detection_engine.detect_anomalies(alerts_dict)
        
        # Convert to response format
        anomaly_results = []
        for anomaly in anomalies:
            anomaly_data = {
                "detection_id": anomaly.detection_id,
                "anomaly_type": anomaly.anomaly_type.value,
                "severity": anomaly.severity,
                "confidence_score": anomaly.confidence_score,
                "anomaly_score": anomaly.anomaly_score,
                "description": anomaly.description,
                "affected_entities": anomaly.affected_entities,
                "indicators": anomaly.indicators,
                "baseline_deviation": anomaly.baseline_deviation,
                "timestamp": anomaly.timestamp.isoformat(),
                "context": anomaly.context,
                "recommended_actions": anomaly.recommended_actions,
                "false_positive_probability": anomaly.false_positive_probability
            }
            anomaly_results.append(anomaly_data)
        
        # Get summary
        summary = await anomaly_detection_engine.get_anomaly_summary(anomalies)
        
        return {
            "anomalies": anomaly_results,
            "summary": summary,
            "total_anomalies": len(anomaly_results),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Anomaly detection failed: {e}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.post("/autonomous-response")
async def execute_autonomous_response(request: AutonomousResponseRequest, background_tasks: BackgroundTasks):
    """Execute autonomous response actions"""
    try:
        logger.info(f"🤖 Executing autonomous response for {len(request.alerts)} alerts")
        
        alerts_dict = [alert.dict() for alert in request.alerts]
        
        # Execute autonomous response
        response_results = await autonomous_response_engine.execute_autonomous_response(alerts_dict, request.context)
        
        return {
            "response_results": response_results,
            "execution_id": f"response_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Autonomous response failed: {e}")
        raise HTTPException(status_code=500, detail=f"Autonomous response failed: {str(e)}")

@router.get("/threat-metrics")
async def get_threat_metrics():
    """Get comprehensive threat metrics"""
    try:
        # Mock threat metrics (in real implementation, calculate from database)
        threat_metrics = {
            "total_threats": 156,
            "critical_threats": 12,
            "high_risk_threats": 34,
            "threat_trends": [
                {
                    "date": (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d"),
                    "threats": 45 + i * 2,
                    "critical": 5 + i,
                    "resolved": 40 + i * 3
                } for i in range(30)
            ],
            "threat_types": {
                "Malware": 45,
                "Phishing": 32,
                "DDoS": 28,
                "Insider": 18,
                "APT": 15,
                "Zero-Day": 8
            },
            "geographic_distribution": {
                "North America": 45,
                "Europe": 38,
                "Asia": 32,
                "Other": 21
            },
            "attack_vectors": {
                "Email": 35,
                "Web": 28,
                "Network": 25,
                "Endpoint": 18,
                "Cloud": 12
            },
            "mitre_techniques": {
                "T1190": 25,
                "T1566": 20,
                "T1059": 18,
                "T1078": 15,
                "T1021": 12
            }
        }
        
        return {
            "threat_metrics": threat_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get threat metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get threat metrics: {str(e)}")

@router.get("/business-metrics")
async def get_business_metrics():
    """Get business impact metrics"""
    try:
        # Mock business metrics
        business_metrics = {
            "risk_score": 67.5,
            "business_impact": "medium",
            "financial_exposure": 2500000,
            "compliance_score": 82.3,
            "mttr": 45,  # minutes
            "mttd": 12,  # minutes
            "roi": 285,  # percentage
            "risk_reduction": 73.2,  # percentage
            "cost_savings": 1250000,
            "productivity_gain": 45.6,
            "security_maturity": "advanced"
        }
        
        return {
            "business_metrics": business_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get business metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get business metrics: {str(e)}")

@router.get("/predictive-analytics")
async def get_predictive_analytics():
    """Get predictive analytics and threat forecasting"""
    try:
        # Mock predictive analytics
        predictions = [
            {
                "type": "Malware Outbreak",
                "probability": 0.75,
                "timeframe": "Next 24 hours",
                "risk_level": "high",
                "confidence": 0.82,
                "indicators": ["Recent malware detections", "Suspicious network traffic"],
                "recommended_actions": ["Enhance monitoring", "Update signatures", "Prepare response team"]
            },
            {
                "type": "Data Exfiltration",
                "probability": 0.45,
                "timeframe": "Next 48 hours",
                "risk_level": "medium",
                "confidence": 0.68,
                "indicators": ["Unusual data access patterns", "Large file transfers"],
                "recommended_actions": ["Monitor egress traffic", "Review access logs", "Enhance DLP"]
            },
            {
                "type": "Insider Threat",
                "probability": 0.30,
                "timeframe": "Next 7 days",
                "risk_level": "medium",
                "confidence": 0.55,
                "indicators": ["Unusual user behavior", "After-hours activity"],
                "recommended_actions": ["User behavior analytics", "Access review", "Enhanced monitoring"]
            }
        ]
        
        return {
            "predictions": predictions,
            "forecast_summary": {
                "total_predictions": len(predictions),
                "high_risk_predictions": len([p for p in predictions if p["risk_level"] == "high"]),
                "average_confidence": sum(p["confidence"] for p in predictions) / len(predictions),
                "next_24h_alerts": len([p for p in predictions if "24 hours" in p["timeframe"]])
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get predictive analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get predictive analytics: {str(e)}")

@router.get("/hunting-insights")
async def get_hunting_insights():
    """Get threat hunting insights and recommendations"""
    try:
        # Mock hunting insights
        insights = [
            {
                "title": "Suspicious PowerShell Activity",
                "description": "Multiple PowerShell executions with encoded commands detected across several workstations",
                "priority": "high",
                "confidence": 0.85,
                "indicators": ["Powerhell", "Base64 encoding", "Command obfuscation"],
                "recommended_actions": ["Investigate PowerShell logs", "Check for malware", "Review user activity"],
                "affected_assets": ["WS-001", "WS-002", "WS-003"],
                "mitre_technique": "T1059"
            },
            {
                "title": "Unusual Network Traffic Patterns",
                "description": "Anomalous network traffic detected between internal systems and external IPs",
                "priority": "medium",
                "confidence": 0.72,
                "indicators": ["Unusual port usage", "Large data transfers", "Off-hours activity"],
                "recommended_actions": ["Analyze network flows", "Check for data exfiltration", "Review firewall logs"],
                "affected_assets": ["Server-001", "Server-002"],
                "mitre_technique": "T1041"
            },
            {
                "title": "Privilege Escalation Indicators",
                "description": "Users with elevated privileges accessing unusual systems and data",
                "priority": "high",
                "confidence": 0.78,
                "indicators": ["Admin account usage", "Unusual system access", "Sensitive data access"],
                "recommended_actions": ["Review admin activity", "Check for compromise", "Audit access logs"],
                "affected_assets": ["DC-001", "DB-001"],
                "mitre_technique": "T1068"
            }
        ]
        
        return {
            "hunting_insights": insights,
            "summary": {
                "total_insights": len(insights),
                "high_priority_insights": len([i for i in insights if i["priority"] == "high"]),
                "average_confidence": sum(i["confidence"] for i in insights) / len(insights),
                "affected_systems": len(set([asset for insight in insights for asset in insight["affected_assets"]]))
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get hunting insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get hunting insights: {str(e)}")

@router.get("/system-health")
async def get_system_health():
    """Get system health and performance metrics"""
    try:
        # Mock system health data
        system_health = {
            "overall_status": "healthy",
            "components": {
                "correlation_engine": {
                    "status": "healthy",
                    "response_time_ms": 45,
                    "last_run": datetime.utcnow().isoformat(),
                    "processed_alerts": 156
                },
                "threat_scoring": {
                    "status": "healthy",
                    "response_time_ms": 23,
                    "last_run": datetime.utcnow().isoformat(),
                    "scores_calculated": 89
                },
                "attack_chain_mapper": {
                    "status": "healthy",
                    "response_time_ms": 67,
                    "last_run": datetime.utcnow().isoformat(),
                    "chains_mapped": 12
                },
                "anomaly_detection": {
                    "status": "healthy",
                    "response_time_ms": 89,
                    "last_run": datetime.utcnow().isoformat(),
                    "anomalies_detected": 5
                },
                "autonomous_response": {
                    "status": "healthy",
                    "response_time_ms": 156,
                    "last_run": datetime.utcnow().isoformat(),
                    "responses_executed": 3
                }
            },
            "performance_metrics": {
                "average_response_time": 76,
                "throughput_per_second": 125,
                "error_rate": 0.02,
                "uptime_percentage": 99.8
            },
            "resource_usage": {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 34.1,
                "network_usage": 12.5
            }
        }
        
        return {
            "system_health": system_health,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")

@router.get("/compliance-status")
async def get_compliance_status():
    """Get compliance and governance status"""
    try:
        # Mock compliance data
        compliance_status = {
            "overall_score": 82.3,
            "compliance_frameworks": {
                "GDPR": {
                    "score": 85.2,
                    "status": "compliant",
                    "last_audit": "2024-01-15",
                    "next_audit": "2024-07-15",
                    "findings": 2,
                    "remediations": 2
                },
                "HIPAA": {
                    "score": 88.7,
                    "status": "compliant",
                    "last_audit": "2024-01-10",
                    "next_audit": "2024-07-10",
                    "findings": 1,
                    "remediations": 1
                },
                "PCI-DSS": {
                    "score": 79.4,
                    "status": "partial_compliance",
                    "last_audit": "2024-01-20",
                    "next_audit": "2024-04-20",
                    "findings": 5,
                    "remediations": 3
                },
                "SOX": {
                    "score": 91.1,
                    "status": "compliant",
                    "last_audit": "2024-01-05",
                    "next_audit": "2024-07-05",
                    "findings": 1,
                    "remediations": 1
                },
                "ISO27001": {
                    "score": 86.8,
                    "status": "compliant",
                    "last_audit": "2024-01-12",
                    "next_audit": "2024-07-12",
                    "findings": 3,
                    "remediations": 3
                }
            },
            "risk_assessments": {
                "total_risks": 23,
                "high_risks": 5,
                "medium_risks": 12,
                "low_risks": 6,
                "mitigated_risks": 18
            },
            "audit_trail": {
                "total_events": 15420,
                "last_24h_events": 342,
                "critical_events": 12,
                "retention_days": 2555
            }
        }
        
        return {
            "compliance_status": compliance_status,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get compliance status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get compliance status: {str(e)}")
