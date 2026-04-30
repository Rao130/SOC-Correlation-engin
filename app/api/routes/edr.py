"""
EDR (Endpoint Detection and Response) API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.services.edr_connectors import (
    edr_manager, 
    EDRProvider, 
    DetectionSeverity, 
    CrowdStrikeConnector, 
    SentinelOneConnector
)
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class EDRCredentials(BaseModel):
    provider: str = Field(..., description="EDR provider (crowdstrike, sentinelone, carbon_black)")
    credentials: Dict[str, Any] = Field(..., description="EDR provider credentials")

class EndpointAction(BaseModel):
    provider: str = Field(..., description="EDR provider")
    endpoint_id: str = Field(..., description="Endpoint ID")
    action: str = Field(..., description="Action to perform")

class ScanRequest(BaseModel):
    provider: str = Field(..., description="EDR provider")
    endpoint_id: str = Field(..., description="Endpoint ID")
    scan_type: str = Field(..., description="Type of scan to perform")

class QuarantineRequest(BaseModel):
    provider: str = Field(..., description="EDR provider")
    endpoint_id: str = Field(..., description="Endpoint ID")
    file_hash: str = Field(..., description="File hash to quarantine")

@router.post("/connectors/register")
async def register_edr_connector(
    request: EDRCredentials,
    current_user: dict = Depends(get_current_user)
):
    """Register an EDR connector"""
    try:
        provider = request.provider.lower()
        
        # Create appropriate connector
        if provider == "crowdstrike":
            connector = CrowdStrikeConnector(request.credentials)
        elif provider == "sentinelone":
            connector = SentinelOneConnector(request.credentials)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Authenticate connector
        auth_success = await connector.authenticate()
        if not auth_success:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Register connector
        edr_manager.register_connector(provider, connector)
        
        return {
            "status": "success",
            "message": f"{provider.upper()} EDR connector registered and authenticated successfully",
            "provider": provider
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering EDR connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_edr_connectors(current_user: dict = Depends(get_current_user)):
    """List registered EDR connectors"""
    try:
        connectors = []
        
        for provider, connector in edr_manager.connectors.items():
            connectors.append({
                "provider": provider,
                "type": connector.__class__.__name__,
                "last_sync": edr_manager.last_sync_times.get(provider),
                "status": "registered"
            })
        
        return {
            "status": "success",
            "connectors": connectors,
            "total": len(connectors)
        }
    except Exception as e:
        logger.error(f"Error listing EDR connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_edr_events(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    providers: Optional[List[str]] = Query(default=None, description="Filter by providers"),
    severity: Optional[List[str]] = Query(default=None, description="Filter by severity"),
    current_user: dict = Depends(get_current_user)
):
    """Get EDR events from all providers"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get all events
        all_events = await edr_manager.get_all_events(start_time, end_time)
        
        # Apply filters
        filtered_events = all_events
        
        if providers:
            filtered_events = [
                event for event in filtered_events
                if event.provider.value in providers
            ]
        
        if severity:
            filtered_events = [
                event for event in filtered_events
                if event.severity.value in severity
            ]
        
        # Convert to response format
        events_response = [
            {
                "id": f"{event.provider.value}_{event.endpoint_id}_{event.timestamp.timestamp()}",
                "provider": event.provider.value,
                "endpoint_id": event.endpoint_id,
                "hostname": event.hostname,
                "ip_address": event.ip_address,
                "user": event.user,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type,
                "severity": event.severity.value,
                "description": event.description,
                "file_path": event.file_path,
                "process_name": event.process_name,
                "command_line": event.command_line,
                "mitre_tactics": event.mitre_tactics,
                "mitre_techniques": event.mitre_techniques,
                "raw_event": event.raw_event
            }
            for event in filtered_events
        ]
        
        return {
            "status": "success",
            "events": events_response,
            "total": len(events_response),
            "query_params": {
                "hours": hours,
                "providers": providers,
                "severity": severity
            }
        }
    except Exception as e:
        logger.error(f"Error getting EDR events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/endpoints")
