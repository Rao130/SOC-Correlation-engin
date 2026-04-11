from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import logging

from app.core.database import get_db
from app.core.logging import setup_logging
from app.models.reputation import ReputationCreate, ReputationUpdate, ReputationResponse

logger = setup_logging()

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
        
        if file_db is not None:
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
                    "last_checked": existing.get("last_checked"),
                    "status": "found"
                }
            else:
                # Create new reputation entry
                new_reputation = {
                    "entity": request.entity,
                    "entity_type": request.entity_type or "unknown",
                    "aggregated_score": 0.0,
                    "risk_level": "unknown",
                    "classification": {},
                    "metrics": {},
                    "tags": [],
                    "created_at": datetime.utcnow(),
                    "last_checked": datetime.utcnow(),
                    "status": "new"
                }
                
                await collection.insert_one(new_reputation)
                
                # Trigger background analysis
                background_tasks.add_task(analyze_entity_reputation, request.entity)
                
                return new_reputation
        else:
            return {"error": "Database not connected"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check reputation: {str(e)}")

@router.get("/", response_model=List[Dict[str, Any]])
async def get_reputation_data(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    entity_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db = Depends(get_db)
):
    """Get reputation data with filtering and pagination"""
    try:
        file_db = db.get_database()
        
        if file_db is not None:
            collection = file_db.reputation
            
            # Build query
            query = {}
            if entity_type:
                query["entity_type"] = entity_type
            if risk_level:
                query["risk_level"] = risk_level
            if search:
                query["$or"] = [
                    {"entity": {"$regex": search, "$options": "i"}},
                    {"classification.category": {"$regex": search, "$options": "i"}}
                ]
            
            # Get data from database
            cursor = collection.find(query).sort("last_checked", -1).skip(skip).limit(limit)
            reputation_data = await cursor.to_list()
            
            # Convert ObjectId to string for JSON serialization
            for item in reputation_data:
                if "_id" in item:
                    item["_id"] = str(item["_id"])
                # Convert any nested ObjectIds
                for key, value in item.items():
                    if hasattr(value, '__str__') and 'ObjectId' in str(type(value)):
                        item[key] = str(value)
            
            return reputation_data
        else:
            return []
        
    except Exception as e:
        logger.error(f"Failed to get reputation data: {e}")
        return []

@router.get("/stats", response_model=Dict[str, Any])
async def get_reputation_stats(db = Depends(get_db)):
    """Get reputation statistics"""
    try:
        file_db = db.get_database()
        
        if file_db is not None:
            collection = file_db.reputation
            
            # Get total count
            total_count = await collection.count_documents({})
            
            # Get counts by risk level
            risk_levels = await collection.aggregate([
                {"$group": {"_id": "$risk_level", "count": {"$sum": 1}}}
            ]).to_list()
            
            # Get counts by entity type
            entity_types = await collection.aggregate([
                {"$group": {"_id": "$entity_type", "count": {"$sum": 1}}}
            ]).to_list()
            
            return {
                "total_entities": total_count,
                "risk_levels": {item["_id"]: item["count"] for item in risk_levels},
                "entity_types": {item["_id"]: item["count"] for item in entity_types},
                "last_updated": datetime.utcnow().isoformat()
            }
        else:
            return {"error": "Database not connected"}
        
    except Exception as e:
        logger.error(f"Failed to get reputation stats: {e}")
        return {"error": str(e)}

async def analyze_entity_reputation(entity: str):
    """Background task to analyze entity reputation"""
    try:
        # This would integrate with external APIs
        # For now, just log the analysis request
        logger.info(f"Analyzing reputation for entity: {entity}")
        await asyncio.sleep(2)  # Simulate analysis time
        logger.info(f"Reputation analysis completed for: {entity}")
    except Exception as e:
        logger.error(f"Failed to analyze entity reputation: {e}")

import asyncio
