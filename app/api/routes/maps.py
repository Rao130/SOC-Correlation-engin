"""
Maps API Routes
Provides geographic threat intelligence and mapping data
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.logging import logger
from app.services.geo_threat_mapper import geo_threat_mapper

router = APIRouter()

@router.get("/threats/summary")
async def get_threats_summary():
    """Get threats summary for dashboard"""
    try:
        # Get real threat statistics
        stats = geo_threat_mapper.get_threat_statistics()
        
        summary = {
            "total_threats": stats.get("total", 0),
            "critical_threats": stats.get("by_severity", {}).get("critical", 0),
            "high_threats": stats.get("by_severity", {}).get("high", 0),
            "medium_threats": stats.get("by_severity", {}).get("medium", 0),
            "low_threats": stats.get("by_severity", {}).get("low", 0),
            "top_countries": [{"country": country, "count": count} for country, count in stats.get("by_country", {}).items()][:10],
            "top_categories": [{"category": category, "count": count} for category, count in stats.get("by_type", {}).items()][:10],
            "timestamp": datetime.utcnow()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threats summary: {str(e)}")

@router.get("/threats")
async def get_threat_map_data(
    filter_type: str = Query("all"),
    time_range: str = Query("24h")
):
    """Get threat data for map visualization"""
    try:
        # Get real threat data
        threats = geo_threat_mapper.get_active_threats(100)
        
        # Convert to map format
        threat_data = []
        for threat in threats:
            location = threat.get('location', {})
            map_threat = {
                "id": threat.get('id', 'unknown'),
                "latitude": location.get('latitude', 0),
                "longitude": location.get('longitude', 0),
                "city": location.get('city', 'Unknown'),
                "country": location.get('country', 'Unknown'),
                "severity": threat.get('severity', 'unknown'),
                "category": threat.get('threat_type', 'unknown'),
                "alert_count": threat.get('affected_assets', 1),
                "threat_actor": threat.get('threat_actor', 'Unknown'),
                "confidence": threat.get('confidence', 0),
                "timestamp": datetime.fromisoformat(threat.get('first_seen', datetime.utcnow().isoformat()).replace('Z', '+00:00'))
            }
            threat_data.append(map_threat)
        
        # Apply filters
        if filter_type == "critical":
            threat_data = [t for t in threat_data if t["severity"] == "critical"]
        elif filter_type == "high":
            threat_data = [t for t in threat_data if t["severity"] == "high"]
        elif filter_type == "recent":
            # Get threats from last 6 hours
            cutoff = datetime.utcnow() - timedelta(hours=6)
            threat_data = [t for t in threat_data if t["timestamp"] > cutoff]
        
        return {
            "threats": threat_data,
            "total": len(threat_data),
            "filter": filter_type,
            "time_range": time_range
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat map data: {str(e)}")

@router.get("/clusters")
async def get_threat_clusters():
    """Get geographic threat clusters"""
    try:
        # Mock cluster data
        clusters = [
            {
                "id": "cluster_001",
                "center": {"latitude": 40.7128, "longitude": -74.0060},
                "radius": 500,  # km
                "threat_count": 15,
                "severity_distribution": {
                    "critical": 3,
                    "high": 5,
                    "medium": 4,
                    "low": 3
                },
                "countries": ["United States", "Canada"],
                "cities": ["New York", "Boston", "Toronto"]
            },
            {
                "id": "cluster_002",
                "center": {"latitude": 51.5074, "longitude": -0.1278},
                "radius": 300,
                "threat_count": 8,
                "severity_distribution": {
                    "critical": 1,
                    "high": 2,
                    "medium": 3,
                    "low": 2
                },
                "countries": ["United Kingdom", "France", "Germany"],
                "cities": ["London", "Paris", "Berlin"]
            }
        ]
        
        return {
            "clusters": clusters,
            "total": len(clusters)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat clusters: {str(e)}")

@router.get("/heatmap")
async def get_threat_heatmap(hours: int = Query(24, ge=1, le=168)):
    """Get threat heatmap data"""
    try:
        heatmap_data = geo_threat_mapper.get_threat_heatmap_data(hours)
        return heatmap_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat heatmap: {str(e)}")

@router.get("/actors")
async def get_top_threat_actors(limit: int = Query(10, ge=1, le=50)):
    """Get top threat actors by activity"""
    try:
        actors = geo_threat_mapper.get_top_threat_actors(limit)
        return {
            "actors": actors,
            "total": len(actors),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get threat actors: {str(e)}")

@router.post("/generate")
async def generate_threats(count: int = Query(5, ge=1, le=50)):
    """Generate new geographic threats"""
    try:
        threats = await geo_threat_mapper.generate_threat_burst(count)
        return {
            "message": f"Generated {count} geographic threats",
            "threats": threats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate threats: {str(e)}")

@router.get("/statistics")
async def get_geographic_statistics():
    """Get geographic threat statistics"""
    try:
        # Get real statistics from threat mapper
        stats = geo_threat_mapper.get_threat_statistics()
        
        # Calculate regions based on countries
        region_mapping = {
            "North America": ["United States", "Canada"],
            "Europe": ["United Kingdom", "Germany", "France"],
            "Asia": ["Japan", "China", "India", "Russia"],
            "South America": ["Brazil"],
            "Oceania": ["Australia"]
        }
        
        region_stats = {}
        total_threats = stats.get("total", 0)
        
        for region, countries in region_mapping.items():
            region_count = sum(stats.get("by_country", {}).get(country, 0) for country in countries)
            region_stats[region] = {
                "threat_count": region_count,
                "percentage": (region_count / total_threats * 100) if total_threats > 0 else 0
            }
        
        return {
            "countries": {
                country: {"threat_count": count, "severity": "high" if count > 10 else "medium" if count > 5 else "low"}
                for country, count in stats.get("by_country", {}).items()
            },
            "regions": region_stats,
            "top_cities": [
                {"city": f"City {i}", "threat_count": count}
                for i, count in enumerate(sorted(stats.get("by_country", {}).values(), reverse=True)[:5], 1)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get geographic statistics: {str(e)}")
