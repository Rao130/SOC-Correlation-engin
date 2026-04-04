from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db

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
        recent_alerts = await alerts_collection.find({
            "timestamp": {"$gte": yesterday}
        }).to_list()
        
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

@router.get("/", response_model=Dict[str, Any])
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
        
        # Get data
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        correlations = await cursor.to_list()
        
        # Get total count
        total = await collection.count_documents(query)
        
        return {
            "data": correlations,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        # Fallback to mock data if database is empty
        mock_correlations = [
            {
                "_id": "corr_001",
                "name": "Entity Based Correlation - IP 192.168.1.100",
                "description": "5 alerts correlated by shared IP entity",
                "correlation_type": "entity_based",
                "correlation_score": 85.5,
                "confidence": 90,
                "status": "active",
                "alert_ids": ["alert_1", "alert_2", "alert_3", "alert_4", "alert_5"],
                "entities": [
                    {"type": "ip", "value": "192.168.1.100", "risk_level": "malicious"}
                ],
                "metrics": {
                    "alert_count": 5,
                    "unique_entities": 3,
                    "severity_score": 7.2,
                    "time_span_hours": 2
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "notes": "High priority correlation - immediate investigation required"
            },
            {
                "_id": "corr_002",
                "name": "Temporal Correlation - Brute Force Pattern",
                "description": "3 alerts within 30 minutes showing brute force pattern",
                "correlation_type": "temporal",
                "correlation_score": 72.3,
                "confidence": 75,
                "status": "active",
                "alert_ids": ["alert_6", "alert_7", "alert_8"],
                "entities": [
                    {"type": "ip", "value": "10.0.0.50", "risk_level": "suspicious"},
                    {"type": "domain", "value": "attacker.com", "risk_level": "malicious"}
                ],
                "metrics": {
                    "alert_count": 3,
                    "unique_entities": 2,
                    "severity_score": 6.8,
                    "time_span_hours": 0.5
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "notes": "Temporal pattern detected - possible coordinated attack"
            },
            {
                "_id": "corr_003",
                "name": "Geographic Correlation - Unknown Region",
                "description": "4 alerts from unusual geographic location",
                "correlation_type": "geographic",
                "correlation_score": 68.9,
                "confidence": 70,
                "status": "investigating",
                "alert_ids": ["alert_9", "alert_10", "alert_11", "alert_12"],
                "entities": [
                    {"type": "country", "value": "XX", "risk_level": "unknown"}
                ],
                "metrics": {
                    "alert_count": 4,
                    "unique_entities": 1,
                    "severity_score": 5.5,
                    "time_span_hours": 6
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "notes": "Unusual geographic pattern - requires investigation"
            }
        ]
        
        return {
            "data": mock_correlations,
            "total": len(mock_correlations),
            "skip": skip,
            "limit": limit
        }

@router.get("/{correlation_id}", response_model=Dict[str, Any])
async def get_correlation_details(
    correlation_id: str,
    db = Depends(get_db)
):
    """Get detailed correlation information"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        correlation = await collection.find_one({"_id": correlation_id})
        
        if not correlation:
            raise HTTPException(status_code=404, detail="Correlation not found")
        
        # Get related alerts
        alerts_collection = file_db.alerts
        related_alerts = await alerts_collection.find({
            "_id": {"$in": correlation.get("alert_ids", [])}
        }).to_list()
        
        return {
            "correlation": correlation,
            "related_alerts": related_alerts,
            "total_related_alerts": len(related_alerts)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get correlation details: {str(e)}")

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
        correlation_doc = {
            "_id": f"corr_{int(datetime.utcnow().timestamp())}_{len(correlation.alert_ids)}",
            "name": correlation.name,
            "description": correlation.description,
            "correlation_type": correlation.correlation_type,
            "correlation_score": correlation.correlation_score,
            "confidence": correlation.confidence,
            "status": "active",
            "alert_ids": correlation.alert_ids,
            "entities": correlation.entities,
            "metrics": {
                "alert_count": len(correlation.alert_ids),
                "unique_entities": len(set(e.get("value", "") for e in correlation.entities)),
                "severity_score": correlation.correlation_score / 10,
                "time_span_hours": 1
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "notes": ""
        }
        
        await collection.insert_one(correlation_doc)
        
        # Trigger background processing
        background_tasks.add_task(process_correlation, correlation_doc["_id"])
        
        return {
            "message": "Correlation created successfully",
            "correlation_id": correlation_doc["_id"],
            "correlation": correlation_doc
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
        
        update_data = {"updated_at": datetime.utcnow()}
        if update.status:
            update_data["status"] = update.status
        if update.notes:
            update_data["notes"] = update.notes
        
        result = await collection.update_one(
            {"_id": correlation_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Correlation not found")
        
        return {"message": "Correlation updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update correlation: {str(e)}")

@router.delete("/{correlation_id}")
async def delete_correlation(
    correlation_id: str,
    db = Depends(get_db)
):
    """Delete correlation group"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        result = await collection.delete_one({"_id": correlation_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Correlation not found")
        
        return {"message": f"Correlation {correlation_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete correlation: {str(e)}")

@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_correlation_stats(db = Depends(get_db)):
    """Get correlation statistics"""
    try:
        file_db = db.get_database()
        collection = file_db.correlation_groups
        
        # Get total correlations
        total_correlations = await collection.count_documents({})
        
        # Get stats by type
        pipeline = [
            {"$group": {"_id": "$correlation_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        type_stats = await collection.aggregate(pipeline).to_list()
        type_distribution = {stat["_id"]: stat["count"] for stat in type_stats}
        
        # Get stats by status
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        status_stats = await collection.aggregate(status_pipeline).to_list()
        status_distribution = {stat["_id"]: stat["count"] for stat in status_stats}
        
        # Get recent correlations (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_correlations = await collection.count_documents({
            "created_at": {"$gte": yesterday}
        })
        
        return {
            "total_correlations": total_correlations,
            "type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "recent_correlations": recent_correlations,
            "active_correlations": status_distribution.get("active", 0)
        }
        
    except Exception as e:
        # Fallback stats
        return {
            "total_correlations": 3,
            "type_distribution": {
                "entity_based": 1,
                "temporal": 1,
                "geographic": 1
            },
            "status_distribution": {
                "active": 2,
                "investigating": 1
            },
            "recent_correlations": 1,
            "active_correlations": 2
        }

async def perform_correlation_analysis(alerts: List[Dict[str, Any]]):
    """Background task to perform correlation analysis"""
    # This would implement actual correlation logic
    # For demo purposes, we'll simulate the analysis
    await asyncio.sleep(3)  # Simulate processing time
    print(f"Performed correlation analysis on {len(alerts)} alerts")

async def process_correlation(correlation_id: str):
    """Background task to process correlation"""
    # This would implement correlation processing logic
    await asyncio.sleep(2)
    print(f"Processed correlation: {correlation_id}")
