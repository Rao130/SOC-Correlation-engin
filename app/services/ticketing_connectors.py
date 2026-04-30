"""
Ticketing System Connectors
Integration with ServiceNow, Jira, and other ticketing systems
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class TicketingProvider(Enum):
    SERVICENOW = "servicenow"
    JIRA = "jira"
    REMEDY = "remedy"
    ZENDESK = "zendesk"

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Ticket:
    """Ticket data structure"""
    provider: TicketingProvider
    ticket_id: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    assignee: Optional[str]
    reporter: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    tags: List[str]
    attachments: List[str]
    custom_fields: Dict[str, Any]
    raw_ticket: Dict[str, Any]

@dataclass
class TicketComment:
    """Ticket comment data structure"""
    ticket_id: str
    comment_id: str
    author: str
    body: str
    created_at: datetime
    is_internal: bool
    attachments: List[str]

class TicketingConnector(ABC):
    """Abstract base class for ticketing connectors"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.last_sync = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with ticketing provider"""
        pass
    
    @abstractmethod
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Ticket:
        """Create a new ticket"""
        pass
    
    @abstractmethod
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket by ID"""
        pass
    
    @abstractmethod
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Ticket:
        """Update ticket"""
        pass
    
    @abstractmethod
    async def add_comment(self, ticket_id: str, comment: str, internal: bool = False) -> TicketComment:
        """Add comment to ticket"""
        pass
    
    @abstractmethod
    async def search_tickets(self, query: str, limit: int = 50) -> List[Ticket]:
        """Search tickets"""
        pass
    
    @abstractmethod
    async def get_tickets_by_status(self, status: TicketStatus, limit: int = 50) -> List[Ticket]:
        """Get tickets by status"""
        pass

class ServiceNowConnector(TicketingConnector):
    """ServiceNow connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.instance_url = credentials.get('instance_url')
        self.username = credentials.get('username')
        self.password = credentials.get('password')
        self.table = credentials.get('table', 'incident')
    
    async def authenticate(self) -> bool:
        """Authenticate with ServiceNow"""
        try:
            # Simulate ServiceNow authentication
            # In real implementation, use ServiceNow REST API
            logger.info(f"Authenticating with ServiceNow instance: {self.instance_url}")
            await asyncio.sleep(0.5)
            
            if not all([self.instance_url, self.username, self.password]):
                raise ValueError("ServiceNow instance_url, username, and password required")
            
            logger.info("ServiceNow authentication successful")
            return True
        except Exception as e:
            logger.error(f"ServiceNow authentication failed: {e}")
            return False
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Ticket:
        """Create ticket in ServiceNow"""
        try:
            # Simulate ServiceNow API call
            await asyncio.sleep(1)
            
            # Generate ticket ID (ServiceNow format: INC0010010)
            ticket_id = f"INC{datetime.now().strftime('%y%m%d%H%M%S')}"
            
            ticket = Ticket(
                provider=TicketingProvider.SERVICENOW,
                ticket_id=ticket_id,
                title=ticket_data.get('title', 'Untitled Incident'),
                description=ticket_data.get('description', ''),
                status=TicketStatus.OPEN,
                priority=TicketPriority(ticket_data.get('priority', 'medium')),
                assignee=ticket_data.get('assignee'),
                reporter=ticket_data.get('reporter', 'system'),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=3) if ticket_data.get('priority') == 'critical' else None,
                tags=ticket_data.get('tags', []),
                attachments=ticket_data.get('attachments', []),
                custom_fields=ticket_data.get('custom_fields', {}),
                raw_ticket=ticket_data
            )
            
            logger.info(f"Created ServiceNow ticket: {ticket_id}")
            return ticket
        except Exception as e:
            logger.error(f"Error creating ServiceNow ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket from ServiceNow"""
        try:
            # Simulate ServiceNow API call
            await asyncio.sleep(0.5)
            
            # Return sample ticket
            return Ticket(
                provider=TicketingProvider.SERVICENOW,
                ticket_id=ticket_id,
                title="Security Incident - Malware Detection",
                description="Malware detected on endpoint workstation-01",
                status=TicketStatus.OPEN,
                priority=TicketPriority.HIGH,
                assignee="security.team",
                reporter="soc.system",
                created_at=datetime.now() - timedelta(hours=2),
                updated_at=datetime.now() - timedelta(minutes=30),
                due_date=datetime.now() + timedelta(days=1),
                tags=["security", "malware", "high-priority"],
                attachments=["malware_sample.zip"],
                custom_fields={"category": "security", "subcategory": "malware"},
                raw_ticket={}
            )
        except Exception as e:
            logger.error(f"Error getting ServiceNow ticket: {e}")
            return None
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Ticket:
        """Update ticket in ServiceNow"""
        try:
            await asyncio.sleep(1)
            
            # Get existing ticket and update it
            ticket = await self.get_ticket(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket {ticket_id} not found")
            
            # Apply updates
            if 'status' in updates:
                ticket.status = TicketStatus(updates['status'])
            if 'priority' in updates:
                ticket.priority = TicketPriority(updates['priority'])
            if 'assignee' in updates:
                ticket.assignee = updates['assignee']
            
            ticket.updated_at = datetime.now()
            
            logger.info(f"Updated ServiceNow ticket: {ticket_id}")
            return ticket
        except Exception as e:
            logger.error(f"Error updating ServiceNow ticket: {e}")
            raise
    
    async def add_comment(self, ticket_id: str, comment: str, internal: bool = False) -> TicketComment:
        """Add comment to ServiceNow ticket"""
        try:
            await asyncio.sleep(0.5)
            
            comment_id = f"comment_{datetime.now().timestamp()}"
            
            return TicketComment(
                ticket_id=ticket_id,
                comment_id=comment_id,
                author="soc.system",
                body=comment,
                created_at=datetime.now(),
                is_internal=internal,
                attachments=[]
            )
        except Exception as e:
            logger.error(f"Error adding comment to ServiceNow ticket: {e}")
            raise
    
    async def search_tickets(self, query: str, limit: int = 50) -> List[Ticket]:
        """Search tickets in ServiceNow"""
        try:
            await asyncio.sleep(1)
            
            # Return sample search results
            return [
                Ticket(
                    provider=TicketingProvider.SERVICENOW,
                    ticket_id="INC0010010",
                    title="Security Incident - Phishing Attack",
                    description="Phishing email detected and blocked",
                    status=TicketStatus.IN_PROGRESS,
                    priority=TicketPriority.MEDIUM,
                    assignee="security.team",
                    reporter="email.system",
                    created_at=datetime.now() - timedelta(hours=6),
                    updated_at=datetime.now() - timedelta(minutes=15),
                    due_date=datetime.now() + timedelta(days=2),
                    tags=["phishing", "email"],
                    attachments=[],
                    custom_fields={},
                    raw_ticket={}
                )
            ]
        except Exception as e:
            logger.error(f"Error searching ServiceNow tickets: {e}")
            return []
    
    async def get_tickets_by_status(self, status: TicketStatus, limit: int = 50) -> List[Ticket]:
        """Get ServiceNow tickets by status"""
        try:
            await asyncio.sleep(1)
            
            # Return sample tickets by status
            return [
                Ticket(
                    provider=TicketingProvider.SERVICENOW,
                    ticket_id="INC0010011",
                    title="Network Security Alert",
                    description="Suspicious network activity detected",
                    status=status,
                    priority=TicketPriority.HIGH,
                    assignee="network.team",
                    reporter="ids.system",
                    created_at=datetime.now() - timedelta(hours=4),
                    updated_at=datetime.now() - timedelta(minutes=45),
                    due_date=datetime.now() + timedelta(hours=8),
                    tags=["network", "security"],
                    attachments=[],
                    custom_fields={},
                    raw_ticket={}
                )
            ]
        except Exception as e:
            logger.error(f"Error getting ServiceNow tickets by status: {e}")
            return []

class JiraConnector(TicketingConnector):
    """Jira connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.base_url = credentials.get('base_url')
        self.username = credentials.get('username')
        self.api_token = credentials.get('api_token')
        self.project_key = credentials.get('project_key', 'SEC')
    
    async def authenticate(self) -> bool:
        """Authenticate with Jira"""
        try:
            # Simulate Jira authentication
            # In real implementation, use Jira REST API
            logger.info(f"Authenticating with Jira: {self.base_url}")
            await asyncio.sleep(0.5)
            
            if not all([self.base_url, self.username, self.api_token]):
                raise ValueError("Jira base_url, username, and api_token required")
            
            logger.info("Jira authentication successful")
            return True
        except Exception as e:
            logger.error(f"Jira authentication failed: {e}")
            return False
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> Ticket:
        """Create ticket in Jira"""
        try:
            # Simulate Jira API call
            await asyncio.sleep(1)
            
            # Generate ticket ID (Jira format: SEC-123)
            ticket_id = f"{self.project_key}-{datetime.now().strftime%Y%m%d%H%M%S}"
            
            ticket = Ticket(
                provider=TicketingProvider.JIRA,
                ticket_id=ticket_id,
                title=ticket_data.get('title', 'Untitled Issue'),
                description=ticket_data.get('description', ''),
                status=TicketStatus.OPEN,
                priority=TicketPriority(ticket_data.get('priority', 'medium')),
                assignee=ticket_data.get('assignee'),
                reporter=ticket_data.get('reporter', 'soc-system'),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                due_date=datetime.now() + timedelta(days=3) if ticket_data.get('priority') == 'critical' else None,
                tags=ticket_data.get('labels', []),
                attachments=ticket_data.get('attachments', []),
                custom_fields={
                    'issue_type': ticket_data.get('issue_type', 'Task'),
                    'components': ticket_data.get('components', [])
                },
                raw_ticket=ticket_data
            )
            
            logger.info(f"Created Jira ticket: {ticket_id}")
            return ticket
        except Exception as e:
            logger.error(f"Error creating Jira ticket: {e}")
            raise
    
    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket from Jira"""
        try:
            # Simulate Jira API call
            await asyncio.sleep(0.5)
            
            # Return sample ticket
            return Ticket(
                provider=TicketingProvider.JIRA,
                ticket_id=ticket_id,
                title="Security Vulnerability - CVE-2024-1234",
                description="Critical vulnerability detected in web application",
                status=TicketStatus.IN_PROGRESS,
                priority=TicketPriority.CRITICAL,
                assignee="dev.team",
                reporter="security.scanner",
                created_at=datetime.now() - timedelta(hours=8),
                updated_at=datetime.now() - timedelta(minutes=20),
                due_date=datetime.now() + timedelta(hours=4),
                tags=["vulnerability", "cve", "web"],
                attachments=["vulnerability_report.pdf"],
                custom_fields={
                    'issue_type': 'Bug',
                    'components': ['Web Application']
                },
                raw_ticket={}
            )
        except Exception as e:
            logger.error(f"Error getting Jira ticket: {e}")
            return None
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Ticket:
        """Update ticket in Jira"""
        try:
            await asyncio.sleep(1)
            
            # Get existing ticket and update it
            ticket = await self.get_ticket(ticket_id)
            if not ticket:
                raise ValueError(f"Ticket {ticket_id} not found")
            
            # Apply updates
            if 'status' in updates:
                ticket.status = TicketStatus(updates['status'])
            if 'priority' in updates:
                ticket.priority = TicketPriority(updates['priority'])
            if 'assignee' in updates:
                ticket.assignee = updates['assignee']
            
            ticket.updated_at = datetime.now()
            
            logger.info(f"Updated Jira ticket: {ticket_id}")
            return ticket
        except Exception as e:
            logger.error(f"Error updating Jira ticket: {e}")
            raise
    
    async def add_comment(self, ticket_id: str, comment: str, internal: bool = False) -> TicketComment:
        """Add comment to Jira ticket"""
        try:
            await asyncio.sleep(0.5)
            
            comment_id = f"comment_{datetime.now().timestamp()}"
            
            return TicketComment(
                ticket_id=ticket_id,
                comment_id=comment_id,
                author="soc-system",
                body=comment,
                created_at=datetime.now(),
                is_internal=internal,
                attachments=[]
            )
        except Exception as e:
            logger.error(f"Error adding comment to Jira ticket: {e}")
            raise
    
    async def search_tickets(self, query: str, limit: int = 50) -> List[Ticket]:
        """Search tickets in Jira"""
        try:
            await asyncio.sleep(1)
            
            # Return sample search results
            return [
                Ticket(
                    provider=TicketingProvider.JIRA,
                    ticket_id="SEC-456",
                    title="Access Control Review",
                    description="Quarterly access control review required",
                    status=TicketStatus.OPEN,
                    priority=TicketPriority.MEDIUM,
                    assignee="compliance.team",
                    reporter="audit.system",
                    created_at=datetime.now() - timedelta(days=2),
                    updated_at=datetime.now() - timedelta(hours=6),
                    due_date=datetime.now() + timedelta(days=7),
                    tags=["compliance", "access"],
                    attachments=[],
                    custom_fields={
                        'issue_type': 'Task',
                        'components': ['Access Control']
                    },
                    raw_ticket={}
                )
            ]
        except Exception as e:
            logger.error(f"Error searching Jira tickets: {e}")
            return []
    
    async def get_tickets_by_status(self, status: TicketStatus, limit: int = 50) -> List[Ticket]:
        """Get Jira tickets by status"""
        try:
            await asyncio.sleep(1)
            
            # Return sample tickets by status
            return [
                Ticket(
                    provider=TicketingProvider.JIRA,
                    ticket_id="SEC-789",
                    title="Security Audit Findings",
                    description="Security audit identified several issues",
                    status=status,
                    priority=TicketPriority.HIGH,
                    assignee="security.team",
                    reporter="audit.system",
                    created_at=datetime.now() - timedelta(days=1),
                    updated_at=datetime.now() - timedelta(hours=3),
                    due_date=datetime.now() + timedelta(days=5),
                    tags=["audit", "findings"],
                    attachments=[],
                    custom_fields={
                        'issue_type': 'Task',
                        'components': ['Security']
                    },
                    raw_ticket={}
                )
            ]
        except Exception as e:
            logger.error(f"Error getting Jira tickets by status: {e}")
            return []

class TicketingManager:
    """Manager for all ticketing connectors"""
    
    def __init__(self):
        self.connectors = {}
        self.default_provider = None
        self.last_sync_times = {}
    
    def register_connector(self, provider: str, connector: TicketingConnector, is_default: bool = False):
        """Register a ticketing connector"""
        self.connectors[provider] = connector
        if is_default:
            self.default_provider = provider
        logger.info(f"Registered {provider} ticketing connector")
    
    async def authenticate_all(self) -> Dict[str, bool]:
        """Authenticate all registered connectors"""
        results = {}
        
        for provider, connector in self.connectors.items():
            try:
                results[provider] = await connector.authenticate()
            except Exception as e:
                logger.error(f"Error authenticating {provider}: {e}")
                results[provider] = False
        
        return results
    
    async def create_ticket(self, ticket_data: Dict[str, Any], provider: Optional[str] = None) -> Ticket:
        """Create ticket using specified or default provider"""
        target_provider = provider or self.default_provider
        
        if not target_provider or target_provider not in self.connectors:
            raise ValueError(f"Ticketing provider {target_provider} not available")
        
        connector = self.connectors[target_provider]
        return await connector.create_ticket(ticket_data)
    
    async def get_ticket(self, ticket_id: str, provider: str) -> Optional[Ticket]:
        """Get ticket from specific provider"""
        if provider not in self.connectors:
            raise ValueError(f"Ticketing provider {provider} not available")
        
        connector = self.connectors[provider]
        return await connector.get_ticket(ticket_id)
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any], provider: str) -> Ticket:
        """Update ticket in specific provider"""
        if provider not in self.connectors:
            raise ValueError(f"Ticketing provider {provider} not available")
        
        connector = self.connectors[provider]
        return await connector.update_ticket(ticket_id, updates)
    
    async def add_comment(self, ticket_id: str, comment: str, provider: str, internal: bool = False) -> TicketComment:
        """Add comment to ticket in specific provider"""
        if provider not in self.connectors:
            raise ValueError(f"Ticketing provider {provider} not available")
        
        connector = self.connectors[provider]
        return await connector.add_comment(ticket_id, comment, internal)
    
    async def search_all_tickets(self, query: str, limit: int = 50) -> Dict[str, List[Ticket]]:
        """Search tickets across all providers"""
        results = {}
        
        for provider, connector in self.connectors.items():
            try:
                tickets = await connector.search_tickets(query, limit)
                results[provider] = tickets
                logger.info(f"Found {len(tickets)} tickets in {provider}")
            except Exception as e:
                logger.error(f"Error searching tickets in {provider}: {e}")
                results[provider] = []
        
        return results
    
    async def get_all_tickets_by_status(self, status: TicketStatus, limit: int = 50) -> Dict[str, List[Ticket]]:
        """Get tickets by status across all providers"""
        results = {}
        
        for provider, connector in self.connectors.items():
            try:
                tickets = await connector.get_tickets_by_status(status, limit)
                results[provider] = tickets
                logger.info(f"Found {len(tickets)} {status.value} tickets in {provider}")
            except Exception as e:
                logger.error(f"Error getting tickets by status in {provider}: {e}")
                results[provider] = []
        
        return results
    
    async def get_ticket_statistics(self) -> Dict[str, Any]:
        """Get ticket statistics across all providers"""
        try:
            stats = {
                "total_tickets": 0,
                "tickets_by_status": {},
                "tickets_by_priority": {},
                "tickets_by_provider": {},
                "recent_tickets": [],
                "overdue_tickets": []
            }
            
            # Get tickets for each status
            for status in TicketStatus:
                status_tickets = await self.get_all_tickets_by_status(status, 100)
                status_count = sum(len(tickets) for tickets in status_tickets.values())
                stats["tickets_by_status"][status.value] = status_count
                stats["total_tickets"] += status_count
            
            # Get recent tickets (last 24 hours)
            for provider, connector in self.connectors.items():
                try:
                    recent_tickets = await connector.search_tickets("created >= -24h", 20)
                    stats["tickets_by_provider"][provider] = len(recent_tickets)
                    stats["recent_tickets"].extend(recent_tickets)
                except Exception as e:
                    logger.error(f"Error getting recent tickets from {provider}: {e}")
            
            # Sort recent tickets by creation time
            stats["recent_tickets"].sort(key=lambda x: x.created_at, reverse=True)
            stats["recent_tickets"] = stats["recent_tickets"][:20]
            
            return stats
        except Exception as e:
            logger.error(f"Error getting ticket statistics: {e}")
            return {}

# Global ticketing manager instance
ticketing_manager = TicketingManager()
