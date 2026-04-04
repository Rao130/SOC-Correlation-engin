from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.services.analytics_engine import AnalyticsEngine
from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()
router = APIRouter()

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

@router.get("/visualizations")
async def get_available_visualizations():
    """Get list of available analytics visualizations"""
    try:
        return await analytics_engine.get_available_visualizations()
    except Exception as e:
        logger.error(f"Error getting visualizations: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get visualizations: {str(e)}")

@router.post("/visualizations/{viz_type}")
async def create_visualization(viz_type: str, data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Create advanced visualization"""
    try:
        result = await analytics_engine.generate_visualization(viz_type, data)
        
        # Run visualization generation in background
        background_tasks.add_task(
            analytics_engine.generate_visualization(viz_type, data),
            f"generate_visualization_{viz_type}"
        )
        
        return {
            "message": f"Visualization {viz_type} creation initiated",
            "visualization_id": f"viz_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "status": "processing",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error creating visualization {viz_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create visualization: {str(e)}")

@router.get("/dashboards/{dashboard_type}")
async def get_dashboard(dashboard_type: str):
    """Get analytics dashboard"""
    try:
        dashboard = await analytics_engine.create_dashboard(dashboard_type)
        
        return {
            "dashboard_type": dashboard_type,
            "dashboard": dashboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard {dashboard_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@router.get("/threat-heatmap")
async def get_threat_heatmap(
    time_range: str = Query("24h"),
    severity_filter: Optional[str] = Query(None),
    region_filter: Optional[str] = Query(None)
):
    """Get threat heatmap visualization"""
    try:
        # Mock threat data for heatmap
        threat_data = {
            "threats": [
                {
                    "id": "threat_001",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "severity": "critical",
                    "category": "malware",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": "threat_002",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                    "severity": "high",
                    "category": "phishing",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": "threat_003",
                    "latitude": 35.6762,
                    "longitude": 139.6503,
                    "severity": "medium",
                    "category": "intrusion",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": "threat_004",
                    "latitude": -33.8688,
                    "longitude": 151.2093,
                    "severity": "high",
                    "category": "ddos",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": "threat_005",
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "severity": "medium",
                    "category": "malware",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        }
        
        # Apply filters
        if severity_filter:
            threat_data["threats"] = [
                t for t in threat_data["threats"] 
                if t.get("severity") == severity_filter.lower()
            ]
        
        # Generate visualization
        viz_config = {
            "time_range": time_range,
            "severity_filter": severity_filter,
            "region_filter": region_filter,
            "intensity_radius": 50,
            "gradient_colors": {
                "low": "#4caf50",
                "medium": "#ff9800",
                "high": "#f44336",
                "critical": "#d32f2f"
            }
        }
        
        result = await analytics_engine.generate_visualization("threat_heatmap", threat_data, viz_config)
        
        return {
            "visualization_type": "threat_heatmap",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating threat heatmap: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate threat heatmap: {str(e)}")

@router.get("/attack-timeline")
async def get_attack_timeline(
    time_range: str = Query("24h"),
    attack_type: Optional[str] = Query(None),
    max_events: int = Query(100)
):
    """Get attack timeline visualization"""
    try:
        # Mock attack timeline data
        attack_data = {
            "attacks": [
                {
                    "id": "attack_001",
                    "type": "malware",
                    "severity": "critical",
                    "target": "web_server",
                    "description": "Ransomware attack detected",
                    "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat()
                },
                {
                    "id": "attack_002",
                    "type": "phishing",
                    "severity": "high",
                    "target": "email_system",
                    "description": "Spear phishing campaign",
                    "timestamp": (datetime.utcnow() - timedelta(hours=4)).isoformat()
                },
                {
                    "id": "attack_003",
                    "type": "intrusion",
                    "severity": "medium",
                    "target": "database_server",
                    "description": "Unauthorized access attempt",
                    "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat()
                },
                {
                    "id": "attack_004",
                    "type": "ddos",
                    "severity": "high",
                    "target": "network_infrastructure",
                    "description": "DDoS attack on primary network",
                    "timestamp": (datetime.utcnow() - timedelta(hours=8)).isoformat()
                },
                {
                    "id": "attack_005",
                    "type": "malware",
                    "severity": "low",
                    "target": "workstation",
                    "description": "Suspicious file detected",
                    "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat()
                }
            ]
        }
        
        # Apply filters
        if attack_type:
            attack_data["attacks"] = [
                a for a in attack_data["attacks"] 
                if a.get("type") == attack_type.lower()
            ]
        
        # Generate visualization
        viz_config = {
            "max_events": max_events,
            "time_window": time_range,
            "group_by": "attack_type"
        }
        
        result = await analytics_engine.generate_visualization("attack_timeline", attack_data, viz_config)
        
        return {
            "visualization_type": "attack_timeline",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating attack timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate attack timeline: {str(e)}")

@router.get("/entity-network")
async def get_entity_network(
    entity_type: Optional[str] = Query(None),
    max_nodes: int = Query(500),
    layout_algorithm: str = Query("force_directed")
):
    """Get entity relationship network visualization"""
    try:
        # Mock entity network data
        entity_data = {
            "entities": [
                {
                    "id": "entity_001",
                    "value": "192.168.1.100",
                    "type": "ip",
                    "risk_level": "high",
                    "connections": [2, 3, 4],
                    "last_seen": datetime.utcnow().isoformat()
                },
                {
                    "id": "entity_002",
                    "value": "malicious-domain.com",
                    "type": "domain",
                    "risk_level": "critical",
                    "connections": [1, 5],
                    "last_seen": datetime.utcnow().isoformat()
                },
                {
                    "id": "entity_003",
                    "value": "user@company.com",
                    "type": "email",
                    "risk_level": "medium",
                    "connections": [1, 2],
                    "last_seen": datetime.utcnow().isoformat()
                },
                {
                    "id": "entity_004",
                    "value": "a1b2c3d4e5f6",
                    "type": "hash",
                    "risk_level": "high",
                    "connections": [6],
                    "last_seen": datetime.utcnow().isoformat()
                },
                {
                    "id": "entity_005",
                    "value": "10.0.0.1",
                    "type": "ip",
                    "risk_level": "low",
                    "connections": [1, 3],
                    "last_seen": datetime.utcnow().isoformat()
                }
            ]
        }
        
        # Apply filters
        if entity_type:
            entity_data["entities"] = [
                e for e in entity_data["entities"] 
                if e.get("type") == entity_type.lower()
            ]
        
        # Generate visualization
        viz_config = {
            "max_nodes": max_nodes,
            "layout_algorithm": layout_algorithm,
            "node_size_range": [5, 20]
        }
        
        result = await analytics_engine.generate_visualization("entity_network", entity_data, viz_config)
        
        return {
            "visualization_type": "entity_network",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating entity network: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate entity network: {str(e)}")

@router.get("/pattern-analysis")
async def get_pattern_analysis(
    min_frequency: int = Query(3),
    confidence_threshold: float = Query(0.7),
    pattern_type: Optional[str] = Query(None)
):
    """Get pattern analysis visualization"""
    try:
        # Mock pattern analysis data
        pattern_data = {
            "patterns": [
                {
                    "pattern_id": "pattern_001",
                    "type": "temporal",
                    "description": "Repeated attacks during business hours",
                    "frequency": 15,
                    "confidence": 0.85,
                    "risk_level": "high",
                    "affected_alerts": ["alert_001", "alert_002", "alert_003"]
                },
                {
                    "pattern_id": "pattern_002",
                    "type": "behavioral",
                    "description": "Similar attack vectors across multiple targets",
                    "frequency": 8,
                    "confidence": 0.78,
                    "risk_level": "medium",
                    "affected_alerts": ["alert_004", "alert_005", "alert_006"]
                },
                {
                    "pattern_id": "pattern_003",
                    "type": "semantic",
                    "description": "Similar phishing email content",
                    "frequency": 12,
                    "confidence": 0.82,
                    "risk_level": "high",
                    "affected_alerts": ["alert_007", "alert_008"]
                },
                {
                    "pattern_id": "pattern_004",
                    "type": "geographic",
                    "description": "Attacks from same geographic region",
                    "frequency": 6,
                    "confidence": 0.75,
                    "risk_level": "medium",
                    "affected_alerts": ["alert_009", "alert_010"]
                }
            ]
        }
        
        # Apply filters
        filtered_patterns = []
        for pattern in pattern_data["patterns"]:
            if pattern.get("frequency", 0) >= min_frequency and pattern.get("confidence", 0) >= confidence_threshold:
                if pattern_type is None or pattern.get("type") == pattern_type:
                    filtered_patterns.append(pattern)
        
        pattern_data["patterns"] = filtered_patterns
        
        # Generate visualization
        viz_config = {
            "min_pattern_frequency": min_frequency,
            "confidence_threshold": confidence_threshold,
            "pattern_types": ["temporal", "behavioral", "semantic", "geographic"]
        }
        
        result = await analytics_engine.generate_visualization("pattern_analysis", pattern_data, viz_config)
        
        return {
            "visualization_type": "pattern_analysis",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating pattern analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate pattern analysis: {str(e)}")

@router.get("/compliance-matrix")
async def get_compliance_matrix(
    frameworks: str = Query("ISO_27001,GDPR"),
    scoring_weights: Optional[str] = Query(None)
):
    """Get compliance matrix visualization"""
    try:
        framework_list = frameworks.split(",")
        
        # Mock compliance data
        compliance_data = {
            "ISO_27001_data": {
                "access_control": [
                    {"id": "A.9.1", "compliant": True, "score": 85, "description": "Access control policy"},
                    {"id": "A.9.2", "compliant": True, "score": 78, "description": "User access management"},
                    {"id": "A.9.3", "compliant": False, "score": 45, "description": "Password policy"},
                    {"id": "A.9.4", "compliant": True, "score": 92, "description": "Privileged access"}
                ],
                "audit_trail": [
                    {"id": "A.12.1", "compliant": True, "score": 88, "description": "Audit data generation"},
                    {"id": "A.12.2", "compliant": True, "score": 95, "description": "Audit trail protection"},
                    {"id": "A.12.3", "compliant": False, "score": 65, "description": "Audit review"}
                ]
            },
            "GDPR_data": {
                "data_protection": [
                    {"id": "Art.5", "compliant": True, "score": 92, "description": "Lawfulness of processing"},
                    {"id": "Art.6", "compliant": True, "score": 88, "description": "Purpose limitation"},
                    {"id": "Art.7", "compliant": False, "score": 55, "description": "Data minimization"}
                ]
            }
        }
        
        # Generate visualization
        viz_config = {
            "frameworks": framework_list,
            "scoring_weights": {
                "ISO_27001": 0.3,
                "GDPR": 0.4
            }
        }
        
        result = await analytics_engine.generate_visualization("compliance_matrix", compliance_data, viz_config)
        
        return {
            "visualization_type": "compliance_matrix",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating compliance matrix: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate compliance matrix: {str(e)}")

@router.get("/performance-metrics")
async def get_performance_metrics(
    metrics: str = Query("mttr,response_time,throughput,error_rate"),
    time_ranges: str = Query("1h,24h,7d,30d"),
    alert_thresholds: Optional[str] = Query(None)
):
    """Get performance metrics dashboard"""
    try:
        metrics_list = metrics.split(",")
        time_ranges_list = time_ranges.split(",")
        
        # Mock performance data
        performance_data = {
            "total_alerts": 1250,
            "warning_alerts": 150,
            "critical_alerts": 25,
            "mttr": 95.2,
            "response_time": 850,
            "throughput": 1250,
            "error_rate": 0.5,
            "uptime_percentage": 99.9
        }
        
        # Parse alert thresholds
        threshold_config = {}
        if alert_thresholds:
            for threshold in alert_thresholds.split(","):
                if "warning" in threshold:
                    threshold_config["warning"] = int(threshold.split(":")[1])
                elif "critical" in threshold:
                    threshold_config["critical"] = int(threshold.split(":")[1])
        
        # Generate visualization
        viz_config = {
            "metrics": metrics_list,
            "time_ranges": time_ranges_list,
            "alert_thresholds": threshold_config
        }
        
        result = await analytics_engine.generate_visualization("performance_metrics", performance_data, viz_config)
        
        return {
            "visualization_type": "performance_metrics",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate performance metrics: {str(e)}")

@router.get("/threat-lifecycle")
async def get_threat_lifecycle(
    stages: str = Query("detection,analysis,containment,eradication"),
    automated_transitions: bool = Query(True),
    escalation_rules: Optional[str] = Query(None)
):
    """Get threat lifecycle management visualization"""
    try:
        stages_list = stages.split(",")
        
        # Mock threat lifecycle data
        lifecycle_data = {
            "threats": [
                {
                    "id": "threat_001",
                    "current_stage": "containment",
                    "severity": "critical",
                    "detected_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                    "assigned_analyst": "analyst_001",
                    "eta_resolution": (datetime.utcnow() + timedelta(hours=4)).isoformat()
                },
                {
                    "id": "threat_002",
                    "current_stage": "analysis",
                    "severity": "high",
                    "detected_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                    "assigned_analyst": "analyst_002",
                    "eta_resolution": (datetime.utcnow() + timedelta(hours=8)).isoformat()
                },
                {
                    "id": "threat_003",
                    "current_stage": "detection",
                    "severity": "medium",
                    "detected_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    "assigned_analyst": "",
                    "eta_resolution": (datetime.utcnow() + timedelta(hours=24)).isoformat()
                }
            ]
        }
        
        # Parse escalation rules
        escalation_config = {}
        if escalation_rules:
            for rule in escalation_rules.split(","):
                if "critical_to_high" in rule:
                    escalation_config["critical_to_high"] = rule.split(":")[1]
                elif "high_to_medium" in rule:
                    escalation_config["high_to_medium"] = rule.split(":")[1]
        
        # Generate visualization
        viz_config = {
            "stages": stages_list,
            "automated_transitions": automated_transitions,
            "escalation_rules": escalation_config
        }
        
        result = await analytics_engine.generate_visualization("threat_lifecycle", lifecycle_data, viz_config)
        
        return {
            "visualization_type": "threat_lifecycle",
            "data": result.get("data", {}),
            "config": viz_config,
            "metadata": result.get("metadata", {}),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating threat lifecycle: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate threat lifecycle: {str(e)}")

@router.get("/export/{viz_type}")
async def export_visualization(
    viz_type: str,
    format: str = Query("json"),
    filters: Optional[str] = Query(None)
):
    """Export visualization data"""
    try:
        # Parse filters
        filter_config = {}
        if filters:
            for filter_pair in filters.split(","):
                key, value = filter_pair.split(":")
                filter_config[key] = value
        
        result = await analytics_engine.export_visualization(viz_type, format, filter_config)
        
        return {
            "visualization_type": viz_type,
            "format": format,
            "filters": filter_config,
            "export_data": result,
            "exported_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error exporting visualization {viz_type}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export visualization: {str(e)}")

@router.get("/executive-dashboard")
async def get_executive_dashboard():
    """Get executive-level analytics dashboard"""
    try:
        dashboard = await analytics_engine.create_dashboard("executive")
        
        return {
            "dashboard_type": "executive",
            "dashboard": dashboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting executive dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get executive dashboard: {str(e)}")

@router.get("/analyst-dashboard")
async def get_analyst_dashboard():
    """Get analyst-level analytics dashboard"""
    try:
        dashboard = await analytics_engine.create_dashboard("analyst")
        
        return {
            "dashboard_type": "analyst",
            "dashboard": dashboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting analyst dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analyst dashboard: {str(e)}")

@router.get("/realtime-dashboard")
async def get_realtime_dashboard():
    """Get real-time monitoring dashboard"""
    try:
        dashboard = await analytics_engine.create_dashboard("real_time")
        
        return {
            "dashboard_type": "real_time",
            "dashboard": dashboard,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting real-time dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get real-time dashboard: {str(e)}")
