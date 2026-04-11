from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.core.database import get_db
from app.core.logging import setup_logging
from app.models.alert import AlertCreate, AlertUpdate, AlertResponse, AlertDocument
from app.services.alert_processor import AlertProcessor

logger = setup_logging()

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

@router.get("/", response_model=List[Dict[str, Any]])
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
        file_db = db.get_database()
        
        # Handle different database types
        if file_db is not None:
            try:
                collection = file_db.alerts
                
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
                        {"description": {"$regex": search, "$options": "i"}}
                    ]
                
                # Get data from database
                alerts = []
                try:
                    cursor = collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
                    alerts = await cursor.to_list()
                    
                    # Convert ObjectId to string for JSON serialization
                    for alert in alerts:
                        if "_id" in alert:
                            alert["_id"] = str(alert["_id"])
                        # Convert any nested ObjectIds
                        for key, value in alert.items():
                            if hasattr(value, '__str__') and 'ObjectId' in str(type(value)):
                                alert[key] = str(value)
                        
                except Exception as db_error:
                    logger.warning(f"Database query failed: {db_error}")
                    alerts = []
                
                return alerts
                
            except AttributeError:
                # Fallback for file-based database
                alerts_data = file_db.alerts.data if hasattr(file_db.alerts, 'data') else file_db.alerts
                
                # Apply filters
                filtered_alerts = alerts_data
                if severity:
                    filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity]
                if status:
                    filtered_alerts = [a for a in filtered_alerts if a.get('status') == status]
                if category:
                    filtered_alerts = [a for a in filtered_alerts if a.get('category') == category]
                if search:
                    search_lower = search.lower()
                    filtered_alerts = [a for a in filtered_alerts if search_lower in a.get('title', '').lower() or search_lower in a.get('description', '').lower()]
                
                # Sort by timestamp (newest first)
                filtered_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Pagination
                paginated_alerts = filtered_alerts[skip:skip + limit]
                
                return paginated_alerts
        else:
            return []
        
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        return []

@router.get("/{alert_id}", response_model=Dict[str, Any])
async def get_alert(alert_id: str, db = Depends(get_db)):
    """Get a specific alert by ID"""
    try:
        file_db = db.get_database()
        collection = file_db.alerts
        
        alert = await collection.find_one({"_id": alert_id})
        
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        alert["_id"] = str(alert["_id"])
        return alert
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alert: {str(e)}")

@router.patch("/{alert_id}", response_model=Dict[str, Any])
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db = Depends(get_db)
):
    """Update an alert"""
    try:
        file_db = db.get_database()
        collection = file_db.alerts
        
        # Check if alert exists
        existing_alert = await collection.find_one({"_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Build update document
        update_data = alert_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        # If status is being updated, set resolved_at for resolved alerts
        if alert_update.status and alert_update.status == "resolved":
            update_data["resolved_at"] = datetime.utcnow()
        
        # Update alert
        await collection.update_one(
            {"_id": alert_id},
            {"$set": update_data}
        )
        
        # Get updated alert
        updated_alert = await collection.find_one({"_id": alert_id})
        updated_alert["_id"] = str(updated_alert["_id"])
        
        return updated_alert
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update alert: {str(e)}")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, db = Depends(get_db)):
    """Delete an alert"""
    try:
        file_db = db.get_database()
        collection = file_db.alerts
        
        result = await collection.delete_one({"_id": alert_id})
        
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
        file_db = db.get_database()
        collection = file_db.alerts
        
        # Check if alert exists
        existing_alert = await collection.find_one({"_id": alert_id})
        if not existing_alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Add note
        note_data = {
            "content": note.get("content", ""),
            "author": note.get("author", "system"),
            "timestamp": datetime.utcnow(),
            "type": note.get("type", "general")
        }
        
        await collection.update_one(
            {"_id": alert_id},
            {
                "$push": {"notes": note_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {"message": "Note added successfully", "note": note_data}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add note: {str(e)}")

async def process_alert_background(alert: Dict[str, Any]):
    """Background task to process alert"""
    try:
        # This would implement alert processing logic
        await asyncio.sleep(1)
        logger.info(f"Processed alert: {alert.get('id', 'unknown')}")
    except Exception as e:
        logger.error(f"Failed to process alert: {e}")
