from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.database import get_db
from app.core.logging import setup_logging

logger = setup_logging()

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "soc_correlation_engine"

router = APIRouter()

class CorrelationCreate(BaseModel):
    name: str
    description: str
    correlation_type: str
    alert_ids: List[str]
    entities: List[Dict[str, Any]]
    correlation_score: float
    confidence: float

class CorrelationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

@router.post("/analyze", response_model=Dict[str, Any])
async def run_correlation_analysis(
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Run correlation analysis on alerts"""
    try:
        file_db = db.get_database()
        alerts_collection = file_db.alerts
        correlation_collection = file_db.correlation_groups
        
        # Get recent alerts (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_alerts = []
        
        try:
            recent_alerts = await alerts_collection.find({
                "timestamp": {"$gte": yesterday}
            }).to_list()
        except Exception as db_error:
            logger.warning(f"Failed to get recent alerts: {db_error}")
        
        if len(recent_alerts) < 2:
            return {
                "message": "Not enough alerts for correlation analysis",
                "correlations_found": 0,
                "alerts_analyzed": len(recent_alerts)
            }
        
        # Trigger background correlation analysis
        background_tasks.add_task(perform_correlation_analysis, recent_alerts)
        
        return {
            "message": "Correlation analysis started",
            "alerts_analyzed": len(recent_alerts),
            "estimated_correlations": "Processing..."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start correlation analysis: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
async def get_correlations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    correlation_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """Get correlation groups with filtering"""
    try:
        file_db = db.get_database()
        
        if file_db is not None:
            collection = file_db.correlation_groups
            
            # Build query
            query = {}
            if correlation_type:
                query["correlation_type"] = correlation_type
            if status:
                query["status"] = status
            if search:
                query["$or"] = [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"description": {"$regex": search, "$options": "i"}}
                ]
            
            # Get data from database
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            correlations = await cursor.to_list()
            
            # Convert ObjectId to string for JSON serialization
            def convert_objectid(obj):
                if hasattr(obj, '__iter__') and not isinstance(obj, str):
                    if isinstance(obj, dict):
                        return {k: convert_objectid(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_objectid(item) for item in obj]
                elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                    return str(obj)
                return obj
            
            correlations = [convert_objectid(correlation) for correlation in correlations]
            
            return correlations
        else:
            return []
        
    except Exception as e:
        logger.error(f"Failed to get correlations: {e}")
        return []

@router.get("/{correlation_id}", response_model=Dict[str, Any])
async def get_correlation_by_id(
    correlation_id: str,
    db = Depends(get_db)
):
    """Get specific correlation by ID"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        # Try to get from database
        correlation = await collection.find_one({"_id": correlation_id})
        
        if correlation:
            # Convert ObjectId to string for JSON serialization
            def convert_objectid(obj):
                if hasattr(obj, '__iter__') and not isinstance(obj, str):
                    if isinstance(obj, dict):
                        return {k: convert_objectid(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_objectid(item) for item in obj]
                elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                    return str(obj)
                return obj
            
            return convert_objectid(correlation)
        else:
            raise HTTPException(status_code=404, detail="Correlation not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get correlation: {str(e)}")

@router.post("/", response_model=Dict[str, Any])
async def create_correlation(
    correlation: CorrelationCreate,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Create a new correlation group"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        # Create correlation document
        correlation_data = {
            "_id": f"corr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "name": correlation.name,
            "description": correlation.description,
            "correlation_type": correlation.correlation_type,
            "correlation_score": correlation.correlation_score,
            "confidence": correlation.confidence,
            "status": "active",
            "alert_ids": correlation.alert_ids,
            "entities": correlation.entities,
            "alert_count": len(correlation.alert_ids),
            "entity_count": len(correlation.entities),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "notes": correlation.description
        }
        
        # Insert into database
        result = await collection.insert_one(correlation_data)
        
        return {
            "message": "Correlation created successfully",
            "correlation_id": str(result.inserted_id),
            "name": correlation.name,
            "correlation_score": correlation.correlation_score
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create correlation: {str(e)}")

@router.patch("/{correlation_id}", response_model=Dict[str, Any])
async def update_correlation(
    correlation_id: str,
    update: CorrelationUpdate,
    db = Depends(get_db)
):
    """Update correlation status or notes"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        if update.status:
            update_data["status"] = update.status
        if update.notes:
            update_data["notes"] = update.notes
        
        # Update correlation
        result = await collection.update_one(
            {"_id": correlation_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Correlation not found")
        
        return {"message": "Correlation updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update correlation: {str(e)}")

@router.delete("/{correlation_id}", response_model=Dict[str, Any])
async def delete_correlation(
    correlation_id: str,
    db = Depends(get_db)
):
    """Delete a correlation"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        result = await collection.delete_one({"_id": correlation_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Correlation not found")
        
        return {"message": "Correlation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete correlation: {str(e)}")

async def perform_correlation_analysis(alerts: List[Dict[str, Any]]):
    """Background task to perform correlation analysis"""
    try:
        # Mock correlation analysis logic
        await asyncio.sleep(2)  # Simulate processing time
        
        # Create sample correlations
        correlations = [
            {
                "name": f"Auto-Correlation - {len(alerts)} Alerts",
                "description": f"Automatically correlated {len(alerts)} alerts",
                "correlation_type": "pattern_based",
                "correlation_score": 75.0,
                "confidence": 80,
                "status": "active",
                "alert_ids": [str(alert.get("_id", f"alert_{i}")) for i, alert in enumerate(alerts)],
                "entities": [alert.get("source_ip", "unknown") for alert in alerts[:5] if alert.get("source_ip")],
                "created_at": datetime.utcnow().isoformat(),
                "alert_count": len(alerts)
            }
        ]
        
        # Save to database
        client = AsyncIOMotorClient(MONGODB_URL)
        db = client[DATABASE_NAME]
        correlation_collection = db.correlation_groups
        
        for correlation in correlations:
            await correlation_collection.insert_one(correlation)
        
        client.close()
        logger.info(f"Created {len(correlations)} correlation groups from analysis")
        
    except Exception as e:
        logger.error(f"Error in correlation analysis: {e}")