async def get_endpoints(
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    current_user: dict = Depends(get_current_user)
):
    """Get endpoints from EDR providers"""
    try:
        if provider:
            if provider not in edr_manager.connectors:
                raise HTTPException(status_code=404, detail=f"EDR connector not found: {provider}")
            
            # Get endpoints from specific provider
            connector = edr_manager.connectors[provider]
            provider_endpoints = {provider: await connector.get_endpoints()}
        else:
            # Get endpoints from all providers
            provider_endpoints = await edr_manager.get_all_endpoints()
        
        # Apply filters and convert to response format
        all_endpoints = []
        for prov_name, endpoints in provider_endpoints.items():
            for endpoint in endpoints:
                if status and endpoint.status.value != status:
                    continue
                
                endpoint_data = {
                    "provider": prov_name,
                    "endpoint_id": endpoint.endpoint_id,
                    "hostname": endpoint.hostname,
                    "ip_address": endpoint.ip_address,
                    "os": endpoint.os,
                    "os_version": endpoint.os_version,
                    "status": endpoint.status.value,
                    "last_seen": endpoint.last_seen.isoformat(),
                    "agent_version": endpoint.agent_version,
                    "policies": endpoint.policies,
                    "tags": endpoint.tags
                }
                all_endpoints.append(endpoint_data)
        
        return {
            "status": "success",
            "endpoints": all_endpoints,
            "total": len(all_endpoints)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting endpoints: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/endpoints/isolate")
async def isolate_endpoint(
    request: EndpointAction,
    current_user: dict = Depends(get_current_user)
):
    """Isolate an endpoint"""
    try:
        provider = request.provider.lower()
        
        result = await edr_manager.isolate_endpoint(provider, request.endpoint_id)
        
        return {
            "status": "success",
            "action_result": result
        }
    except Exception as e:
        logger.error(f"Error isolating endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/endpoints/unisolate")
async def unisolate_endpoint(
    request: EndpointAction,
    current_user: dict = Depends(get_current_user)
):
    """Un-isolate an endpoint"""
    try:
        provider = request.provider.lower()
        
        result = await edr_manager.unisolate_endpoint(provider, request.endpoint_id)
        
        return {
            "status": "success",
            "action_result": result
        }
    except Exception as e:
        logger.error(f"Error un-isolating endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/endpoints/scan")
async def scan_endpoint(
    request: ScanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Scan an endpoint"""
    try:
        provider = request.provider.lower()
        
        result = await edr_manager.scan_endpoint(provider, request.endpoint_id, request.scan_type)
        
        return {
            "status": "success",
            "scan_result": result
        }
    except Exception as e:
        logger.error(f"Error scanning endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/endpoints/quarantine")
async def quarantine_file(
    request: QuarantineRequest,
    current_user: dict = Depends(get_current_user)
):
    """Quarantine a file on endpoint"""
    try:
        provider = request.provider.lower()
        
        result = await edr_manager.quarantine_file(provider, request.endpoint_id, request.file_hash)
        
        return {
            "status": "success",
            "quarantine_result": result
        }
    except Exception as e:
        logger.error(f"Error quarantining file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_edr_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get EDR dashboard data"""
    try:
        # Get recent events (last 24 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        recent_events = await edr_manager.get_all_events(start_time, end_time)
        
        # Get endpoints
        all_endpoints = await edr_manager.get_all_endpoints()
        
        # Get endpoint statistics
        endpoint_stats = await edr_manager.get_endpoint_statistics()
        
        # Calculate metrics
        total_events = len(recent_events)
        critical_events = len([e for e in recent_events if e.severity == DetectionSeverity.CRITICAL])
        high_events = len([e for e in recent_events if e.severity == DetectionSeverity.HIGH])
        medium_events = len([e for e in recent_events if e.severity == DetectionSeverity.MEDIUM])
        low_events = len([e for e in recent_events if e.severity == DetectionSeverity.LOW])
        
        # Provider breakdown
        provider_events = {}
        for event in recent_events:
            provider = event.provider.value
            provider_events[provider] = provider_events.get(provider, 0) + 1
        
        # Recent critical events
        critical_events_list = [
            {
                "id": f"{event.provider.value}_{event.endpoint_id}_{event.timestamp.timestamp()}",
                "provider": event.provider.value,
                "endpoint_id": event.endpoint_id,
                "hostname": event.hostname,
                "timestamp": event.timestamp.isoformat(),
                "severity": event.severity.value,
                "description": event.description,
                "user": event.user,
                "process_name": event.process_name
            }
            for event in recent_events
            if event.severity in [DetectionSeverity.CRITICAL, DetectionSeverity.HIGH]
        ][:10]
        
        return {
            "status": "success",
            "dashboard": {
                "summary": {
                    "total_events": total_events,
                    "critical_events": critical_events,
                    "high_events": high_events,
                    "medium_events": medium_events,
                    "low_events": low_events,
                    "total_endpoints": endpoint_stats.get('total_endpoints', 0),
                    "online_endpoints": endpoint_stats.get('online_endpoints', 0),
                    "offline_endpoints": endpoint_stats.get('offline_endpoints', 0),
                    "isolated_endpoints": endpoint_stats.get('isolated_endpoints', 0)
                },
                "provider_breakdown": provider_events,
                "endpoint_statistics": endpoint_stats,
                "recent_critical_events": critical_events_list,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting EDR dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_edr_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get EDR statistics"""
    try:
        # Get events for last 7 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        events = await edr_manager.get_all_events(start_time, end_time)
        endpoints = await edr_manager.get_all_endpoints()
        endpoint_stats = await edr_manager.get_endpoint_statistics()
        
        # Event trends by day
        daily_events = {}
        for event in events:
            day = event.timestamp.strftime('%Y-%m-%d')
            daily_events[day] = daily_events.get(day, 0) + 1
        
        # Severity distribution
        severity_distribution = {}
        for event in events:
            severity = event.severity.value
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        # Event type distribution
        event_type_distribution = {}
        for event in events:
            event_type = event.event_type
            event_type_distribution[event_type] = event_type_distribution.get(event_type, 0) + 1
        
        # Provider statistics
        provider_stats = {}
        for provider in edr_manager.connectors.keys():
            provider_events = [e for e in events if e.provider.value == provider]
            provider_endpoints = endpoints.get(provider, [])
            
            provider_stats[provider] = {
                "events": len(provider_events),
                "endpoints": len(provider_endpoints),
                "critical_events": len([e for e in provider_events if e.severity == DetectionSeverity.CRITICAL]),
                "high_events": len([e for e in provider_events if e.severity == DetectionSeverity.HIGH])
            }
        
        return {
            "status": "success",
            "stats": {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "days": 7
                },
                "total_events": len(events),
                "total_endpoints": endpoint_stats.get('total_endpoints', 0),
                "daily_events": daily_events,
                "severity_distribution": severity_distribution,
                "event_type_distribution": event_type_distribution,
                "provider_stats": provider_stats,
                "endpoint_statistics": endpoint_stats
            }
        }
    except Exception as e:
        logger.error(f"Error getting EDR stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/threat-intelligence")
async def get_threat_intelligence(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    current_user: dict = Depends(get_current_user)
):
    """Get threat intelligence from EDR events"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        events = await edr_manager.get_all_events(start_time, end_time)
        
        # Extract MITRE tactics and techniques
        tactics = {}
        techniques = {}
        
        for event in events:
            for tactic in event.mitre_tactics:
                tactics[tactic] = tactics.get(tactic, 0) + 1
            
            for technique in event.mitre_techniques:
                techniques[technique] = techniques.get(technique, 0) + 1
        
        # Identify top malicious processes
        malicious_processes = {}
        for event in events:
            if event.process_name and event.severity in [DetectionSeverity.HIGH, DetectionSeverity.CRITICAL]:
                process = event.process_name
                malicious_processes[process] = malicious_processes.get(process, 0) + 1
        
        # Identify top suspicious users
        suspicious_users = {}
        for event in events:
            if event.severity in [DetectionSeverity.HIGH, DetectionSeverity.CRITICAL]:
                user = event.user
                suspicious_users[user] = suspicious_users.get(user, 0) + 1
        
        return {
            "status": "success",
            "threat_intelligence": {
                "period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                },
                "mitre_tactics": dict(sorted(tactics.items(), key=lambda x: x[1], reverse=True)),
                "mitre_techniques": dict(sorted(techniques.items(), key=lambda x: x[1], reverse=True)),
                "top_malicious_processes": dict(sorted(malicious_processes.items(), key=lambda x: x[1], reverse=True)[:10]),
                "top_suspicious_users": dict(sorted(suspicious_users.items(), key=lambda x: x[1], reverse=True)[:10]),
                "total_threat_events": len([e for e in events if e.severity in [DetectionSeverity.HIGH, DetectionSeverity.CRITICAL]])
            }
        }
    except Exception as e:
        logger.error(f"Error getting threat intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connectors/{provider}")
async def unregister_edr_connector(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Unregister an EDR connector"""
    try:
        provider = provider.lower()
        
        if provider not in edr_manager.connectors:
            raise HTTPException(status_code=404, detail=f"EDR connector not found: {provider}")
        
        # Remove connector
        del edr_manager.connectors[provider]
        
        # Clean up last sync time
        if provider in edr_manager.last_sync_times:
            del edr_manager.last_sync_times[provider]
        
        return {
            "status": "success",
            "message": f"{provider.upper()} EDR connector unregistered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering EDR connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))
