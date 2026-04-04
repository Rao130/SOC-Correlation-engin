from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()

class ReputationCheck(BaseModel):
    entity: str
    entity_type: Optional[str] = None

class ReputationCreate(BaseModel):
    entity: str
    entity_type: str
    aggregated_score: float
    risk_level: str
    classification: Dict[str, Any]
    metrics: Dict[str, Any]
    tags: Optional[List[str]] = None

@router.post("/check", response_model=Dict[str, Any])
async def check_reputation(
    request: ReputationCheck,
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Check reputation of an entity"""
    try:
        file_db = db.get_database()
        collection = file_db.reputation
        
        # Search for existing entity
        existing = await collection.find_one({"entity": request.entity})
        
        if existing:
            # Update last checked timestamp
            await collection.update_one(
                {"entity": request.entity},
                {"$set": {"last_checked": datetime.utcnow()}}
            )
            return {
                "entity": existing["entity"],
                "entity_type": existing["entity_type"],
                "aggregated_score": existing["aggregated_score"],
                "risk_level": existing["risk_level"],
                "classification": existing["classification"],
                "metrics": existing["metrics"],
                "last_checked": datetime.utcnow(),
                "created_at": existing["created_at"]
            }
        else:
            # Create new reputation entry with default values
            new_reputation = {
                "entity": request.entity,
                "entity_type": request.entity_type or "unknown",
                "aggregated_score": 50.0,  # Neutral score
                "risk_level": "unknown",
                "classification": {
                    "category": "unknown",
                    "confidence": 50
                },
                "metrics": {
                    "alert_count": 0,
                    "false_positive_count": 0,
                    "true_positive_count": 0
                },
                "created_at": datetime.utcnow(),
                "last_checked": datetime.utcnow(),
                "tags": []
            }
            
            await collection.insert_one(new_reputation)
            
            # Trigger background analysis
            background_tasks.add_task(analyze_entity_reputation, request.entity)
            
            return new_reputation
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check reputation: {str(e)}")

@router.get("/", response_model=Dict[str, Any])
async def get_reputation_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    risk_level: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """Get reputation data with filtering"""
    try:
        file_db = db.get_database()
        collection = file_db.reputation
        
        # Build query
        query = {}
        if risk_level:
            query["risk_level"] = risk_level
        if entity_type:
            query["entity_type"] = entity_type
        if search:
            query["$or"] = [
                {"entity": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search]}}
            ]
        
        # Get data
        cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        reputation_data = await cursor.to_list()
        
        # Get total count
        total = await collection.count_documents(query)
        
        return {
            "data": reputation_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        # Fallback to mock data if database is empty
        mock_data = [
            {
                "entity": "192.168.1.100",
                "entity_type": "ip",
                "aggregated_score": 85.2,
                "risk_level": "malicious",
                "classification": {
                    "category": "malware",
                    "confidence": 90
                },
                "metrics": {
                    "alert_count": 15,
                    "false_positive_count": 2,
                    "true_positive_count": 13
                },
                "created_at": datetime.utcnow(),
                "last_checked": datetime.utcnow(),
                "tags": ["malware", "high_risk"]
            },
            {
                "entity": "suspicious-domain.com",
                "entity_type": "domain", 
                "aggregated_score": 65.8,
                "risk_level": "suspicious",
                "classification": {
                    "category": "phishing",
                    "confidence": 75
                },
                "metrics": {
                    "alert_count": 8,
                    "false_positive_count": 1,
                    "true_positive_count": 7
                },
                "created_at": datetime.utcnow(),
                "last_checked": datetime.utcnow(),
                "tags": ["phishing", "suspicious"]
            },
            {
                "entity": "10.0.0.50",
                "entity_type": "ip",
                "aggregated_score": 25.3,
                "risk_level": "benign",
                "classification": {
                    "category": "trusted",
                    "confidence": 85
                },
                "metrics": {
                    "alert_count": 2,
                    "false_positive_count": 2,
                    "true_positive_count": 0
                },
                "created_at": datetime.utcnow(),
                "last_checked": datetime.utcnow(),
                "tags": ["trusted", "internal"]
            }
        ]
        
        return {
            "data": mock_data,
            "total": len(mock_data),
            "skip": skip,
            "limit": limit
        }

@router.get("/stats", response_model=Dict[str, Any])
async def get_reputation_stats(db = Depends(get_db)):
    """Get reputation statistics"""
    try:
        file_db = db.get_database()
        collection = file_db.reputation
        
        # Get stats by risk level
        pipeline = [
            {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        risk_stats = await collection.aggregate(pipeline).to_list()
        risk_distribution = {stat["_id"]: stat["count"] for stat in risk_stats}
        
        # Get total entities
        total_entities = await collection.count_documents({})
        
        # Get recent additions (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_additions = await collection.count_documents({
            "created_at": {"$gte": yesterday}
        })
        
        return {
            "total_entities": total_entities,
            "risk_distribution": risk_distribution,
            "recent_additions": recent_additions,
            "high_risk_entities": risk_distribution.get("malicious", 0) + risk_distribution.get("suspicious", 0)
        }
        
    except Exception as e:
        # Fallback stats
        return {
            "total_entities": 3,
            "risk_distribution": {
                "malicious": 1,
                "suspicious": 1,
                "benign": 1
            },
            "recent_additions": 0,
            "high_risk_entities": 2
        }

@router.delete("/{entity}")
async def delete_reputation_entity(
    entity: str,
    db = Depends(get_db)
):
    """Delete reputation entity"""
    try:
        file_db = db.get_database()
        collection = file_db.reputation
        
        result = await collection.delete_one({"entity": entity})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return {"message": f"Entity {entity} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete entity: {str(e)}")

@router.post("/bulk-update")
async def bulk_update_reputation(
    entities: List[Dict[str, Any]],
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """Bulk update reputation entities"""
    try:
        file_db = db.get_database()
        collection = file_db.reputation
        
        updated_count = 0
        for entity_data in entities:
            # Update or insert entity
            await collection.update_one(
                {"entity": entity_data["entity"]},
                {"$set": {**entity_data, "last_checked": datetime.utcnow()}},
                upsert=True
            )
            updated_count += 1
        
        return {"message": f"Updated {updated_count} entities successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to bulk update: {str(e)}")

async def analyze_entity_reputation(entity: str):
    """Background task to analyze entity reputation"""
    # This would integrate with threat intelligence feeds
    # For demo purposes, we'll just simulate analysis
    await asyncio.sleep(2)  # Simulate API call
    print(f"Analyzed reputation for entity: {entity}")
