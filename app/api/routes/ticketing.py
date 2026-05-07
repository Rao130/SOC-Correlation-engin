"""
Ticketing System API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.services.ticketing_connectors import (
    ticketing_manager, 
    TicketingProvider, 
    TicketStatus, 
    TicketPriority,
    ServiceNowConnector, 
    JiraConnector
)
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class TicketingCredentials(BaseModel):
    provider: str = Field(..., description="Ticketing provider (servicenow, jira, remedy)")
    credentials: Dict[str, Any] = Field(..., description="Ticketing provider credentials")
    is_default: bool = Field(default=False, description="Set as default provider")

class TicketCreate(BaseModel):
    title: str = Field(..., description="Ticket title")
    description: str = Field(..., description="Ticket description")
    priority: str = Field(default="medium", description="Ticket priority")
    assignee: Optional[str] = Field(default=None, description="Assignee")
    reporter: Optional[str] = Field(default=None, description="Reporter")
    tags: List[str] = Field(default_factory=list, description="Ticket tags")
    attachments: List[str] = Field(default_factory=list, description="Ticket attachments")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Custom fields")
    provider: Optional[str] = Field(default=None, description="Target provider")

class TicketUpdate(BaseModel):
    status: Optional[str] = Field(default=None, description="New status")
    priority: Optional[str] = Field(default=None, description="New priority")
    assignee: Optional[str] = Field(default=None, description="New assignee")
    comment: Optional[str] = Field(default=None, description="Update comment")

class TicketComment(BaseModel):
    comment: str = Field(..., description="Comment text")
    internal: bool = Field(default=False, description="Internal comment")

@router.post("/connectors/register")
async def register_ticketing_connector(
    request: TicketingCredentials,
    current_user: dict = Depends(get_current_user)
):
    """Register a ticketing connector"""
    try:
        provider = request.provider.lower()
        
        # Create appropriate connector
        if provider == "servicenow":
            connector = ServiceNowConnector(request.credentials)
        elif provider == "jira":
            connector = JiraConnector(request.credentials)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")
        
        # Authenticate connector
        auth_success = await connector.authenticate()
        if not auth_success:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Register connector
        ticketing_manager.register_connector(provider, connector, request.is_default)
        
        return {
            "status": "success",
            "message": f"{provider.upper()} ticketing connector registered and authenticated successfully",
            "provider": provider,
            "is_default": request.is_default
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering ticketing connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/connectors")
async def list_ticketing_connectors(current_user: dict = Depends(get_current_user)):
    """List registered ticketing connectors"""
    try:
        connectors = []
        
        for provider, connector in ticketing_manager.connectors.items():
            connectors.append({
                "provider": provider,
                "type": connector.__class__.__name__,
                "is_default": provider == ticketing_manager.default_provider,
                "last_sync": ticketing_manager.last_sync_times.get(provider),
                "status": "registered"
            })
        
        return {
            "status": "success",
            "connectors": connectors,
            "total": len(connectors),
            "default_provider": ticketing_manager.default_provider
        }
    except Exception as e:
        logger.error(f"Error listing ticketing connectors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tickets")
async def create_ticket(
    ticket: TicketCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new ticket"""
    try:
        # Prepare ticket data
        ticket_data = {
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'assignee': ticket.assignee,
            'reporter': ticket.reporter or current_user.get('username', 'system'),
            'tags': ticket.tags,
            'attachments': ticket.attachments,
            'custom_fields': ticket.custom_fields
        }
        
        # Add Jira-specific fields if needed
        if ticket.provider == "jira" or (not ticket.provider and ticketing_manager.default_provider == "jira"):
            ticket_data['issue_type'] = ticket.custom_fields.get('issue_type', 'Task')
            ticket_data['components'] = ticket.custom_fields.get('components', [])
            ticket_data['labels'] = ticket.tags
        
        # Create ticket
        created_ticket = await ticketing_manager.create_ticket(ticket_data, ticket.provider)
        
        return {
            "status": "success",
            "message": "Ticket created successfully",
            "ticket": {
                "provider": created_ticket.provider.value,
                "ticket_id": created_ticket.ticket_id,
                "title": created_ticket.title,
                "status": created_ticket.status.value,
                "priority": created_ticket.priority.value,
                "assignee": created_ticket.assignee,
                "reporter": created_ticket.reporter,
                "created_at": created_ticket.created_at.isoformat(),
                "due_date": created_ticket.due_date.isoformat() if created_ticket.due_date else None,
                "tags": created_ticket.tags,
                "attachments": created_ticket.attachments
            }
        }
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets/{provider}/{ticket_id}")
async def get_ticket(
    provider: str,
    ticket_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get ticket by ID"""
    try:
        ticket = await ticketing_manager.get_ticket(ticket_id, provider)
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            "status": "success",
            "ticket": {
                "provider": ticket.provider.value,
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value,
                "priority": ticket.priority.value,
                "assignee": ticket.assignee,
                "reporter": ticket.reporter,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
                "tags": ticket.tags,
                "attachments": ticket.attachments,
                "custom_fields": ticket.custom_fields
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tickets/{provider}/{ticket_id}")
async def update_ticket(
    provider: str,
    ticket_id: str,
    update: TicketUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update ticket"""
    try:
        # Prepare update data
        updates = {}
        if update.status:
            updates['status'] = update.status
        if update.priority:
            updates['priority'] = update.priority
        if update.assignee:
            updates['assignee'] = update.assignee
        
        # Update ticket
        updated_ticket = await ticketing_manager.update_ticket(ticket_id, updates, provider)
        
        # Add comment if provided
        if update.comment:
            await ticketing_manager.add_comment(ticket_id, update.comment, provider, internal=False)
        
        return {
            "status": "success",
            "message": "Ticket updated successfully",
            "ticket": {
                "provider": updated_ticket.provider.value,
                "ticket_id": updated_ticket.ticket_id,
                "title": updated_ticket.title,
                "status": updated_ticket.status.value,
                "priority": updated_ticket.priority.value,
                "assignee": updated_ticket.assignee,
                "updated_at": updated_ticket.updated_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tickets/{provider}/{ticket_id}/comments")
async def add_ticket_comment(
    provider: str,
    ticket_id: str,
    comment: TicketComment,
    current_user: dict = Depends(get_current_user)
):
    """Add comment to ticket"""
    try:
        ticket_comment = await ticketing_manager.add_comment(
            ticket_id, 
            comment.comment, 
            provider, 
            comment.internal
        )
        
        return {
            "status": "success",
            "message": "Comment added successfully",
            "comment": {
                "ticket_id": ticket_comment.ticket_id,
                "comment_id": ticket_comment.comment_id,
                "author": ticket_comment.author,
                "body": ticket_comment.body,
                "created_at": ticket_comment.created_at.isoformat(),
                "is_internal": ticket_comment.is_internal,
                "attachments": ticket_comment.attachments
            }
        }
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets/search")
async def search_tickets(
    query: str = Query(..., description="Search query"),
    provider: Optional[str] = Query(default=None, description="Search in specific provider"),
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """Search tickets"""
    try:
        if provider:
            if provider not in ticketing_manager.connectors:
                raise HTTPException(status_code=404, detail=f"Provider not found: {provider}")
            
            # Search in specific provider
            connector = ticketing_manager.connectors[provider]
            tickets = await connector.search_tickets(query, limit)
            results = {provider: tickets}
        else:
            # Search in all providers
            results = await ticketing_manager.search_all_tickets(query, limit)
        
        # Convert to response format
        formatted_results = {}
        for prov_name, tickets in results.items():
            formatted_results[prov_name] = [
                {
                    "provider": ticket.provider.value,
                    "ticket_id": ticket.ticket_id,
                    "title": ticket.title,
                    "status": ticket.status.value,
                    "priority": ticket.priority.value,
                    "assignee": ticket.assignee,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat(),
                    "tags": ticket.tags
                }
                for ticket in tickets
            ]
        
        total_tickets = sum(len(tickets) for tickets in results.values())
        
        return {
            "status": "success",
            "query": query,
            "results": formatted_results,
            "total_tickets": total_tickets,
            "providers_searched": list(results.keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets")
async def list_tickets(
    status: Optional[str] = Query(default=None, description="Filter by status"),
    provider: Optional[str] = Query(default=None, description="Filter by provider"),
    priority: Optional[str] = Query(default=None, description="Filter by priority"),
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum results"),
    current_user: dict = Depends(get_current_user)
):
    """List tickets with filters"""
    try:
        all_results = {}
        
        if status:
            # Get tickets by status
            status_enum = TicketStatus(status)
            results = await ticketing_manager.get_all_tickets_by_status(status_enum, limit)
            all_results = results
        else:
            # Get recent tickets from all providers
            for prov_name, connector in ticketing_manager.connectors.items():
                if provider and prov_name != provider:
                    continue
                
                try:
                    tickets = await connector.search_tickets("", limit)
                    all_results[prov_name] = tickets
                except Exception as e:
                    logger.error(f"Error getting tickets from {prov_name}: {e}")
                    all_results[prov_name] = []
        
        # Apply additional filters
        formatted_results = {}
        for prov_name, tickets in all_results.items():
            filtered_tickets = tickets
            
            if priority:
                filtered_tickets = [
                    ticket for ticket in filtered_tickets
                    if ticket.priority.value == priority
                ]
            
            formatted_results[prov_name] = [
                {
                    "provider": ticket.provider.value,
                    "ticket_id": ticket.ticket_id,
                    "title": ticket.title,
                    "description": ticket.description[:200] + "..." if len(ticket.description) > 200 else ticket.description,
                    "status": ticket.status.value,
                    "priority": ticket.priority.value,
                    "assignee": ticket.assignee,
                    "reporter": ticket.reporter,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat(),
                    "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
                    "tags": ticket.tags
                }
                for ticket in filtered_tickets
            ]
        
        total_tickets = sum(len(tickets) for tickets in formatted_results.values())
        
        return {
            "status": "success",
            "tickets": formatted_results,
            "total_tickets": total_tickets,
            "filters": {
                "status": status,
                "provider": provider,
                "priority": priority
            }
        }
    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_ticketing_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get ticketing dashboard data"""
    try:
        # Get ticket statistics
        stats = await ticketing_manager.get_ticket_statistics()
        
        # Get recent tickets
        recent_tickets = stats.get('recent_tickets', [])
        
        # Get overdue tickets
        overdue_tickets = []
        for ticket in recent_tickets:
            if ticket.due_date and ticket.due_date < datetime.now():
                overdue_tickets.append(ticket)
        
        # Calculate priority distribution
        priority_counts = {}
        for ticket in recent_tickets:
            priority = ticket.priority.value
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        # Calculate status distribution
        status_counts = stats.get('tickets_by_status', {})
        
        # Provider breakdown
        provider_breakdown = stats.get('tickets_by_provider', {})
        
        return {
            "status": "success",
            "dashboard": {
                "summary": {
                    "total_tickets": stats.get('total_tickets', 0),
                    "open_tickets": status_counts.get('open', 0),
                    "in_progress_tickets": status_counts.get('in_progress', 0),
                    "resolved_tickets": status_counts.get('resolved', 0),
                    "overdue_tickets": len(overdue_tickets),
                    "connected_providers": len(ticketing_manager.connectors)
                },
                "priority_distribution": priority_counts,
                "status_distribution": status_counts,
                "provider_breakdown": provider_breakdown,
                "recent_tickets": [
                    {
                        "provider": ticket.provider.value,
                        "ticket_id": ticket.ticket_id,
                        "title": ticket.title,
                        "status": ticket.status.value,
                        "priority": ticket.priority.value,
                        "assignee": ticket.assignee,
                        "created_at": ticket.created_at.isoformat(),
                        "due_date": ticket.due_date.isoformat() if ticket.due_date else None,
                        "tags": ticket.tags
                    }
                    for ticket in recent_tickets[:20]
                ],
                "overdue_tickets": [
                    {
                        "provider": ticket.provider.value,
                        "ticket_id": ticket.ticket_id,
                        "title": ticket.title,
                        "priority": ticket.priority.value,
                        "assignee": ticket.assignee,
                        "due_date": ticket.due_date.isoformat(),
                        "days_overdue": (datetime.now() - ticket.due_date).days
                    }
                    for ticket in overdue_tickets[:10]
                ],
                "last_updated": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting ticketing dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_ticketing_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get ticketing statistics"""
    try:
        stats = await ticketing_manager.get_ticket_statistics()
        
        return {
            "status": "success",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting ticketing stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def list_providers(current_user: dict = Depends(get_current_user)):
    """List available ticketing providers"""
    try:
        providers = [
            {
                "value": provider.value,
                "name": provider.value.replace("_", " ").title(),
                "description": f"{provider.value.replace('_', ' ')} ticketing system integration"
            }
            for provider in TicketingProvider
        ]
        
        return {
            "status": "success",
            "providers": providers,
            "total": len(providers)
        }
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statuses")
async def list_statuses(current_user: dict = Depends(get_current_user)):
    """List available ticket statuses"""
    try:
        statuses = [
            {
                "value": status.value,
                "name": status.value.replace("_", " ").title(),
                "description": f"Ticket {status.value.replace('_', ' ')} status"
            }
            for status in TicketStatus
        ]
        
        return {
            "status": "success",
            "statuses": statuses,
            "total": len(statuses)
        }
    except Exception as e:
        logger.error(f"Error listing statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priorities")
async def list_priorities(current_user: dict = Depends(get_current_user)):
    """List available ticket priorities"""
    try:
        priorities = [
            {
                "value": priority.value,
                "name": priority.value.title(),
                "description": f"Ticket {priority.value} priority level"
            }
            for priority in TicketPriority
        ]
        
        return {
            "status": "success",
            "priorities": priorities,
            "total": len(priorities)
        }
    except Exception as e:
        logger.error(f"Error listing priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/connectors/{provider}")
async def unregister_ticketing_connector(
    provider: str,
    current_user: dict = Depends(get_current_user)
):
    """Unregister a ticketing connector"""
    try:
        provider = provider.lower()
        
        if provider not in ticketing_manager.connectors:
            raise HTTPException(status_code=404, detail=f"Ticketing connector not found: {provider}")
        
        # Check if it's the default provider
        if provider == ticketing_manager.default_provider:
            # Set new default if there are other connectors
            remaining_providers = [p for p in ticketing_manager.connectors.keys() if p != provider]
            if remaining_providers:
                ticketing_manager.default_provider = remaining_providers[0]
            else:
                ticketing_manager.default_provider = None
        
        # Remove connector
        del ticketing_manager.connectors[provider]
        
        # Clean up last sync time
        if provider in ticketing_manager.last_sync_times:
            del ticketing_manager.last_sync_times[provider]
        
        return {
            "status": "success",
            "message": f"{provider.upper()} ticketing connector unregistered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering ticketing connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))
