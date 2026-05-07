"""
Cloud Platform Connectors API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.services.cloud_connectors import (
    cloud_connector_manager, 
    CloudProvider, 
    AWSConnector, 
    AzureConnector, 
    GCPConnector
)
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class CloudCredentials(BaseModel):
    provider: str = Field(..., description="Cloud provider (aws, azure, gcp)")
    credentials: Dict[str, Any] = Field(..., description="Cloud provider credentials")

class SecurityEventQuery(BaseModel):
    start_time: datetime = Field(..., description="Start time for events")
    end_time: datetime = Field(..., description="End time for events")
    providers: Optional[List[str]] = Field(default=None, description="Filter by providers")
    severity: Optional[List[str]] = Field(default=None, description="Filter by severity")
    event_types: Optional[List[str]] = Field(default=None, description="Filter by event types")

class RemediationRequest(BaseModel):
    provider: str = Field(..., description="Cloud provider")
    issue_id: str = Field(..., description="Issue ID to remediate")
    action: str = Field(..., description="Remediation action")

@router.post("/connectors/register")
async def register_connector(
    request: CloudCredentials,
    current_user: dict = Depends(get_current_user)
):
    """Register a cloud connector"""
    try:
        provider = request.provider.lower()
        
        # Create appropriate connector
        if provider == "aws":
            connector = AWSConnector(request.credentials)
        elif provider == "azure":
            connector = AzureConnector(request.credentials)
        elif provider == "gcp":
            connector = GCPConnector(request.credentials)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Authenticate the connector
        auth_success = await connector.authenticate()
        if not auth_success:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Register the connector
        cloud_connector_manager.register_connector(provider, connector)
        
        return {
            "status": "success",
            "message": f"{provider.upper()} connector registered and authenticated successfully",
            "provider": provider
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connectors/authenticate-all")
async def authenticate_all_connectors(current_user: dict = Depends(get_current_user)):
    """Authenticate all registered connectors"""
    try:
        results = await cloud_connector_manager.authenticate_all()
        
        return {
            "status": "success",
            "authentication_results": results,
            "authenticated_count": sum(1 for success in results.values() if success),
            "total_count": len(results)
        }
    except Exception as e:
        logger.error(f"Error authenticating connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_connectors(current_user: dict = Depends(get_current_user)):
    """List registered connectors"""
    try:
        connectors = []
        
        for provider, connector in cloud_connector_manager.connectors.items():
            connectors.append({
                "provider": provider,
                "type": connector.__class__.__name__,
                "last_sync": cloud_connector_manager.last_sync_times.get(provider),
                "status": "registered"
            })
        
        return {
            "status": "success",
            "connectors": connectors,
            "total": len(connectors)
        }
    except Exception as e:
        logger.error(f"Error listing connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/query")
async def query_security_events(
    query: SecurityEventQuery,
    current_user: dict = Depends(get_current_user)
):
    """Query security events from cloud providers"""
    try:
        # Get all events
        all_events = await cloud_connector_manager.get_all_security_events(
            query.start_time,
            query.end_time
        )
        
        # Apply filters
        filtered_events = all_events
        
        if query.providers:
            filtered_events = [
                event for event in filtered_events
                if event.provider.value in query.providers
            ]
        
        if query.severity:
            filtered_events = [
                event for event in filtered_events
                if event.severity in query.severity
            ]
        
        if query.event_types:
            filtered_events = [
                event for event in filtered_events
                if event.event_type in query.event_types
            ]
        
        # Convert to response format
        events_response = [
            {
                "id": f"{event.provider.value}_{event.service}_{event.timestamp.timestamp()}",
                "provider": event.provider.value,
                "service": event.service,
                "event_type": event.event_type,
                "severity": event.severity,
                "timestamp": event.timestamp.isoformat(),
                "resource_id": event.resource_id,
                "resource_type": event.resource_type,
                "account_id": event.account_id,
                "region": event.region,
                "details": event.details,
                "raw_event": event.raw_event
            }
            for event in filtered_events
        ]
        
        return {
            "status": "success",
            "events": events_response,
            "total": len(events_response),
            "query_params": {
                "start_time": query.start_time.isoformat(),
                "end_time": query.end_time.isoformat(),
                "providers": query.providers,
                "severity": query.severity,
                "event_types": query.event_types
            }
        }
    except Exception as e:
        logger.error(f"Error querying security events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/recent")
async def get_recent_events(
    hours: int = Query(default=24, ge=1, le=168, description="Hours to look back"),
    providers: Optional[List[str]] = Query(default=None, description="Filter by providers"),
    severity: Optional[List[str]] = Query(default=None, description="Filter by severity"),
    current_user: dict = Depends(get_current_user)
):
    """Get recent security events"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        query = SecurityEventQuery(
            start_time=start_time,
            end_time=end_time,
            providers=providers,
            severity=severity
        )
        
        return await query_security_events(query, current_user)
    except Exception as e:
        logger.error(f"Error getting recent events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/vulnerabilities")
