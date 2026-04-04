from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.core.database import get_db
from app.models.alert import AlertCreate, AlertUpdate, AlertResponse, AlertDocument
from app.services.alert_processor import AlertProcessor

router = APIRouter()

@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new security alert"""
    try:
        # Create alert document
        alert_doc = AlertDocument(
            title=alert.title,
            description=alert.description,
            severity=alert.severity,
            source=alert.source,
            category=alert.category,
            confidence=alert.confidence,
            entities=alert.entities,
            location=alert.location,
            context=alert.context,
            raw_data=alert.raw_data
        )
        
        # Calculate criticality score
        alert_doc.update_criticality_score()
        
        # Save to database
        file_db = db.get_database()  # Get file database instance
        alerts_collection = file_db.alerts  # Get alerts collection
        await alerts_collection.insert_one(alert_doc.dict())
        
        # Trigger background processing
        background_tasks.add_task(
            process_alert_background,
            alert_doc.dict()
        )
        
        return alert_doc.to_response()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
async def get_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    sort_by: str = Query("timestamp", regex="^(timestamp|severity|criticality_score)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """Get alerts with filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if severity:
            query["severity"] = severity
        if status:
            query["status"] = status
        if category:
            query["category"] = category
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"entities.value": {"$regex": search, "$options": "i"}}
            ]
        
        # Sort configuration
        sort_direction = 1 if sort_order == "asc" else -1
        sort_config = [(sort_by, sort_direction)]
        
        # Get alerts
        file_db = db.get_database()  # Get file database instance
        alerts_collection = file_db.alerts  # Get alerts collection
        alerts = await alerts_collection.find(query).sort(sort_config).skip(skip).limit(limit).to_list(length=None)
        
        # Get total count
        total = await alerts_collection.count_documents(query)
        
        # Convert to response models
        alert_responses = []
        for alert in alerts:
            alert_doc = AlertDocument(**alert)
            alert_responses.append(alert_doc.to_response())
        
        return {
            "data": alert_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": (skip + limit) < total
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(alert_id: str, db = Depends(get_db)):
    """Get a specific alert by ID"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        alert = await alerts_collection.find_one({"alert_id": alert_id})
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert_doc = AlertDocument(**alert)
        return alert_doc.to_response()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert: {str(e)}")

@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db = Depends(get_db)
):
    """Update an alert"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        
        # Check if alert exists
        existing_alert = await alerts_collection.find_one({"alert_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Build update document
        update_data = alert_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # If status is being updated, set resolved_at for resolved alerts
        if alert_update.status and alert_update.status == "resolved":
            update_data["resolved_at"] = datetime.utcnow()
        
        # Update alert
        await alerts_collection.update_one(
            {"alert_id": alert_id},
            {"$set": update_data}
        )
        
        # Get updated alert
        updated_alert = await alerts_collection.find_one({"alert_id": alert_id})
        alert_doc = AlertDocument(**updated_alert)
        
        # Recalculate criticality score if severity changed
        if alert_update.severity:
            alert_doc.update_criticality_score()
            await alerts_collection.update_one(
                {"alert_id": alert_id},
                {"$set": {"criticality_score": alert_doc.criticality_score}}
            )
        
        return alert_doc.to_response()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, db = Depends(get_db)):
    """Delete an alert"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        result = await alerts_collection.delete_one({"alert_id": alert_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {"message": "Alert deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete alert: {str(e)}")

@router.post("/{alert_id}/notes")
async def add_alert_note(
    alert_id: str,
    note: Dict[str, Any],
    db = Depends(get_db)
):
    """Add a note to an alert"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        
        # Check if alert exists
        existing_alert = await alerts_collection.find_one({"alert_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Create note
        new_note = {
            "user_id": note.get("user_id", "system"),
            "user_name": note.get("user_name", "System"),
            "note": note.get("note", ""),
            "timestamp": datetime.utcnow()
        }
        
        # Add note to alert
        await alerts_collection.update_one(
            {"alert_id": alert_id},
            {
                "$push": {"notes": new_note},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {"message": "Note added successfully", "note": new_note}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add note: {str(e)}")

@router.post("/{alert_id}/assign")
async def assign_alert(
    alert_id: str,
    assignment: Dict[str, Any],
    db = Depends(get_db)
):
    """Assign an alert to an analyst"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        
        # Check if alert exists
        existing_alert = await alerts_collection.find_one({"alert_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Create assignment
        assignment_data = {
            "user_id": assignment.get("user_id"),
            "user_name": assignment.get("user_name"),
            "assigned_at": datetime.utcnow()
        }
        
        # Update alert assignment
        await alerts_collection.update_one(
            {"alert_id": alert_id},
            {
                "$set": {
                    "assigned_to": assignment_data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Alert assigned successfully", "assignment": assignment_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to assign alert: {str(e)}")

@router.get("/stats/summary")
async def get_alert_stats(db = Depends(get_db)):
    """Get alert statistics summary"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        
        # Get counts by status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        status_counts = await alerts_collection.aggregate(status_pipeline).to_list(None)
        
        # Get counts by severity
        severity_pipeline = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        severity_counts = await alerts_collection.aggregate(severity_pipeline).to_list(None)
        
        # Get counts by category
        category_pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_counts = await alerts_collection.aggregate(category_pipeline).to_list(None)
        
        # Get recent trends (last 24 hours)
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        
        recent_pipeline = [
            {"$match": {"timestamp": {"$gte": day_ago}}},
            {"$group": {
                "_id": {"$dateTrunc": {"date": "$timestamp", "unit": "hour"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        recent_trends = await alerts_collection.aggregate(recent_pipeline).to_list(None)
        
        # Get fatigue metrics
        fatigue_pipeline = [
            {"$group": {
                "_id": None,
                "total_alerts": {"$sum": 1},
                "duplicate_count": {"$sum": "$fatigue_metrics.duplicate_count"},
                "suppression_count": {"$sum": "$fatigue_metrics.suppression_count"},
                "auto_resolve_count": {"$sum": "$fatigue_metrics.auto_resolve_count"},
                "avg_resolution_time": {"$avg": "$fatigue_metrics.average_resolution_time"}
            }}
        ]
        fatigue_metrics = await alerts_collection.aggregate(fatigue_pipeline).to_list(None)
        
        return {
            "status_counts": {item["_id"]: item["count"] for item in status_counts},
            "severity_counts": {item["_id"]: item["count"] for item in severity_counts},
            "category_counts": {item["_id"]: item["count"] for item in category_counts},
            "recent_trends": [
                {"hour": str(item["_id"]), "count": item["count"]} 
                for item in recent_trends
            ],
            "fatigue_metrics": fatigue_metrics[0] if fatigue_metrics else {
                "total_alerts": 0,
                "duplicate_count": 0,
                "suppression_count": 0,
                "auto_resolve_count": 0,
                "avg_resolution_time": 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert stats: {str(e)}")

@router.post("/bulk", response_model=List[AlertResponse])
async def create_bulk_alerts(
    alerts: List[AlertCreate],
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create multiple alerts in bulk"""
    try:
        created_alerts = []
        alerts_collection = db.get_mongodb_db().alerts
        
        for alert_data in alerts:
            # Create alert document
            alert_doc = AlertDocument(
                title=alert_data.title,
                description=alert_data.description,
                severity=alert_data.severity,
                source=alert_data.source,
                category=alert_data.category,
                confidence=alert_data.confidence,
                entities=alert_data.entities,
                location=alert_data.location,
                context=alert_data.context,
                raw_data=alert_data.raw_data
            )
            
            # Calculate criticality score
            alert_doc.update_criticality_score()
            
            # Save to database
            await alerts_collection.insert_one(alert_doc.dict())
            created_alerts.append(alert_doc.to_response())
            
            # Trigger background processing
            background_tasks.add_task(
                process_alert_background,
                alert_doc.dict()
            )
        
        return created_alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create bulk alerts: {str(e)}")

@router.post("/suppress/{alert_id}")
async def suppress_alert(
    alert_id: str,
    suppression: Dict[str, Any],
    db = Depends(get_db)
):
    """Suppress an alert (temporarily hide it)"""
    try:
        alerts_collection = db.get_mongodb_db().alerts
        
        # Check if alert exists
        existing_alert = await alerts_collection.find_one({"alert_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert status to suppressed
        await alerts_collection.update_one(
            {"alert_id": alert_id},
            {
                "$set": {
                    "status": "suppressed",
                    "suppression_reason": suppression.get("reason", ""),
                    "suppression_expires": suppression.get("expires_at"),
                    "updated_at": datetime.utcnow()
                },
                "$inc": {"fatigue_metrics.suppression_count": 1}
            }
        )
        
        return {"message": "Alert suppressed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to suppress alert: {str(e)}")

async def process_alert_background(alert_data: Dict[str, Any]):
    """Background task to process alert after creation"""
    try:
        # This would integrate with the AlertProcessor service
        # For now, we'll just log it
        print(f"Background processing alert: {alert_data['alert_id']}")
        
        # In a real implementation, this would:
        # 1. Check entity reputations
        # 2. Run correlation analysis
        # 3. Update fatigue metrics
        # 4. Send notifications if needed
        # 5. Update dashboard via WebSocket
        
    except Exception as e:
        print(f"Error in background alert processing: {e}")
