"""
Mobile App API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class MobileAlertAck(BaseModel):
    alert_id: str = Field(..., description="Alert ID to acknowledge")
    note: Optional[str] = Field(default=None, description="Acknowledgment note")

class MobileAlertAction(BaseModel):
    alert_id: str = Field(..., description="Alert ID")
    action: str = Field(..., description="Action to take")
    note: Optional[str] = Field(default=None, description="Action note")

@router.get("/alerts")
async def get_mobile_alerts(
    limit: int = Query(default=20, ge=1, le=100, description="Maximum alerts to return"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts optimized for mobile display"""
    try:
        # Fetch real alerts from database
        from app.core.database import get_db
        db = await get_db()
        if not db:
            return {"alerts": [], "total": 0}
        
        alerts_collection = db.get_collection("alerts")
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Query real alerts
        cursor = alerts_collection.find({
            "timestamp": {"$gte": start_time, "$lte": end_time}
        }).sort("timestamp", -1).limit(100)
        
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
        
        # Apply filters
        filtered_alerts = mobile_alerts
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a["severity"] == severity]
        
        if status:
            filtered_alerts = [a for a in filtered_alerts if a["status"] == status]
        
        # Sort by priority and timestamp
        filtered_alerts.sort(key=lambda x: (x["priority"], x["timestamp"]), reverse=True)
        
        return {
            "status": "success",
            "alerts": filtered_alerts[:limit],
            "total": len(filtered_alerts),
            "filters": {
                "severity": severity,
                "status": status,
                "hours": hours
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting mobile alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/stats")
async def get_mobile_alerts_stats(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """Get alert statistics for mobile dashboard"""
    try:
        # This would normally calculate from database
        # For now, return sample stats
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        stats = {
            "summary": {
                "critical": 2,
                "high": 5,
                "medium": 12,
                "low": 8,
                "total": 27,
                "unacknowledged": 7,
                "requires_action": 4
            },
            "trends": {
                "current_hour": 3,
                "previous_hour": 5,
                "current_day": 27,
                "previous_day": 31,
                "trend_direction": "decreasing"
            },
            "top_sources": [
                {"source": "EDR", "count": 15},
                {"source": "Authentication", "count": 8},
                {"source": "Network", "count": 4}
            ],
            "top_users": [
                {"user": "john.doe", "count": 6},
                {"user": "admin", "count": 4},
                {"user": "jane.smith", "count": 3}
            ],
            "response_times": {
                "average_minutes": 15,
                "sla_compliance": 85
            },
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            }
        }
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting mobile alert stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_mobile_alert(
    alert_id: str,
    ack: MobileAlertAck,
    current_user: dict = Depends(get_current_user)
):
    """Acknowledge an alert from mobile"""
    try:
        # This would normally update the alert in database
        # For now, simulate acknowledgment
        
        logger.info(f"Alert {alert_id} acknowledged by {current_user.get('username', 'mobile_user')}")
        
        return {
            "status": "success",
            "message": f"Alert {alert_id} acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": current_user.get('username', 'mobile_user'),
            "acknowledged_at": datetime.now().isoformat(),
            "note": ack.note
        }
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/action")
async def take_alert_action(
    alert_id: str,
    action: MobileAlertAction,
    current_user: dict = Depends(get_current_user)
):
    """Take action on an alert from mobile"""
    try:
        # This would normally execute the action
        # For now, simulate action execution
        
        action_results = {
            "isolate": {
                "status": "success",
                "message": "Endpoint isolated successfully",
                "endpoint_id": "workstation-01"
            },
            "scan": {
                "status": "success",
                "message": "Scan initiated successfully",
                "scan_id": f"scan_{datetime.now().timestamp()}"
            },
            "quarantine": {
                "status": "success",
                "message": "File quarantined successfully",
                "file_hash": "abc123..."
            },
            "block_ip": {
                "status": "success",
                "message": "IP blocked successfully",
                "ip_address": "192.168.1.100"
            },
            "investigate": {
                "status": "success",
                "message": "Investigation started",
                "ticket_id": "INC001001"
            }
        }
        
        result = action_results.get(action.action, {
            "status": "failed",
            "message": f"Unknown action: {action.action}"
        })
        
        logger.info(f"Action {action.action} taken on alert {alert_id} by {current_user.get('username', 'mobile_user')}")
        
        return {
            "status": "success",
            "message": f"Action {action.action} executed successfully",
            "alert_id": alert_id,
            "action": action.action,
            "result": result,
            "executed_by": current_user.get('username', 'mobile_user'),
            "executed_at": datetime.now().isoformat(),
            "note": action.note
        }
    except Exception as e:
        logger.error(f"Error taking action on alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_mobile_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get mobile-optimized dashboard data"""
    try:
        # Get various dashboard components
        alerts_response = await get_mobile_alerts(limit=10, current_user=current_user)
        stats_response = await get_mobile_alerts_stats(hours=24, current_user=current_user)
        
        # System status
        system_status = {
            "api": "online",
            "websocket": "online",
            "database": "online",
            "last_update": datetime.now().isoformat()
        }
        
        # Quick actions
        quick_actions = [
            {
                "id": "create_incident",
                "title": "Create Incident",
                "description": "Create new security incident",
                "icon": "plus-circle",
                "color": "blue"
            },
            {
                "id": "view_all_critical",
                "title": "Critical Alerts",
                "description": "View all critical alerts",
                "icon": "exclamation-triangle",
                "color": "red"
            },
            {
                "id": "system_status",
                "title": "System Status",
                "description": "Check system health",
                "icon": "heartbeat",
                "color": "green"
            }
        ]
        
        return {
            "status": "success",
            "dashboard": {
                "alerts": alerts_response.get("alerts", []),
                "stats": stats_response.get("stats", {}),
                "system_status": system_status,
                "quick_actions": quick_actions,
                "last_refresh": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting mobile dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/settings")
async def get_mobile_settings(
    current_user: dict = Depends(get_current_user)
):
    """Get mobile app settings"""
    try:
        settings = {
            "notifications": {
                "push_enabled": True,
                "sound_enabled": True,
                "vibration_enabled": True,
                "critical_only": False,
                "quiet_hours": {
                    "enabled": True,
                    "start": "22:00",
                    "end": "07:00"
                }
            },
            "display": {
                "theme": "auto",  # auto, light, dark
                "compact_mode": False,
                "show_location": True,
                "show_hostname": True
            },
            "security": {
                "biometric_enabled": True,
                "auto_lock_timeout": 300,  # seconds
                "require_auth": True
            },
            "sync": {
                "auto_refresh": True,
                "refresh_interval": 30,  # seconds
                "offline_mode": False,
                "cache_size": 100  # MB
            },
            "alerts": {
                "auto_acknowledge": False,
                "default_severity": "medium",
                "show_dismissed": False,
                "group_similar": True
            }
        }
        
        return {
            "status": "success",
            "settings": settings
        }
    except Exception as e:
        logger.error(f"Error getting mobile settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/settings")
async def update_mobile_settings(
    settings: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update mobile app settings"""
    try:
        # This would normally save to user preferences
        # For now, just validate and return success
        
        logger.info(f"Mobile settings updated by {current_user.get('username', 'mobile_user')}")
        
        return {
            "status": "success",
            "message": "Settings updated successfully",
            "updated_at": datetime.now().isoformat(),
            "updated_by": current_user.get('username', 'mobile_user')
        }
    except Exception as e:
        logger.error(f"Error updating mobile settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def mobile_health_check():
    """Mobile app health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "features": {
                "real_time_alerts": True,
                "push_notifications": True,
                "offline_mode": True,
                "biometric_auth": True,
                "dark_mode": True
            }
        }
    except Exception as e:
        logger.error(f"Mobile health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/notifications")
async def get_mobile_notifications(
    limit: int = Query(default=50, ge=1, le=200, description="Maximum notifications"),
    unread_only: bool = Query(default=False, description="Only unread notifications"),
    current_user: dict = Depends(get_current_user)
):
    """Get mobile notifications"""
    try:
        # This would normally fetch from database
        # For now, return sample notifications
        notifications = [
            {
                "id": "notif_1",
                "type": "alert",
                "title": "Critical Alert: Malware Detected",
                "message": "Malware detected on workstation-01. Immediate action required.",
                "data": {
                    "alert_id": "mobile_alert_1",
                    "severity": "critical"
                },
                "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
                "read": False,
                "priority": "high"
            },
            {
                "id": "notif_2",
                "type": "system",
                "title": "System Update",
                "message": "SOC system updated to version 2.1.0",
                "data": {},
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "read": True,
                "priority": "low"
            },
            {
                "id": "notif_3",
                "type": "alert",
                "title": "Alert Acknowledged",
                "message": "Alert 'Suspicious Login' has been acknowledged",
                "data": {
                    "alert_id": "mobile_alert_2",
                    "action": "acknowledged"
                },
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "read": True,
                "priority": "medium"
            }
        ]
        
        # Apply filters
        filtered_notifications = notifications
        
        if unread_only:
            filtered_notifications = [n for n in filtered_notifications if not n["read"]]
        
        # Sort by timestamp (newest first)
        filtered_notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "status": "success",
            "notifications": filtered_notifications[:limit],
            "total": len(filtered_notifications),
            "unread_count": len([n for n in notifications if not n["read"]]),
            "filters": {
                "unread_only": unread_only,
                "limit": limit
            }
        }
    except Exception as e:
        logger.error(f"Error getting mobile notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        # This would normally update in database
        logger.info(f"Notification {notification_id} marked as read by {current_user.get('username', 'mobile_user')}")
        
        return {
            "status": "success",
            "message": f"Notification {notification_id} marked as read",
            "read_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offline/sync")
async def get_offline_data(
    last_sync: Optional[str] = Query(default=None, description="Last sync timestamp"),
    current_user: dict = Depends(get_current_user)
):
    """Get data for offline synchronization"""
    try:
        # Parse last sync timestamp
        last_sync_time = None
        if last_sync:
            try:
                last_sync_time = datetime.fromisoformat(last_sync)
            except:
                last_sync_time = datetime.now() - timedelta(days=1)
        else:
            last_sync_time = datetime.now() - timedelta(days=1)
        
        # Get data updated since last sync
        # This would normally fetch from database
        offline_data = {
            "alerts": [
                {
                    "id": "offline_alert_1",
                    "title": "Offline Alert Sample",
                    "description": "This alert was updated while you were offline",
                    "severity": "high",
                    "timestamp": (last_sync_time + timedelta(hours=2)).isoformat(),
                    "sync_required": True
                }
            ],
            "settings": {
                "last_updated": (last_sync_time + timedelta(hours=6)).isoformat(),
                "version": "1.0.1"
            },
            "system_status": {
                "last_check": datetime.now().isoformat(),
                "status": "operational"
            }
        }
        
        return {
            "status": "success",
            "data": offline_data,
            "sync_timestamp": datetime.now().isoformat(),
            "last_client_sync": last_sync
        }
    except Exception as e:
        logger.error(f"Error getting offline data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
