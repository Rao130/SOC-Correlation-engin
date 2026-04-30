"""
Analytics API Routes
Provides security analytics and metrics endpoints
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
from app.services.analytics_engine import AnalyticsEngine
from app.core.database import get_db
from app.core.logging import logger

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
    """Get threat heatmap visualization with real data"""
    try:
        from app.services.real_data_generator import data_generator
        
        # Get real alerts from data generator
        alerts = data_generator.get_recent_alerts(100)
        
        # Convert alerts to threat heatmap data
        threats = []
        for alert in alerts:
            if alert.get('location') and alert.get('location', {}).get('latitude'):
                threat = {
                    "id": alert.get('_id', f"threat_{len(threats)}"),
                    "latitude": alert['location']['latitude'],
                    "longitude": alert['location']['longitude'],
                    "severity": alert.get('severity', 'unknown'),
                    "category": alert.get('category', 'unknown'),
                    "title": alert.get('title', 'Unknown Threat'),
                    "description": alert.get('description', ''),
                    "timestamp": alert.get('timestamp', datetime.utcnow().isoformat()),
                    "source": alert.get('source', 'Unknown'),
                    "confidence": alert.get('confidence', 0)
}
                
                # Apply filters
                if severity_filter and threat['severity'] != severity_filter:
                    continue
                if region_filter and threat.get('country') != region_filter:
                    continue
                    
                threats.append(threat)
        
        return {
            "threats": threats,
            "total_count": len(threats),
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error generating threat heatmap: {e}")
        return {
            "threats": [],
            "total_count": 0,
            "time_range": time_range,
            "generated_at": datetime.utcnow().isoformat()
        }

@router.get("/realtime-stats")
async def get_realtime_statistics():
    """Get real-time analytics statistics"""
    try:
        from app.services.real_data_generator import data_generator
        from app.services.network_monitor import network_monitor
        from app.services.log_streamer import log_streamer
        
        # Get alert statistics
        alert_stats = data_generator.get_alert_statistics()
        
        # Get network statistics
        network_stats = {
            "monitoring_active": network_monitor.monitoring_active,
            "memory_alerts_count": len(network_monitor.memory_alerts),
            "recent_network_alerts": len([a for a in network_monitor.memory_alerts 
                                        if self._is_recent_alert(a.get('timestamp', ''))])
        }
        
        # Get log statistics
        log_stats = log_streamer.get_log_statistics()
        
        # Combine all statistics
        combined_stats = {
            "alerts": alert_stats,
            "network": network_stats,
            "logs": log_stats,
            "total_alerts": len(data_generator.generated_alerts) + len(network_monitor.memory_alerts),
            "total_logs": len(log_streamer.generated_logs),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return combined_stats
        
    except Exception as e:
        logger.error(f"Error getting realtime statistics: {e}")
        # Return fallback data
        return {
            "alerts": {"total": 0, "by_severity": {}, "by_category": {}, "last_hour": 0},
            "network": {"monitoring_active": False, "memory_alerts_count": 0, "recent_network_alerts": 0},
            "logs": {"total": 0, "by_severity": {}, "by_source": {}, "security_relevant": 0, "last_minute": 0},
            "total_alerts": 0,
            "total_logs": 0,
            "generated_at": datetime.utcnow().isoformat()
        }

def _is_recent_alert(timestamp_str: str) -> bool:
    """Check if alert is recent (within last hour)"""
    try:
        if not timestamp_str:
            return False
        
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str.replace('Z', '+00:00')
        
        alert_time = datetime.fromisoformat(timestamp_str)
        return alert_time > datetime.utcnow() - timedelta(hours=1)
    except (ValueError, TypeError, AttributeError):
        return False

@router.get("/dashboard-data")
async def get_dashboard_data():
    """Get comprehensive dashboard data for analytics"""
    try:
        from app.services.real_data_generator import data_generator
        from app.services.network_monitor import network_monitor
        from app.services.log_streamer import log_streamer
        
        # Get all alerts
        all_alerts = []
        if hasattr(data_generator, 'generated_alerts'):
            all_alerts.extend(data_generator.generated_alerts)
        if hasattr(network_monitor, 'memory_alerts'):
            all_alerts.extend(network_monitor.memory_alerts)
        
        # Calculate analytics data
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        category_counts = {}
        source_counts = {}
        hourly_trends = {}
        
        for alert in all_alerts:
            # Count by severity
            severity = alert.get('severity', 'unknown')
            if severity in severity_counts:
                severity_counts[severity] += 1
            
            # Count by category
            category = alert.get('category', 'unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
            
            # Count by source
            source = alert.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Hourly trends
            try:
                timestamp = alert.get('timestamp', '')
                if timestamp:
                    if timestamp.endswith('Z'):
                        timestamp = timestamp.replace('Z', '+00:00')
                    alert_time = datetime.fromisoformat(timestamp)
                    hour_key = alert_time.strftime('%Y-%m-%d %H:00')
                    hourly_trends[hour_key] = hourly_trends.get(hour_key, 0) + 1
            except:
                continue
        
        # Get log data
        log_stats = log_streamer.get_log_statistics()
        
        return {
            "summary": {
                "total_alerts": len(all_alerts),
                "critical_alerts": severity_counts.get('critical', 0),
                "high_alerts": severity_counts.get('high', 0),
                "total_logs": len(log_streamer.generated_logs) if hasattr(log_streamer, 'generated_logs') else 0,
                "error_logs": log_stats.get('by_severity', {}).get('ERROR', 0),
                "critical_logs": log_stats.get('by_severity', {}).get('CRITICAL', 0)
            },
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "source_analysis": source_counts,
            "hourly_trends": hourly_trends,
            "log_statistics": log_stats,
            "recent_alerts": all_alerts[:10],  # Last 10 alerts
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        # Return fallback data
        return {
            "summary": {
                "total_alerts": 0,
                "critical_alerts": 0,
                "high_alerts": 0,
                "total_logs": 0,
                "error_logs": 0,
                "critical_logs": 0
            },
            "severity_distribution": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "category_distribution": {},
            "source_analysis": {},
            "hourly_trends": {},
            "log_statistics": {"total": 0, "by_severity": {}, "by_source": {}, "security_relevant": 0, "last_minute": 0},
            "recent_alerts": [],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting realtime stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get realtime stats: {str(e)}")

@router.get("/attack-timeline")
async def get_attack_timeline(
    time_range: str = Query("24h"),
    severity_filter: Optional[str] = Query(None)
):
    """Get attack timeline data for charts"""
    try:
        from app.services.real_data_generator import data_generator
        
        alerts = data_generator.get_recent_alerts(200)
        
        # Filter by time range and severity
        now = datetime.utcnow()
        time_delta = timedelta(hours=24) if time_range == "24h" else timedelta(hours=168)  # 1 week
        
        filtered_alerts = []
        for alert in alerts:
            try:
                alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
                if (now - alert_time) <= time_delta:
                    if not severity_filter or alert.get('severity') == severity_filter:
                        filtered_alerts.append(alert)
            except:
                continue
        
        # Create timeline buckets
        buckets = 24 if time_range == "24h" else 168  # hourly buckets
        timeline_data = []
        
        for i in range(buckets):
            bucket_time = now - timedelta(hours=buckets - i - 1)
            bucket_start = bucket_time.replace(minute=0, second=0, microsecond=0)
            bucket_end = bucket_start + timedelta(hours=1)
            
            bucket_alerts = []
            for alert in filtered_alerts:
                try:
                    alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
                    if bucket_start <= alert_time < bucket_end:
                        bucket_alerts.append(alert)
                except:
                    continue
            
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for alert in bucket_alerts:
                severity = alert.get('severity', 'low')
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            timeline_data.append({
                "timestamp": bucket_start.isoformat(),
                "total": len(bucket_alerts),
                "severity_breakdown": severity_counts,
                "categories": list(set([a.get('category', 'unknown') for a in bucket_alerts]))
            })
        
        return {
            "timeline": timeline_data,
            "time_range": time_range,
            "total_alerts": len(filtered_alerts),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting attack timeline: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get attack timeline: {str(e)}")

def _get_top_threats(category_stats):
    """Get top threat categories"""
    if not category_stats:
        return []
    
    sorted_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)
    return [{"category": cat, "count": count} for cat, count in sorted_categories[:5]]

@router.get("/entity-network")
async def get_entity_network(
    entity_type: Optional[str] = Query(None),
    max_nodes: int = Query(500),
    layout_algorithm: str = Query("force_directed")
):
    """Get entity relationship network visualization - REAL DATA ONLY"""
    try:
        from app.services.network_monitor import network_monitor
        
        # Extract entities from real network monitor data
        entities_map = {}
        for alert in network_monitor.memory_alerts:
            for entity in alert.get("entities", []):
                entity_value = entity.get("value", "")
                entity_type_val = entity.get("type", "unknown")
                
                if entity_value and entity_type_val:
                    if entity_value not in entities_map:
                        entities_map[entity_value] = {
                            "id": f"entity_{len(entities_map) + 1}",
                            "value": entity_value,
                            "type": entity_type_val,
                            "risk_level": "medium",
                            "connections": [],
                            "last_seen": alert.get("timestamp", datetime.utcnow().isoformat())
                        }
        
        entity_list = list(entities_map.values())
        
        # Apply type filter if specified
        if entity_type:
            entity_list = [e for e in entity_list if e.get("type") == entity_type.lower()]
        
        # Limit results
        entity_list = entity_list[:max_nodes]
        
        entity_data = {"entities": entity_list}
        
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

@router.get("/data-generator-status")
async def get_data_generator_status():
    """Get status of the real-time data generator"""
    try:
        from app.services.real_data_generator import data_generator
        from app.services.network_monitor import network_monitor
        from app.services.log_streamer import log_streamer
        
        status = {
            "data_generator": {
                "active": data_generator.active,
                "generated_alerts": len(data_generator.generated_alerts),
                "statistics": data_generator.get_alert_statistics()
            },
            "network_monitor": {
                "active": network_monitor.monitoring_active,
                "memory_alerts": len(network_monitor.memory_alerts),
                "recent_alerts": network_monitor.memory_alerts[-5:] if network_monitor.memory_alerts else []
            },
            "log_streamer": {
                "active": log_streamer.active,
                "generated_logs": len(log_streamer.generated_logs),
                "statistics": log_streamer.get_log_statistics()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting data generator status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get data generator status: {str(e)}")

@router.get("/generated-alerts")
async def get_generated_alerts():
    """Get alerts from the real-time data generator"""
    try:
        from app.services.real_data_generator import data_generator
        
        # Get recent alerts from data generator
        alerts = data_generator.get_recent_alerts(100)
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "source": "data_generator",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting generated alerts: {e}")
        return {
            "alerts": [],
            "count": 0,
            "error": str(e)
        }

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
