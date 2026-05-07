"""
Threat Intelligence API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.threat_intelligence import (
    threat_intel_manager, 
    ThreatType, 
    ThreatSeverity
)
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class ThreatIntelCredentials(BaseModel):
    provider: str = Field(..., description="Threat intelligence provider")
    credentials: Dict[str, Any] = Field(..., description="Provider credentials")

class IndicatorSearch(BaseModel):
    query: str = Field(..., description="Search query")
    indicator_type: Optional[str] = Field(default=None, description="Indicator type filter")
    hours: int = Field(default=24, ge=1, le=168, description="Hours to look back")

@router.post("/connectors/register")
async def register_threat_intel_connector(
    request: ThreatIntelCredentials,
    current_user: dict = Depends(get_current_user)
):
    """Register a threat intelligence connector"""
    try:
        provider = request.provider.lower()
        
        # Create appropriate connector
        if provider == "recorded_future":
            from app.services.threat_intelligence import RecordedFutureConnector
            connector = RecordedFutureConnector(request.credentials)
        elif provider == "mandiant":
            from app.services.threat_intelligence import MandiantConnector
            connector = MandiantConnector(request.credentials)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Authenticate connector
        auth_success = await connector.authenticate()
        if not auth_success:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Register connector
        threat_intel_manager.register_connector(provider, connector)
        
        return {
            "status": "success",
            "message": f"{provider.upper()} threat intelligence connector registered and authenticated successfully",
            "provider": provider
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering threat intelligence connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_threat_intel_connectors(current_user: dict = Depends(get_current_user)):
    """List registered threat intelligence connectors"""
    try:
        connectors = []
        
        for provider_name, source_config in threat_intel_manager.intelligence_sources.items():
            connectors.append({
                "provider": provider_name,
                "type": source_config.get('name', 'Unknown'),
                "last_sync": threat_intel_manager.cache.get(f'last_check_{provider_name}', None),
                "status": "enabled" if source_config.get('enabled', False) else "disabled"
            })
        
        return {
            "status": "success",
            "connectors": connectors,
            "total": len(connectors)
        }
    except Exception as e:
        logger.error(f"Error listing threat intelligence connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/indicators")
async def get_threat_indicators(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    threat_type: Optional[str] = Query(default=None, description="Filter by threat type"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    current_user: dict = Depends(get_current_user)
):
    """Get threat indicators from all providers"""
    try:
        if provider:
            if provider not in threat_intel_manager.intelligence_sources:
                raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
            
            # Get indicators from specific provider
            all_indicators = await threat_intel_manager.get_all_indicators(hours)
            provider_indicators = {provider: all_indicators.get(provider, [])}
        else:
            # Get indicators from all providers
            provider_indicators = await threat_intel_manager.get_all_indicators(hours)
        
        # Apply filters and convert to response format
        formatted_indicators = {}
        total_indicators = 0
        
        for prov_name, indicators in provider_indicators.items():
            filtered_indicators = indicators
            
            if threat_type:
                filtered_indicators = [
                    ind for ind in filtered_indicators
                    if ind.get("threat_type", "") == threat_type
                ]
            
            if severity:
                filtered_indicators = [
                    ind for ind in filtered_indicators
                    if ind.get("severity", "") == severity
                ]
            
            formatted_indicators[prov_name] = [
                {
                    "id": indicator.get("id", ""),
                    "indicator_type": indicator.get("indicator_type", ""),
                    "value": indicator.get("value", ""),
                    "threat_type": indicator.get("threat_type", ""),
                    "severity": indicator.get("severity", ""),
                    "confidence": indicator.get("confidence", 0.0),
                    "first_seen": indicator.get("first_seen", datetime.now()).isoformat() if indicator.get("first_seen") else datetime.now().isoformat(),
                    "last_seen": indicator.get("last_seen", datetime.now()).isoformat() if indicator.get("last_seen") else datetime.now().isoformat(),
                    "description": indicator.get("description", ""),
                    "tags": indicator.get("tags", []),
                    "context": indicator.get("context", {})
                }
                for indicator in filtered_indicators
            ]
            
            total_indicators += len(formatted_indicators[prov_name])
        
        return {
            "status": "success",
            "indicators": formatted_indicators,
            "total_indicators": total_indicators,
            "filters": {
                "hours": hours,
                "provider": provider,
                "threat_type": threat_type,
                "severity": severity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threat indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/indicators/search")
async def search_threat_indicators(
    search: IndicatorSearch,
    current_user: dict = Depends(get_current_user)
):
    """Search threat indicators across all providers"""
    try:
        results = await threat_intel_manager.search_all_indicators(
            search.query, 
            search.indicator_type
        )
        
        # Convert to response format
        formatted_results = {}
        total_results = 0
        
        for prov_name, indicators in results.items():
            formatted_results[prov_name] = [
                {
                    "id": indicator.get("id", ""),
                    "indicator_type": indicator.get("indicator_type", ""),
                    "value": indicator.get("value", ""),
                    "threat_type": indicator.get("threat_type", ""),
                    "severity": indicator.get("severity", ""),
                    "confidence": indicator.get("confidence", 0.0),
                    "first_seen": indicator.get("first_seen", datetime.now()).isoformat() if indicator.get("first_seen") else datetime.now().isoformat(),
                    "last_seen": indicator.get("last_seen", datetime.now()).isoformat() if indicator.get("last_seen") else datetime.now().isoformat(),
                    "description": indicator.get("description", ""),
                    "tags": indicator.get("tags", []),
                    "context": indicator.get("context", {})
                }
                for indicator in indicators
            ]
            
            total_results += len(formatted_results[prov_name])
        
        return {
            "status": "success",
            "query": search.query,
            "results": formatted_results,
            "total_results": total_results,
            "filters": {
                "indicator_type": search.indicator_type,
                "hours": search.hours
            }
        }
    except Exception as e:
        logger.error(f"Error searching threat indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def get_threat_reports(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    threat_type: Optional[str] = Query(default=None, description="Filter by threat type"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    current_user: dict = Depends(get_current_user)
):
    """Get threat reports from all providers"""
    try:
        if provider:
            if provider not in threat_intel_manager.intelligence_sources:
                raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
            
            # Get reports from specific provider
            all_reports = await threat_intel_manager.get_all_reports(hours)
            provider_reports = {provider: all_reports.get(provider, [])}
        else:
            # Get reports from all providers
            provider_reports = await threat_intel_manager.get_all_reports(hours)
        
        # Apply filters and convert to response format
        formatted_reports = {}
        total_reports = 0
        
        for prov_name, reports in provider_reports.items():
            filtered_reports = reports
            
            if threat_type:
                filtered_reports = [
                    rep for rep in filtered_reports
                    if rep.get("threat_type", "") == threat_type
                ]
            
            if severity:
                filtered_reports = [
                    rep for rep in filtered_reports
                    if rep.get("severity", "") == severity
                ]
            
            formatted_reports[prov_name] = [
                {
                    "id": report.get("id", ""),
                    "title": report.get("title", ""),
                    "threat_type": report.get("threat_type", ""),
                    "severity": report.get("severity", ""),
                    "confidence": report.get("confidence", 0.0),
                    "published": report.get("published", datetime.now()).isoformat() if report.get("published") else datetime.now().isoformat(),
                    "updated": report.get("updated", datetime.now()).isoformat() if report.get("updated") else datetime.now().isoformat(),
                    "summary": report.get("summary", ""),
                    "indicators_count": report.get("indicators_count", 0),
                    "tactics": report.get("tactics", []),
                    "techniques": report.get("techniques", []),
                    "affected_systems": report.get("affected_systems", []),
                    "mitigation": report.get("mitigation", ""),
                    "references": report.get("references", [])
                }
                for report in filtered_reports
            ]
            
            total_reports += len(formatted_reports[prov_name])
        
        return {
            "status": "success",
            "reports": formatted_reports,
            "total_reports": total_reports,
            "filters": {
                "hours": hours,
                "provider": provider,
                "threat_type": threat_type,
                "severity": severity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting threat reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_threat_intel_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence dashboard data"""
    try:
        # Get threat summary
        summary = await threat_intel_manager.get_threat_summary(hours=24)
        
        # Get top threats
        top_threats = await threat_intel_manager.get_top_threats(hours=24, limit=10)
        
        # Get recent indicators and reports
        recent_indicators = await threat_intel_manager.get_all_indicators(hours=6)
        recent_reports = await threat_intel_manager.get_all_reports(hours=6)
        
        # Calculate provider statistics
        provider_stats = {}
        for provider in threat_intel_manager.intelligence_sources.keys():
            provider_indicators = recent_indicators.get(provider, [])
            provider_reports = recent_reports.get(provider, [])
            
            provider_stats[provider] = {
                "indicators_count": len(provider_indicators),
                "reports_count": len(provider_reports),
                "last_sync": threat_intel_manager.cache.get(f'last_check_{provider}', None)
            }
        
        return {
            "status": "success",
            "dashboard": {
                "summary": summary,
                "top_threats": top_threats,
                "provider_stats": provider_stats,
                "recent_indicators": {
                    provider: indicators[:5] for provider, indicators in recent_indicators.items()
                },
                "recent_reports": {
                    provider: reports[:5] for provider, reports in recent_reports.items()
                },
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_threat_intel_summary(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence summary"""
    try:
        summary = await threat_intel_manager.get_threat_summary(hours)
        
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-threats")
async def get_top_threats(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    limit: int = Query(default=10, ge=1, le=100, description="Maximum threats to return"),
    current_user: dict = Depends(get_current_user)
):
    """Get top threats"""
    try:
        top_threats = await threat_intel_manager.get_top_threats(hours, limit)
        
        return {
            "status": "success",
            "top_threats": top_threats,
            "filters": {
                "hours": hours,
                "limit": limit
            }
        }
    except Exception as e:
        logger.error(f"Error getting top threats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_threat_intel_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence statistics"""
    try:
        # Get statistics for different time periods
        stats_24h = await threat_intel_manager.get_threat_summary(hours=24)
        stats_7d = await threat_intel_manager.get_threat_summary(hours=24*7)
        stats_30d = await threat_intel_manager.get_threat_summary(hours=24*30)
        
        return {
            "status": "success",
            "stats": {
                "last_24h": stats_24h,
                "last_7d": stats_7d,
                "last_30d": stats_30d,
                "active_providers": len([s for s in threat_intel_manager.intelligence_sources.values() if s.get('enabled')]),
                "provider_list": list(threat_intel_manager.intelligence_sources.keys())
            }
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def list_providers(current_user: dict = Depends(get_current_user)):
    """List available threat intelligence providers"""
    try:
        providers = [
            {
                "value": provider.value,
                "name": provider.value.replace("_", " ").title(),
                "description": f"{provider.value.replace('_', ' ')} threat intelligence provider",
                "capabilities": {
                    "indicators": True,
                    "reports": True,
                    "search": True
                }
            }
            for provider in ThreatIntelProvider
        ]
        
        return {
            "status": "success",
            "providers": providers,
            "total": len(providers)
        }
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threat-types")
async def list_threat_types(current_user: dict = Depends(get_current_user)):
    """List available threat types"""
    try:
        threat_types = [
            {
                "value": threat_type.value,
                "name": threat_type.value.replace("_", " ").title(),
                "description": f"{threat_type.value.replace('_', ' ')} threats"
            }
            for threat_type in ThreatType
        ]
        
        return {
            "status": "success",
            "threat_types": threat_types,
            "total": len(threat_types)
        }
    except Exception as e:
        logger.error(f"Error listing threat types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/severities")
async def list_severities(current_user: dict = Depends(get_current_user)):
    """List available severity levels"""
    try:
        severities = [
            {
                "value": severity.value,
                "name": severity.value.title(),
                "description": f"{severity.value.title()} severity level"
            }
            for severity in ThreatSeverity
        ]
        
        return {
            "status": "success",
            "severities": severities,
            "total": len(severities)
        }
    except Exception as e:
        logger.error(f"Error listing severities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connectors/{provider}")
async def unregister_threat_intel_connector(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Unregister a threat intelligence connector"""
    try:
        provider = provider.lower()
        
        if provider not in threat_intel_manager.intelligence_sources:
            raise HTTPException(status_code=404, detail=f"Connector not found: {provider}")
        
        # Remove connector
        del threat_intel_manager.intelligence_sources[provider]
        
        return {
            "status": "success",
            "message": f"{provider.upper()} threat intelligence connector unregistered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering threat intelligence connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync")
async def sync_threat_intel(
    provider: Optional[str] = Query(default=None, description="Specific provider to sync"),
    current_user: dict = Depends(get_current_user)
):
    """Manually sync threat intelligence"""
    try:
        if provider:
            if provider not in threat_intel_manager.intelligence_sources:
                raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
            
            # Sync specific provider
            all_indicators = await threat_intel_manager.get_all_indicators(hours=24)
            all_reports = await threat_intel_manager.get_all_reports(hours=24)
            indicators = all_indicators.get(provider, [])
            reports = all_reports.get(provider, [])
            
            return {
                "status": "success",
                "message": f"Sync completed for {provider}",
                "provider": provider,
                "indicators_synced": len(indicators),
                "reports_synced": len(reports),
                "sync_time": datetime.now().isoformat()
            }
        else:
            # Sync all providers
            all_indicators = await threat_intel_manager.get_all_indicators(hours=24)
            all_reports = await threat_intel_manager.get_all_reports(hours=24)
            
            total_indicators = sum(len(indicators) for indicators in all_indicators.values())
            total_reports = sum(len(reports) for reports in all_reports.values())
            
            return {
                "status": "success",
                "message": "Sync completed for all providers",
                "total_indicators_synced": total_indicators,
                "total_reports_synced": total_reports,
                "providers_synced": list(all_indicators.keys()),
                "sync_time": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error syncing threat intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))
