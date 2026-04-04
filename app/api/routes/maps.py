from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from datetime import datetime

router = APIRouter()

@router.get("/threats/summary")
async def get_threats_summary():
    """Get threats summary for dashboard"""
    try:
        # Mock summary data
        summary = {
            "total_threats": 45,
            "critical_threats": 8,
            "high_threats": 15,
            "medium_threats": 12,
            "low_threats": 10,
            "top_countries": [
                {"country": "United States", "count": 18},
                {"country": "United Kingdom", "count": 12},
                {"country": "Japan", "count": 8}
            ],
            "top_categories": [
                {"category": "malware", "count": 25},
                {"category": "phishing", "count": 18},
                {"category": "intrusion", "count": 12}
            ],
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
        # Mock threat data for map
        threat_data = [
            {
                "id": "threat_001",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "city": "New York",
                "country": "United States",
                "severity": "high",
                "category": "malware",
                "alert_count": 5,
                "timestamp": datetime.utcnow()
            },
            {
                "id": "threat_002",
                "latitude": 51.5074,
                "longitude": -0.1278,
                "city": "London",
                "country": "United Kingdom", 
                "severity": "medium",
                "category": "phishing",
                "alert_count": 3,
                "timestamp": datetime.utcnow()
            },
            {
                "id": "threat_003",
                "latitude": 35.6762,
                "longitude": 139.6503,
                "city": "Tokyo",
                "country": "Japan",
                "severity": "critical",
                "category": "intrusion",
                "alert_count": 8,
                "timestamp": datetime.utcnow()
            },
            {
                "id": "threat_004",
                "latitude": -33.8688,
                "longitude": 151.2093,
                "city": "Sydney",
                "country": "Australia",
                "severity": "low",
                "category": "policy_violation",
                "alert_count": 2,
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Apply filters
        if filter_type == "critical":
            threat_data = [t for t in threat_data if t["severity"] == "critical"]
        elif filter_type == "recent":
            threat_data = threat_data[:2]  # Recent threats
        
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

@router.get("/statistics")
async def get_geographic_statistics():
    """Get geographic threat statistics"""
    try:
        # Mock statistics
        return {
            "countries": {
                "United States": {"threat_count": 45, "severity": "high"},
                "United Kingdom": {"threat_count": 23, "severity": "medium"},
                "Japan": {"threat_count": 18, "severity": "critical"},
                "Germany": {"threat_count": 12, "severity": "medium"},
                "Australia": {"threat_count": 8, "severity": "low"},
                "Canada": {"threat_count": 7, "severity": "low"},
                "France": {"threat_count": 6, "severity": "medium"},
                "Brazil": {"threat_count": 5, "severity": "high"}
            },
            "regions": {
                "North America": {"threat_count": 52, "percentage": 38.2},
                "Europe": {"threat_count": 41, "percentage": 30.1},
                "Asia": {"threat_count": 25, "percentage": 18.4},
                "Oceania": {"threat_count": 8, "percentage": 5.9},
                "South America": {"threat_count": 5, "percentage": 3.7},
                "Africa": {"threat_count": 5, "percentage": 3.7}
            },
            "top_cities": [
                {"city": "New York", "threat_count": 18},
                {"city": "London", "threat_count": 12},
                {"city": "Tokyo", "threat_count": 10},
                {"city": "Berlin", "threat_count": 7},
                {"city": "Sydney", "threat_count": 6}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get geographic statistics: {str(e)}")
