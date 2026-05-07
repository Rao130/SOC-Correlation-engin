"""
User Behavior Analytics (UBA) API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.uba_engine import uba_engine, BehaviorType, RiskLevel
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class BehaviorEvent(BaseModel):
    user_id: str = Field(..., description="User identifier")
    timestamp: datetime = Field(..., description="Event timestamp")
    behavior_type: str = Field(..., description="Type of behavior")
    action: str = Field(..., description="Action performed")
    resource: str = Field(..., description="Resource accessed")
    source_ip: str = Field(..., description="Source IP address")
    device: str = Field(..., description="Device used")
    location: str = Field(..., description="Location of access")
    success: bool = Field(default=True, description="Was the action successful")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class UserRiskQuery(BaseModel):
    user_id: str = Field(..., description="User ID to analyze")
    days: int = Field(default=30, ge=1, le=365, description="Analysis period in days")

@router.post("/events/process")
async def process_behavior_event(
    event: BehaviorEvent,
    current_user: dict = Depends(get_current_user)
):
    """Process a single behavior event"""
    try:
        # Convert to dict for processing
        event_dict = {
            'user_id': event.user_id,
            'timestamp': event.timestamp.isoformat(),
            'behavior_type': event.behavior_type,
            'action': event.action,
            'resource': event.resource,
            'source_ip': event.source_ip,
            'device': event.device,
            'location': event.location,
            'success': event.success,
            'metadata': event.metadata
        }
        
        # Process event
        anomaly = await uba_engine.process_behavior_event(event_dict)
        
        if anomaly:
            return {
                "status": "success",
                "message": "Behavior event processed with anomaly detected",
                "anomaly": {
                    "id": anomaly.id,
                    "user_id": anomaly.user_id,
                    "timestamp": anomaly.timestamp.isoformat(),
                    "behavior_type": anomaly.behavior_type.value,
                    "anomaly_type": anomaly.anomaly_type,
                    "risk_level": anomaly.risk_level.value,
                    "risk_score": anomaly.risk_score,
                    "description": anomaly.description,
                    "details": anomaly.details
                }
            }
        else:
            return {
                "status": "success",
                "message": "Behavior event processed normally",
                "anomaly": None
            }
    except Exception as e:
        logger.error(f"Error processing behavior event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/batch")
async def process_behavior_events(
    events: List[BehaviorEvent],
    current_user: dict = Depends(get_current_user)
):
    """Process multiple behavior events"""
    try:
        results = []
        anomalies_detected = 0
        
        for event in events:
            event_dict = {
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'behavior_type': event.behavior_type,
                'action': event.action,
                'resource': event.resource,
                'source_ip': event.source_ip,
                'device': event.device,
                'location': event.location,
                'success': event.success,
                'metadata': event.metadata
            }
            
            anomaly = await uba_engine.process_behavior_event(event_dict)
            
            result = {
                "user_id": event.user_id,
                "timestamp": event.timestamp.isoformat(),
                "processed": True,
                "anomaly_detected": anomaly is not None
            }
            
            if anomaly:
                result["anomaly"] = {
                    "id": anomaly.id,
                    "anomaly_type": anomaly.anomaly_type,
                    "risk_level": anomaly.risk_level.value,
                    "risk_score": anomaly.risk_score,
                    "description": anomaly.description
                }
                anomalies_detected += 1
            
            results.append(result)
        
        return {
            "status": "success",
            "message": f"Processed {len(events)} behavior events",
            "total_events": len(events),
            "anomalies_detected": anomalies_detected,
            "results": results
        }
    except Exception as e:
        logger.error(f"Error processing behavior events batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/risk")
async def get_user_risk_analysis(
    user_id: str,
    days: int = Query(default=30, ge=1, le=365, description="Analysis period in days"),
    current_user: dict = Depends(get_current_user)
):
    """Get risk analysis for a specific user"""
    try:
        risk_analysis = await uba_engine.analyze_user_risk(user_id, days)
        
        return {
            "status": "success",
            "risk_analysis": risk_analysis
        }
    except Exception as e:
        logger.error(f"Error getting user risk analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}/patterns")
async def get_user_patterns(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get learned behavior patterns for a user"""
    try:
        patterns = uba_engine.get_user_patterns(user_id)
        
        return {
            "status": "success",
            "patterns": patterns
        }
    except Exception as e:
        logger.error(f"Error getting user patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/anomalies")
