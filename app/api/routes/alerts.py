from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio

from app.core.database import get_db
from app.core.logging import logger
from app.models.alert import AlertCreate, AlertUpdate, AlertResponse, AlertDocument
try:
    from app.services.alert_processor import AlertProcessor
    alert_processor = AlertProcessor()
except ImportError as e:
    logger.warning(f"AlertProcessor not available: {e}")
    alert_processor = None

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
        
        # Trigger background processing if available
        if alert_processor:
            background_tasks.add_task(
                process_alert_background,
                alert_doc.dict()
            )
        
        return alert_doc.to_response()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
@router.get("", response_model=List[Dict[str, Any]])
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
        # First try to get data from database (has proper MongoDB _id)
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
                
                # Get alerts from database with proper MongoDB _id
                cursor = collection.find(query)
                
                # Apply sorting
                if sort_by == "timestamp":
                    cursor = cursor.sort("timestamp", -1 if sort_order == "desc" else 1)
                elif sort_by == "severity":
                    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                    # For database, we'll handle severity sorting after retrieval
                    pass
                
                # Get alerts and convert to proper format
                db_alerts = []
                async for alert_doc in cursor:
                    # Convert MongoDB document to dict and ensure _id is string
                    alert_dict = dict(alert_doc)
                    alert_dict['_id'] = str(alert_doc['_id'])  # Convert ObjectId to string
                    db_alerts.append(alert_dict)
                
                # Apply additional sorting if needed
                if sort_by == "severity":
                    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                    reverse_order = sort_order == "desc"
                    db_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 1), reverse=reverse_order)
                elif sort_by == "criticality_score":
                    reverse_order = sort_order == "desc"
                    db_alerts.sort(key=lambda x: x.get('criticality_score', 0), reverse=reverse_order)
                
                # Apply pagination
                paginated_alerts = db_alerts[skip:skip + limit]
                
                logger.info(f"Returning {len(paginated_alerts)} alerts from database (total: {len(db_alerts)})")
                return paginated_alerts
                
            except Exception as e:
                logger.error(f"Database error: {e}")
                # Fall back to memory data if database fails
        
        # Fallback to memory data if database not available
        from app.services.real_data_generator import data_generator
        from app.services.network_monitor import network_monitor
        
        # Combine alerts from both generators
        all_alerts = []
        
        # Get alerts from data generator
        if hasattr(data_generator, 'generated_alerts') and data_generator.generated_alerts:
            all_alerts.extend(data_generator.generated_alerts)
        
        # Get alerts from network monitor
        if hasattr(network_monitor, 'memory_alerts') and network_monitor.memory_alerts:
            all_alerts.extend(network_monitor.memory_alerts)
        
        # If we have in-memory data, use it
        if all_alerts:
            # Apply filters
            filtered_alerts = all_alerts
            
            if severity:
                filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity]
            if status:
                filtered_alerts = [a for a in filtered_alerts if a.get('status') == status]
            if category:
                filtered_alerts = [a for a in filtered_alerts if a.get('category') == category]
            if search:
                search_lower = search.lower()
                filtered_alerts = [a for a in filtered_alerts 
                                 if search_lower in a.get('title', '').lower() or 
                                    search_lower in a.get('description', '').lower()]
            
            # Sort alerts
            reverse_order = sort_order == "desc"
            if sort_by == "timestamp":
                def get_timestamp(alert):
                    ts = alert.get('timestamp', '')
                    if isinstance(ts, str):
                        try:
                            # Handle different timestamp formats
                            if ts.endswith('Z'):
                                ts = ts.replace('Z', '+00:00')
                            return datetime.fromisoformat(ts)
                        except:
                            return datetime.min
                    elif isinstance(ts, datetime):
                        return ts
                    else:
                        return datetime.min
                
                filtered_alerts.sort(key=get_timestamp, reverse=reverse_order)
            elif sort_by == "severity":
                severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
                filtered_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 1), reverse=reverse_order)
            elif sort_by == "criticality_score":
                filtered_alerts.sort(key=lambda x: x.get('criticality_score', 0), reverse=reverse_order)
            
            # Apply pagination
            paginated_alerts = filtered_alerts[skip:skip + limit]
            
            logger.info(f"Returning {len(paginated_alerts)} alerts from memory (total: {len(filtered_alerts)})")
            return paginated_alerts
        
        # Fallback to database if no in-memory data
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
                def get_db_timestamp(alert):
                    ts = alert.get('timestamp', '')
                    if isinstance(ts, str):
                        try:
                            # Handle different timestamp formats
                            if ts.endswith('Z'):
                                ts = ts.replace('Z', '+00:00')
                            return datetime.fromisoformat(ts)
                        except:
                            return datetime.min
                    elif isinstance(ts, datetime):
                        return ts
                    else:
                        return datetime.min
                
                filtered_alerts.sort(key=get_db_timestamp, reverse=True)
                
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
        
        # Convert string ID to ObjectId for MongoDB query
        from bson import ObjectId
        
        try:
            object_id = ObjectId(alert_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid alert ID format")
        
        alert = await collection.find_one({"_id": object_id})
        
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
        
        # Convert string ID to ObjectId for MongoDB query
        from bson import ObjectId
        
        try:
            object_id = ObjectId(alert_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid alert ID format")
        
        # Check if alert exists
        existing_alert = await collection.find_one({"_id": object_id})
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
            {"_id": object_id},
            {"$set": update_data}
        )
        
        # Get updated alert
        updated_alert = await collection.find_one({"_id": object_id})
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
        if alert_processor:
            # Process alert with AlertProcessor if available
            await alert_processor.process_alert(alert)
        else:
            # Fallback processing
            await asyncio.sleep(1)
            logger.info(f"Basic alert processing completed: {alert.get('alert_id', 'unknown')}")
    except Exception as e:
        logger.error(f"Failed to process alert: {e}")
