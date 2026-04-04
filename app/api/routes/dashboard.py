from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime

router = APIRouter()

@router.get("/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics"""
    try:
        # Mock data for demo
        return {
            "alerts": {
                "total": 125,
                "new": 15,
                "investigating": 8,
                "resolved": 102
            },
            "correlations": {
                "total": 45,
                "active": 12
            },
            "reputation": {
                "total_entities": 892,
                "malicious": 67,
                "suspicious": 134
            },
            "threats": {
                "total": 23,
                "critical": 3,
                "high": 8,
                "medium": 12
            },
            "system": {
                "uptime": 86400,
                "processing_rate": 98.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")

@router.get("/trends")
async def get_dashboard_trends():
    """Get dashboard trend data"""
    try:
        # Mock trend data
        return {
            "alert_trends": [
                {"hour": "00:00", "count": 5},
                {"hour": "01:00", "count": 3},
                {"hour": "02:00", "count": 7},
                {"hour": "03:00", "count": 2},
                {"hour": "04:00", "count": 4},
                {"hour": "05:00", "count": 8},
                {"hour": "06:00", "count": 12},
                {"hour": "07:00", "count": 15},
                {"hour": "08:00", "count": 18},
                {"hour": "09:00", "count": 22},
                {"hour": "10:00", "count": 19},
                {"hour": "11:00", "count": 25}
            ],
            "severity_distribution": {
                "critical": 8,
                "high": 15,
                "medium": 32,
                "low": 70
            },
            "category_distribution": {
                "malware": 25,
                "phishing": 18,
                "intrusion": 12,
                "ddos": 8,
                "policy_violation": 15,
                "anomaly": 47
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard trends: {str(e)}")