async def get_recent_anomalies(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    risk_level: Optional[str] = Query(default=None, description="Filter by risk level"),
    user_id: Optional[str] = Query(default=None, description="Filter by user ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get recent behavior anomalies"""
    try:
        anomalies = uba_engine.get_recent_anomalies(hours, risk_level, user_id)
        
        return {
            "status": "success",
            "anomalies": anomalies,
            "total": len(anomalies),
            "filters": {
                "hours": hours,
                "risk_level": risk_level,
                "user_id": user_id
            }
        }
    except Exception as e:
        logger.error(f"Error getting recent anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_uba_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get UBA dashboard data"""
    try:
        # Get organization risk overview
        org_risk = await uba_engine.get_organization_risk_overview()
        
        # Get recent anomalies (last 24 hours)
        recent_anomalies = uba_engine.get_recent_anomalies(24)
        
        # Calculate dashboard metrics
        total_anomalies = len(recent_anomalies)
        critical_anomalies = len([a for a in recent_anomalies if a['risk_level'] == 'critical'])
        high_anomalies = len([a for a in recent_anomalies if a['risk_level'] == 'high'])
        medium_anomalies = len([a for a in recent_anomalies if a['risk_level'] == 'medium'])
        
        # Get top risk users
        user_risk_counts = {}
        for anomaly in recent_anomalies:
            user_id = anomaly['user_id']
            if user_id not in user_risk_counts:
                user_risk_counts[user_id] = {'total': 0, 'critical': 0, 'high': 0}
            user_risk_counts[user_id]['total'] += 1
            if anomaly['risk_level'] == 'critical':
                user_risk_counts[user_id]['critical'] += 1
            elif anomaly['risk_level'] == 'high':
                user_risk_counts[user_id]['high'] += 1
        
        # Sort users by risk (critical first, then high, then total)
        top_risk_users = sorted(
            user_risk_counts.items(),
            key=lambda x: (x[1]['critical'], x[1]['high'], x[1]['total']),
            reverse=True
        )[:10]
        
        # Get anomaly type distribution
        anomaly_types = {}
        for anomaly in recent_anomalies:
            anomaly_type = anomaly['anomaly_type']
            anomaly_types[anomaly_type] = anomaly_types.get(anomaly_type, 0) + 1
        
        # Get behavior type distribution
        behavior_types = {}
        for anomaly in recent_anomalies:
            behavior_type = anomaly['behavior_type']
            behavior_types[behavior_type] = behavior_types.get(behavior_type, 0) + 1
        
        return {
            "status": "success",
            "dashboard": {
                "summary": {
                    "total_anomalies": total_anomalies,
                    "critical_anomalies": critical_anomalies,
                    "high_anomalies": high_anomalies,
                    "medium_anomalies": medium_anomalies,
                    "low_anomalies": total_anomalies - critical_anomalies - high_anomalies - medium_anomalies,
                    "high_risk_users": org_risk.get('high_risk_users', 0),
                    "total_monitored_users": org_risk.get('total_users', 0)
                },
                "organization_risk": org_risk,
                "top_risk_users": [
                    {
                        "user_id": user_id,
                        "total_anomalies": risk_data['total'],
                        "critical_anomalies": risk_data['critical'],
                        "high_anomalies": risk_data['high']
                    }
                    for user_id, risk_data in top_risk_users
                ],
                "anomaly_distribution": {
                    "by_type": anomaly_types,
                    "by_behavior": behavior_types,
                    "by_risk_level": {
                        "critical": critical_anomalies,
                        "high": high_anomalies,
                        "medium": medium_anomalies,
                        "low": total_anomalies - critical_anomalies - high_anomalies - medium_anomalies
                    }
                },
                "recent_critical_anomalies": [
                    anomaly for anomaly in recent_anomalies
                    if anomaly['risk_level'] in ['critical', 'high']
                ][:10],
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting UBA dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_uba_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get UBA statistics"""
    try:
        # Get organization risk overview
        org_risk = await uba_engine.get_organization_risk_overview()
        
        # Get anomalies for different time periods
        last_24h = uba_engine.get_recent_anomalies(24)
        last_7d = uba_engine.get_recent_anomalies(24 * 7)
        last_30d = uba_engine.get_recent_anomalies(24 * 30)
        
        # Calculate trend data
        daily_anomalies = {}
        for anomaly in last_7d:
            date = anomaly['timestamp'][:10]  # Extract date part
            daily_anomalies[date] = daily_anomalies.get(date, 0) + 1
        
        # Risk level trends
        risk_trends = {
            '24h': {
                'critical': len([a for a in last_24h if a['risk_level'] == 'critical']),
                'high': len([a for a in last_24h if a['risk_level'] == 'high']),
                'medium': len([a for a in last_24h if a['risk_level'] == 'medium']),
                'low': len([a for a in last_24h if a['risk_level'] == 'low'])
            },
            '7d': {
                'critical': len([a for a in last_7d if a['risk_level'] == 'critical']),
                'high': len([a for a in last_7d if a['risk_level'] == 'high']),
                'medium': len([a for a in last_7d if a['risk_level'] == 'medium']),
                'low': len([a for a in last_7d if a['risk_level'] == 'low'])
            },
            '30d': {
                'critical': len([a for a in last_30d if a['risk_level'] == 'critical']),
                'high': len([a for a in last_30d if a['risk_level'] == 'high']),
                'medium': len([a for a in last_30d if a['risk_level'] == 'medium']),
                'low': len([a for a in last_30d if a['risk_level'] == 'low'])
            }
        }
        
        # Anomaly type trends
        anomaly_type_trends = {}
        for anomaly in last_7d:
            anomaly_type = anomaly['anomaly_type']
            anomaly_type_trends[anomaly_type] = anomaly_type_trends.get(anomaly_type, 0) + 1
        
        # User activity stats
        user_activity = {}
        for anomaly in last_7d:
            user_id = anomaly['user_id']
            user_activity[user_id] = user_activity.get(user_id, 0) + 1
        
        most_active_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "status": "success",
            "stats": {
                "overview": org_risk,
                "anomaly_counts": {
                    "last_24h": len(last_24h),
                    "last_7d": len(last_7d),
                    "last_30d": len(last_30d)
                },
                "risk_trends": risk_trends,
                "daily_anomalies": daily_anomalies,
                "anomaly_type_trends": anomaly_type_trends,
                "most_active_users": [
                    {
                        "user_id": user_id,
                        "anomaly_count": count
                    }
                    for user_id, count in most_active_users
                ],
                "total_patterns": len(uba_engine.behavior_patterns),
                "total_alerts": len(uba_engine.anomaly_alerts)
            }
        }
    except Exception as e:
        logger.error(f"Error getting UBA stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/behavior-types")
async def get_behavior_types(current_user: dict = Depends(get_current_user)):
    """Get available behavior types"""
    try:
        behavior_types = [
            {
                "value": bt.value,
                "name": bt.value.replace("_", " ").title(),
                "description": f"User {bt.value.replace('_', ' ')} activities"
            }
            for bt in BehaviorType
        ]
        
        return {
            "status": "success",
            "behavior_types": behavior_types,
            "total": len(behavior_types)
        }
    except Exception as e:
        logger.error(f"Error getting behavior types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-levels")
async def get_risk_levels(current_user: dict = Depends(get_current_user)):
    """Get available risk levels"""
    try:
        risk_levels = [
            {
                "value": rl.value,
                "name": rl.value.title(),
                "description": f"{rl.value.title()} risk level for user behavior anomalies"
            }
            for rl in RiskLevel
        ]
        
        return {
            "status": "success",
            "risk_levels": risk_levels,
            "total": len(risk_levels)
        }
    except Exception as e:
        logger.error(f"Error getting risk levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def list_monitored_users(
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum number of users"),
    current_user: dict = Depends(get_current_user)
):
    """List monitored users"""
    try:
        # Get unique users from patterns and anomalies
        pattern_users = set()
        for pattern_key in uba_engine.behavior_patterns.keys():
            user_id = pattern_key.split('_')[0]
            pattern_users.add(user_id)
        
        anomaly_users = set()
        for alert in uba_engine.anomaly_alerts:
            anomaly_users.add(alert.user_id)
        
        all_users = pattern_users.union(anomaly_users)
        
        # Get risk analysis for each user (simplified)
        user_list = []
        for user_id in list(all_users)[:limit]:
            # Get recent anomalies for this user
            user_anomalies = uba_engine.get_recent_anomalies(24 * 7, user_id=user_id)
            
            # Calculate basic risk metrics
            total_anomalies = len(user_anomalies)
            high_risk_anomalies = len([a for a in user_anomalies if a['risk_level'] in ['high', 'critical']])
            
            # Determine risk level
            if high_risk_anomalies > 0:
                risk_level = 'high'
            elif total_anomalies > 5:
                risk_level = 'medium'
            else:
                risk_level = 'low'
            
            user_list.append({
                "user_id": user_id,
                "total_anomalies": total_anomalies,
                "high_risk_anomalies": high_risk_anomalies,
                "risk_level": risk_level,
                "last_activity": max([a['timestamp'] for a in user_anomalies]) if user_anomalies else None
            })
        
        # Sort by risk (high risk first)
        user_list.sort(key=lambda x: (x['risk_level'] == 'high', x['risk_level'] == 'medium', x['total_anomalies']), reverse=True)
        
        return {
            "status": "success",
            "users": user_list,
            "total": len(user_list)
        }
    except Exception as e:
        logger.error(f"Error listing monitored users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/anomalies/{anomaly_id}")
async def delete_anomaly(
    anomaly_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an anomaly (for false positives)"""
    try:
        # Find and remove the anomaly
        initial_count = len(uba_engine.anomaly_alerts)
        uba_engine.anomaly_alerts = [
            alert for alert in uba_engine.anomaly_alerts
            if alert.id != anomaly_id
        ]
        
        if len(uba_engine.anomaly_alerts) == initial_count:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        return {
            "status": "success",
            "message": f"Anomaly {anomaly_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting anomaly: {e}")
        raise HTTPException(status_code=500, detail=str(e))
