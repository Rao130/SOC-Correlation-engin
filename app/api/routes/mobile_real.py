"""
Mobile API endpoints - Real-time data only, no mock data
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.logging import logger

router = APIRouter()

@router.get("/alerts")
async def get_mobile_alerts(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum alerts to return"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back")
):
    """Get real alerts optimized for mobile display"""
    try:
        # Fetch real alerts from database
        db = await get_db()
        if not db:
            return {"alerts": [], "total": 0}
        
        alerts_collection = db.get_collection("alerts")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Build query
        query = {"timestamp": {"$gte": start_time, "$lte": end_time}}
        if severity:
            query["severity"] = severity
        if status:
            query["status"] = status
        
        # Query real alerts
        cursor = alerts_collection.find(query).sort("timestamp", -1).limit(limit)
        alerts = await cursor.to_list()
        
        # Convert to mobile format
        mobile_alerts = []
        for alert in alerts:
            mobile_alert = {
                "_id": str(alert.get("_id", "")),
                "title": alert.get("title", "Unknown Alert"),
                "description": alert.get("description", "No description available"),
                "severity": alert.get("severity", "medium"),
                "status": alert.get("status", "new"),
                "source": alert.get("source", "Unknown"),
                "timestamp": alert.get("timestamp", datetime.utcnow().isoformat()),
                "location": alert.get("raw_data", {}).get("target_asset", "Unknown"),
                "user": alert.get("raw_data", {}).get("user_name", "Unknown"),
                "hostname": alert.get("raw_data", {}).get("target_asset", "Unknown"),
                "actions": ["investigate", "acknowledge"],
                "priority": 1 if alert.get("severity") == "critical" else 2,
                "requires_action": alert.get("severity") in ["critical", "high"]
            }
            mobile_alerts.append(mobile_alert)
        
        return {
            "alerts": mobile_alerts,
            "total": len(mobile_alerts),
            "query_params": {
                "limit": limit,
                "severity": severity,
                "status": status,
                "hours": hours
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting mobile alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/stats")
async def get_mobile_stats(hours: int = Query(default=24, ge=1, le=168)):
    """Get real alert statistics for mobile dashboard"""
    try:
        # Fetch real stats from database
        db = await get_db()
        if not db:
            return {
                "total_alerts": 0,
                "critical_alerts": 0,
                "high_alerts": 0,
                "medium_alerts": 0,
                "low_alerts": 0,
                "new_alerts": 0,
                "investigating_alerts": 0,
                "resolved_alerts": 0
            }
        
        alerts_collection = db.get_collection("alerts")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get total alerts
        total_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time}
        })
        
        # Get alerts by severity
        critical_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "severity": "critical"
        })
        
        high_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "severity": "high"
        })
        
        medium_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "severity": "medium"
        })
        
        low_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "severity": "low"
        })
        
        # Get alerts by status
        new_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "status": "new"
        })
        
        investigating_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "status": "investigating"
        })
        
        resolved_alerts = await alerts_collection.count_documents({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "status": "resolved"
        })
        
        return {
            "total_alerts": total_alerts,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "medium_alerts": medium_alerts,
            "low_alerts": low_alerts,
            "new_alerts": new_alerts,
            "investigating_alerts": investigating_alerts,
            "resolved_alerts": resolved_alerts,
            "period_hours": hours,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting mobile stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/notifications")
async def get_mobile_notifications(limit: int = Query(default=10, ge=1, le=50)):
    """Get real notifications for mobile"""
    try:
        # Fetch real recent alerts as notifications
        db = await get_db()
        if not db:
            return {"notifications": []}
        
        alerts_collection = db.get_collection("alerts")
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=6)  # Last 6 hours
        
        # Get recent critical and high alerts
        cursor = alerts_collection.find({
            "timestamp": {"$gte": start_time, "$lte": end_time},
            "severity": {"$in": ["critical", "high"]}
        }).sort("timestamp", -1).limit(limit)
        
        alerts = await cursor.to_list()
        
        # Convert to notification format
        notifications = []
        for alert in alerts:
            notification = {
                "id": str(alert.get("_id", "")),
                "title": f"{alert.get('severity', 'medium').title()}: {alert.get('title', 'Alert')}",
                "message": alert.get("description", "No description available"),
                "severity": alert.get("severity", "medium"),
                "timestamp": alert.get("timestamp", datetime.utcnow().isoformat()),
                "read": False,
                "type": "alert",
                "action_required": alert.get("severity") == "critical"
            }
            notifications.append(notification)
        
        return {
            "notifications": notifications,
            "unread_count": len(notifications),
            "total_count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting mobile notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")