async def get_vulnerabilities(
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    current_user: dict = Depends(get_current_user)
):
    """Get vulnerabilities from cloud providers"""
    try:
        if provider:
            if provider not in cloud_connector_manager.connectors:
                raise HTTPException(status_code=404, detail=f"Connector not found: {provider}")
            
            # Get vulnerabilities from specific provider
            connector = cloud_connector_manager.connectors[provider]
            vulnerabilities = {provider: await connector.get_vulnerabilities()}
        else:
            # Get vulnerabilities from all providers
            vulnerabilities = await cloud_connector_manager.get_all_vulnerabilities()
        
        return {
            "status": "success",
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": sum(len(vulns) for vulns in vulnerabilities.values())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vulnerabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compliance")
async def get_compliance_status(
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    current_user: dict = Depends(get_current_user)
):
    """Get compliance status from cloud providers"""
    try:
        if provider:
            if provider not in cloud_connector_manager.connectors:
                raise HTTPException(status_code=404, detail=f"Connector not found: {provider}")
            
            # Get compliance status from specific provider
            connector = cloud_connector_manager.connectors[provider]
            compliance_status = {provider: await connector.get_compliance_status()}
        else:
            # Get compliance status from all providers
            compliance_status = await cloud_connector_manager.get_all_compliance_status()
        
        # Calculate overall compliance metrics
        total_resources = 0
        compliant_resources = 0
        non_compliant_resources = 0
        
        for status in compliance_status.values():
            if status:
                total_resources += status.get('total_resources', 0)
                compliant_resources += status.get('compliant_resources', 0)
                non_compliant_resources += status.get('non_compliant_resources', 0)
        
        overall_compliance_percentage = (
            (compliant_resources / total_resources * 100) 
            if total_resources > 0 else 0
        )
        
        return {
            "status": "success",
            "compliance_status": compliance_status,
            "summary": {
                "total_resources": total_resources,
                "compliant_resources": compliant_resources,
                "non_compliant_resources": non_compliant_resources,
                "overall_compliance_percentage": round(overall_compliance_percentage, 1)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remediate")
async def remediate_issue(
    request: RemediationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Remediate a security issue"""
    try:
        provider = request.provider.lower()
        
        if provider not in cloud_connector_manager.connectors:
            raise HTTPException(status_code=404, detail=f"Connector not found: {provider}")
        
        connector = cloud_connector_manager.connectors[provider]
        result = await connector.remediate_issue(request.issue_id, request.action)
        
        return {
            "status": "success",
            "remediation_result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error remediating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remediate/batch")
async def remediate_multiple_issues(
    requests: List[RemediationRequest],
    current_user: dict = Depends(get_current_user)
):
    """Remediate multiple security issues"""
    try:
        issues = [
            {
                "provider": req.provider.lower(),
                "issue_id": req.issue_id,
                "action": req.action
            }
            for req in requests
        ]
        
        results = await cloud_connector_manager.remediate_all_issues(issues)
        
        return {
            "status": "success",
            "remediation_results": results,
            "total_issues": len(requests),
            "successful_remediations": sum(1 for r in results if r.get('status') == 'success'),
            "failed_remediations": sum(1 for r in results if r.get('status') == 'failed')
        }
    except Exception as e:
        logger.error(f"Error in batch remediation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_cloud_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get cloud security dashboard data"""
    try:
        # Get recent events (last 24 hours)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        recent_events = await cloud_connector_manager.get_all_security_events(start_time, end_time)
        
        # Get vulnerabilities
        vulnerabilities = await cloud_connector_manager.get_all_vulnerabilities()
        
        # Get compliance status
        compliance_status = await cloud_connector_manager.get_all_compliance_status()
        
        # Calculate metrics
        total_events = len(recent_events)
        high_severity_events = len([e for e in recent_events if e.severity == 'HIGH'])
        medium_severity_events = len([e for e in recent_events if e.severity == 'MEDIUM'])
        low_severity_events = len([e for e in recent_events if e.severity == 'LOW'])
        
        total_vulnerabilities = sum(len(vulns) for vulns in vulnerabilities.values())
        high_vulnerabilities = sum(
            len([v for v in vulns if v.get('severity') == 'HIGH'])
            for vulns in vulnerabilities.values()
        )
        
        # Provider breakdown
        provider_events = {}
        for event in recent_events:
            provider = event.provider.value
            provider_events[provider] = provider_events.get(provider, 0) + 1
        
        provider_vulnerabilities = {
            provider: len(vulns)
            for provider, vulns in vulnerabilities.items()
        }
        
        # Recent high-priority events
        high_priority_events = [
            {
                "id": f"{event.provider.value}_{event.service}_{event.timestamp.timestamp()}",
                "provider": event.provider.value,
                "service": event.service,
                "event_type": event.event_type,
                "severity": event.severity,
                "timestamp": event.timestamp.isoformat(),
                "resource_id": event.resource_id,
                "description": event.details.get('description', event.event_type)
            }
            for event in recent_events
            if event.severity in ['HIGH', 'CRITICAL']
        ][:10]
        
        return {
            "status": "success",
            "dashboard": {
                "summary": {
                    "total_events": total_events,
                    "high_severity_events": high_severity_events,
                    "medium_severity_events": medium_severity_events,
                    "low_severity_events": low_severity_events,
                    "total_vulnerabilities": total_vulnerabilities,
                    "high_vulnerabilities": high_vulnerabilities,
                    "connected_providers": len(cloud_connector_manager.connectors)
                },
                "provider_breakdown": {
                    "events": provider_events,
                    "vulnerabilities": provider_vulnerabilities
                },
                "compliance_summary": compliance_status,
                "recent_high_priority_events": high_priority_events,
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting cloud dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_cloud_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get cloud security statistics"""
    try:
        # Get events for the last 7 days
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        events = await cloud_connector_manager.get_all_security_events(start_time, end_time)
        vulnerabilities = await cloud_connector_manager.get_all_vulnerabilities()
        compliance_status = await cloud_connector_manager.get_all_compliance_status()
        
        # Event trends by day
        daily_events = {}
        for event in events:
            day = event.timestamp.strftime('%Y-%m-%d')
            daily_events[day] = daily_events.get(day, 0) + 1
        
        # Severity distribution
        severity_distribution = {}
        for event in events:
            severity = event.severity
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        # Service distribution
        service_distribution = {}
        for event in events:
            service = event.service
            service_distribution[service] = service_distribution.get(service, 0) + 1
        
        # Provider statistics
        provider_stats = {}
        for provider in cloud_connector_manager.connectors.keys():
            provider_events = [e for e in events if e.provider.value == provider]
            provider_vulns = vulnerabilities.get(provider, [])
            provider_compliance = compliance_status.get(provider, {})
            
            provider_stats[provider] = {
                "events": len(provider_events),
                "vulnerabilities": len(provider_vulns),
                "compliance_percentage": provider_compliance.get('compliance_percentage', 0),
                "high_severity_events": len([e for e in provider_events if e.severity == 'HIGH'])
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
                "total_vulnerabilities": sum(len(vulns) for vulns in vulnerabilities.values()),
                "daily_events": daily_events,
                "severity_distribution": severity_distribution,
                "service_distribution": service_distribution,
                "provider_stats": provider_stats
            }
        }
    except Exception as e:
        logger.error(f"Error getting cloud stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connectors/{provider}")
async def unregister_connector(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Unregister a cloud connector"""
    try:
        provider = provider.lower()
        
        if provider not in cloud_connector_manager.connectors:
            raise HTTPException(status_code=404, detail=f"Connector not found: {provider}")
        
        # Remove the connector
        del cloud_connector_manager.connectors[provider]
        
        # Clean up last sync time
        if provider in cloud_connector_manager.last_sync_times:
            del cloud_connector_manager.last_sync_times[provider]
        
        return {
            "status": "success",
            "message": f"{provider.upper()} connector unregistered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))
