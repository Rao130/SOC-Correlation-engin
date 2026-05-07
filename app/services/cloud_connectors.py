"""
Cloud Platform Connectors
Integration with AWS, Azure, and GCP security services
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

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

@dataclass
class CloudSecurityEvent:
    """Cloud security event data structure"""
    provider: CloudProvider
    service: str
    event_type: str
    severity: str
    timestamp: datetime
    resource_id: str
    resource_type: str
    account_id: str
    region: str
    details: Dict[str, Any]
    raw_event: Dict[str, Any]

class CloudConnector(ABC):
    """Abstract base class for cloud connectors"""
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.last_sync = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with cloud provider"""
        pass
    
    @abstractmethod
    async def get_security_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get security events from cloud provider"""
        pass
    
    @abstractmethod
    async def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get vulnerability findings"""
        pass
    
    @abstractmethod
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        pass
    
    @abstractmethod
    async def remediate_issue(self, issue_id: str, action: str) -> Dict[str, Any]:
        """Remediate security issue"""
        pass

class AWSConnector(CloudConnector):
    """AWS Security Hub and GuardDuty connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.access_key = credentials.get('access_key')
        self.secret_key = credentials.get('secret_key')
        self.region = credentials.get('region', 'us-east-1')
        self.session_token = credentials.get('session_token')
    
    async def authenticate(self) -> bool:
        """Authenticate with AWS"""
        try:
            # Simulate AWS authentication
            # In real implementation, use boto3
            logger.info(f"Authenticating with AWS in region {self.region}")
            await asyncio.sleep(0.5)  # Simulate API call
            
            # Validate credentials
            if not self.access_key or not self.secret_key:
                raise ValueError("AWS access key and secret key required")
            
            logger.info("AWS authentication successful")
            return True
        except Exception as e:
            logger.error(f"AWS authentication failed: {e}")
            return False
    
    async def get_security_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get security events from AWS Security Hub and GuardDuty"""
        try:
            events = []
            
            # Simulate GuardDuty findings
            guardduty_events = await self._get_guardduty_findings(start_time, end_time)
            events.extend(guardduty_events)
            
            # Simulate Security Hub findings
            security_hub_events = await self._get_security_hub_findings(start_time, end_time)
            events.extend(security_hub_events)
            
            # Simulate CloudTrail events
            cloudtrail_events = await self._get_cloudtrail_events(start_time, end_time)
            events.extend(cloudtrail_events)
            
            logger.info(f"Retrieved {len(events)} security events from AWS")
            return events
        except Exception as e:
            logger.error(f"Error getting AWS security events: {e}")
            return []
    
    async def _get_guardduty_findings(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get GuardDuty findings"""
        # Simulate GuardDuty API calls
        await asyncio.sleep(1)
        
        sample_findings = [
            {
                "id": "gd-001",
                "type": "Backdoor:EC2/C&CActivity.B",
                "severity": "HIGH",
                "resource": "i-1234567890abcdef0",
                "resource_type": "AWS::EC2::Instance",
                "description": "EC2 instance communicating with known C&C server",
                "details": {
                    "ip_address": "192.0.2.1",
                    "domain": "malicious.example.com",
                    "port": 443
                }
            },
            {
                "id": "gd-002",
                "type": "UnauthorizedAccess:IAMUser/ConsoleLogin",
                "severity": "MEDIUM",
                "resource": "arn:aws:iam::123456789012:user/testuser",
                "resource_type": "AWS::IAM::User",
                "description": "Console login from unusual location",
                "details": {
                    "source_ip": "203.0.113.1",
                    "location": "Unknown",
                    "user_agent": "Mozilla/5.0..."
                }
            }
        ]
        
        events = []
        for finding in sample_findings:
            event = CloudSecurityEvent(
                provider=CloudProvider.AWS,
                service="GuardDuty",
                event_type=finding["type"],
                severity=finding["severity"],
                timestamp=datetime.now() - timedelta(hours=2),
                resource_id=finding["resource"],
                resource_type=finding["resource_type"],
                account_id="123456789012",
                region=self.region,
                details=finding["details"],
                raw_event=finding
            )
            events.append(event)
        
        return events
    
    async def _get_security_hub_findings(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get Security Hub findings"""
        # Simulate Security Hub API calls
        await asyncio.sleep(1)
        
        sample_findings = [
            {
                "id": "sh-001",
                "type": "S3 Bucket Public Read",
                "severity": "HIGH",
                "resource": "arn:aws:s3:::public-bucket",
                "resource_type": "AWS::S3::Bucket",
                "description": "S3 bucket configured for public read access",
                "details": {
                    "bucket_name": "public-bucket",
                    "policy": "PublicRead",
                    "permissions": ["READ"]
                }
            }
        ]
        
        events = []
        for finding in sample_findings:
            event = CloudSecurityEvent(
                provider=CloudProvider.AWS,
                service="SecurityHub",
                event_type=finding["type"],
                severity=finding["severity"],
                timestamp=datetime.now() - timedelta(hours=4),
                resource_id=finding["resource"],
                resource_type=finding["resource_type"],
                account_id="123456789012",
                region=self.region,
                details=finding["details"],
                raw_event=finding
            )
            events.append(event)
        
        return events
    
    async def _get_cloudtrail_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get CloudTrail events"""
        # Simulate CloudTrail API calls
        await asyncio.sleep(0.5)
        
        sample_events = [
            {
                "id": "ct-001",
                "type": "RootAccountUsage",
                "severity": "HIGH",
                "resource": "arn:aws:iam::123456789012:root",
                "resource_type": "AWS::IAM::User",
                "description": "Root account used for console login",
                "details": {
                    "user": "root",
                    "action": "ConsoleLogin",
                    "source_ip": "198.51.100.1",
                    "event_name": "ConsoleLogin"
                }
            }
        ]
        
        events = []
        for event in sample_events:
            security_event = CloudSecurityEvent(
                provider=CloudProvider.AWS,
                service="CloudTrail",
                event_type=event["type"],
                severity=event["severity"],
                timestamp=datetime.now() - timedelta(hours=1),
                resource_id=event["resource"],
                resource_type=event["resource_type"],
                account_id="123456789012",
                region=self.region,
                details=event["details"],
                raw_event=event
            )
            events.append(security_event)
        
        return events
    
    async def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get AWS Inspector vulnerabilities"""
        try:
            # Simulate Inspector API calls
            await asyncio.sleep(1)
            
            vulnerabilities = [
                {
                    "id": "ins-001",
                    "resource_id": "i-1234567890abcdef0",
                    "resource_type": "AWS::EC2::Instance",
                    "severity": "HIGH",
                    "title": "CVE-2021-44228 - Log4j Remote Code Execution",
                    "description": "Apache Log4j vulnerable to remote code execution",
                    "package": "log4j-core",
                    "version": "2.14.0",
                    "fixed_version": "2.15.0"
                },
                {
                    "id": "ins-002",
                    "resource_id": "i-0987654321fedcba0",
                    "resource_type": "AWS::EC2::Instance",
                    "severity": "MEDIUM",
                    "title": "Outdated OpenSSL Version",
                    "description": "OpenSSL version has known vulnerabilities",
                    "package": "openssl",
                    "version": "1.1.1f",
                    "fixed_version": "1.1.1k"
                }
            ]
            
            logger.info(f"Retrieved {len(vulnerabilities)} vulnerabilities from AWS Inspector")
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error getting AWS vulnerabilities: {e}")
            return []
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get AWS Config compliance status"""
        try:
            # Simulate AWS Config API calls
            await asyncio.sleep(1)
            
            compliance_status = {
                "overall_compliance": "NON_COMPLIANT",
                "compliant_resources": 45,
                "non_compliant_resources": 8,
                "total_resources": 53,
                "compliance_percentage": 84.9,
                "rules": [
                    {
                        "rule_name": "s3-bucket-public-read-prohibited",
                        "compliance_type": "NON_COMPLIANT",
                        "resource_count": 2,
                        "severity": "HIGH"
                    },
                    {
                        "rule_name": "ec2-instance-managed-by-systems-manager",
                        "compliance_type": "COMPLIANT",
                        "resource_count": 15,
                        "severity": "MEDIUM"
                    },
                    {
                        "rule_name": "iam-password-policy",
                        "compliance_type": "COMPLIANT",
                        "resource_count": 1,
                        "severity": "LOW"
                    }
                ]
            }
            
            logger.info("Retrieved AWS compliance status")
            return compliance_status
        except Exception as e:
            logger.error(f"Error getting AWS compliance status: {e}")
            return {}
    
    async def remediate_issue(self, issue_id: str, action: str) -> Dict[str, Any]:
        """Remediate AWS security issue"""
        try:
            # Simulate remediation actions
            await asyncio.sleep(2)
            
            remediation_actions = {
                "isolate_instance": {
                    "action": "isolate_ec2_instance",
                    "status": "success",
                    "details": "EC2 instance isolated from network"
                },
                "disable_user": {
                    "action": "disable_iam_user",
                    "status": "success",
                    "details": "IAM user access disabled"
                },
                "delete_public_bucket": {
                    "action": "remove_public_access",
                    "status": "success",
                    "details": "S3 bucket public access removed"
                }
            }
            
            result = remediation_actions.get(action, {
                "action": action,
                "status": "failed",
                "details": "Unknown remediation action"
            })
            
            result["issue_id"] = issue_id
            result["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Remediated AWS issue {issue_id} with action {action}")
            return result
        except Exception as e:
            logger.error(f"Error remediating AWS issue: {e}")
            return {"status": "failed", "error": str(e)}

class AzureConnector(CloudConnector):
    """Azure Security Center and Sentinel connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.tenant_id = credentials.get('tenant_id')
        self.client_id = credentials.get('client_id')
        self.client_secret = credentials.get('client_secret')
        self.subscription_id = credentials.get('subscription_id')
    
    async def authenticate(self) -> bool:
        """Authenticate with Azure"""
        try:
            # Simulate Azure authentication
            # In real implementation, use azure-identity
            logger.info(f"Authenticating with Azure tenant {self.tenant_id}")
            await asyncio.sleep(0.5)
            
            if not all([self.tenant_id, self.client_id, self.client_secret, self.subscription_id]):
                raise ValueError("Azure tenant_id, client_id, client_secret, and subscription_id required")
            
            logger.info("Azure authentication successful")
            return True
        except Exception as e:
            logger.error(f"Azure authentication failed: {e}")
            return False
    
    async def get_security_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get security events from Azure Security Center and Sentinel"""
        try:
            events = []
            
            # Simulate Security Center alerts
            security_center_events = await self._get_security_center_alerts(start_time, end_time)
            events.extend(security_center_events)
            
            # Simulate Sentinel incidents
            sentinel_events = await self._get_sentinel_incidents(start_time, end_time)
            events.extend(sentinel_events)
            
            logger.info(f"Retrieved {len(events)} security events from Azure")
            return events
        except Exception as e:
            logger.error(f"Error getting Azure security events: {e}")
            return []
    
    async def _get_security_center_alerts(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get Security Center alerts"""
        await asyncio.sleep(1)
        
        sample_alerts = [
            {
                "id": "az-sc-001",
                "type": "Suspicious process execution",
                "severity": "HIGH",
                "resource": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/test-vm",
                "resource_type": "Microsoft.Compute/virtualMachines",
                "description": "Suspicious PowerShell execution detected",
                "details": {
                    "process": "powershell.exe",
                    "command_line": "Invoke-Mimikatz",
                    "user": "SYSTEM"
                }
            }
        ]
        
        events = []
        for alert in sample_alerts:
            event = CloudSecurityEvent(
                provider=CloudProvider.AZURE,
                service="SecurityCenter",
                event_type=alert["type"],
                severity=alert["severity"],
                timestamp=datetime.now() - timedelta(hours=3),
                resource_id=alert["resource"],
                resource_type=alert["resource_type"],
                account_id=self.subscription_id,
                region="global",
                details=alert["details"],
                raw_event=alert
            )
            events.append(event)
        
        return events
    
    async def _get_sentinel_incidents(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get Sentinel incidents"""
        await asyncio.sleep(1)
        
        sample_incidents = [
            {
                "id": "az-sentinel-001",
                "type": "Brute force attack detected",
                "severity": "MEDIUM",
                "resource": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/test-rg/providers/Microsoft.Network/publicIPs/test-ip",
                "resource_type": "Microsoft.Network/publicIPAddresses",
                "description": "Multiple failed RDP login attempts detected",
                "details": {
                    "source_ips": ["203.0.113.1", "203.0.113.2"],
                    "target_port": 3389,
                    "attempt_count": 50
                }
            }
        ]
        
        events = []
        for incident in sample_incidents:
            event = CloudSecurityEvent(
                provider=CloudProvider.AZURE,
                service="Sentinel",
                event_type=incident["type"],
                severity=incident["severity"],
                timestamp=datetime.now() - timedelta(hours=2),
                resource_id=incident["resource"],
                resource_type=incident["resource_type"],
                account_id=self.subscription_id,
                region="global",
                details=incident["details"],
                raw_event=incident
            )
            events.append(event)
        
        return events
    
    async def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get Azure Defender vulnerabilities"""
        try:
            await asyncio.sleep(1)
            
            vulnerabilities = [
                {
                    "id": "az-def-001",
                    "resource_id": "/subscriptions/12345678-1234-1234-1234-123456789012/resourceGroups/test-rg/providers/Microsoft.Compute/virtualMachines/test-vm",
                    "resource_type": "Microsoft.Compute/virtualMachines",
                    "severity": "HIGH",
                    "title": "Missing security updates",
                    "description": "VM has missing critical security updates",
                    "missing_updates": 5,
                    "critical_updates": 2
                }
            ]
            
            logger.info(f"Retrieved {len(vulnerabilities)} vulnerabilities from Azure Defender")
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error getting Azure vulnerabilities: {e}")
            return []
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get Azure Policy compliance status"""
        try:
            await asyncio.sleep(1)
            
            compliance_status = {
                "overall_compliance": "COMPLIANT",
                "compliant_resources": 67,
                "non_compliant_resources": 3,
                "total_resources": 70,
                "compliance_percentage": 95.7,
                "policies": [
                    {
                        "policy_name": "Storage accounts should disable public network access",
                        "compliance_type": "COMPLIANT",
                        "resource_count": 12,
                        "severity": "HIGH"
                    },
                    {
                        "policy_name": "Virtual machines should be backed up",
                        "compliance_type": "NON_COMPLIANT",
                        "resource_count": 3,
                        "severity": "MEDIUM"
                    }
                ]
            }
            
            logger.info("Retrieved Azure compliance status")
            return compliance_status
        except Exception as e:
            logger.error(f"Error getting Azure compliance status: {e}")
            return {}
    
    async def remediate_issue(self, issue_id: str, action: str) -> Dict[str, Any]:
        """Remediate Azure security issue"""
        try:
            await asyncio.sleep(2)
            
            remediation_actions = {
                "isolate_vm": {
                    "action": "isolate_virtual_machine",
                    "status": "success",
                    "details": "Virtual machine isolated from network"
                },
                "stop_vm": {
                    "action": "stop_virtual_machine",
                    "status": "success",
                    "details": "Virtual machine stopped"
                },
                "update_firewall": {
                    "action": "update_network_security_group",
                    "status": "success",
                    "details": "Network security group rules updated"
                }
            }
            
            result = remediation_actions.get(action, {
                "action": action,
                "status": "failed",
                "details": "Unknown remediation action"
            })
            
            result["issue_id"] = issue_id
            result["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Remediated Azure issue {issue_id} with action {action}")
            return result
        except Exception as e:
            logger.error(f"Error remediating Azure issue: {e}")
            return {"status": "failed", "error": str(e)}

class GCPConnector(CloudConnector):
    """Google Cloud Security Command Center connector"""
    
    def __init__(self, credentials: Dict[str, Any]):
        super().__init__(credentials)
        self.project_id = credentials.get('project_id')
        self.service_account_key = credentials.get('service_account_key')
    
    async def authenticate(self) -> bool:
        """Authenticate with GCP"""
        try:
            # Simulate GCP authentication
            # In real implementation, use google-cloud libraries
            logger.info(f"Authenticating with GCP project {self.project_id}")
            await asyncio.sleep(0.5)
            
            if not self.project_id:
                raise ValueError("GCP project_id required")
            
            logger.info("GCP authentication successful")
            return True
        except Exception as e:
            logger.error(f"GCP authentication failed: {e}")
            return False
    
    async def get_security_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get security events from GCP Security Command Center"""
        try:
            events = []
            
            # Simulate SCC findings
            scc_events = await self._get_scc_findings(start_time, end_time)
            events.extend(scc_events)
            
            # Simulate Cloud Audit Logs
            audit_events = await self._get_audit_logs(start_time, end_time)
            events.extend(audit_events)
            
            logger.info(f"Retrieved {len(events)} security events from GCP")
            return events
        except Exception as e:
            logger.error(f"Error getting GCP security events: {e}")
            return []
    
    async def _get_scc_findings(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get Security Command Center findings"""
        await asyncio.sleep(1)
        
        sample_findings = [
            {
                "id": "gcp-scc-001",
                "type": "Public IP Address",
                "severity": "MEDIUM",
                "resource": "//compute.googleapis.com/projects/test-project/zones/us-central1-a/instances/test-vm",
                "resource_type": "google.compute.Instance",
                "description": "Compute instance has public IP address",
                "details": {
                    "public_ip": "203.0.113.100",
                    "internal_ip": "10.128.0.2",
                    "network_tags": ["web-server"]
                }
            }
        ]
        
        events = []
        for finding in sample_findings:
            event = CloudSecurityEvent(
                provider=CloudProvider.GCP,
                service="SecurityCommandCenter",
                event_type=finding["type"],
                severity=finding["severity"],
                timestamp=datetime.now() - timedelta(hours=5),
                resource_id=finding["resource"],
                resource_type=finding["resource_type"],
                account_id=self.project_id,
                region="us-central1",
                details=finding["details"],
                raw_event=finding
            )
            events.append(event)
        
        return events
    
    async def _get_audit_logs(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get Cloud Audit Logs"""
        await asyncio.sleep(0.5)
        
        sample_logs = [
            {
                "id": "gcp-audit-001",
                "type": "Service Account Key Creation",
                "severity": "HIGH",
                "resource": "//iam.googleapis.com/projects/test-project/serviceAccounts/test@test-project.iam.gserviceaccount.com",
                "resource_type": "google.iam.ServiceAccount",
                "description": "New service account key created",
                "details": {
                    "user": "user@example.com",
                    "key_id": "1234567890abcdef",
                    "method": "google.iam.admin.v1.CreateServiceAccountKey"
                }
            }
        ]
        
        events = []
        for log in sample_logs:
            event = CloudSecurityEvent(
                provider=CloudProvider.GCP,
                service="CloudAuditLogs",
                event_type=log["type"],
                severity=log["severity"],
                timestamp=datetime.now() - timedelta(hours=1),
                resource_id=log["resource"],
                resource_type=log["resource_type"],
                account_id=self.project_id,
                region="global",
                details=log["details"],
                raw_event=log
            )
            events.append(event)
        
        return events
    
    async def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        """Get GCP Container Analysis vulnerabilities"""
        try:
            await asyncio.sleep(1)
            
            vulnerabilities = [
                {
                    "id": "gcp-vuln-001",
                    "resource_id": "gcr.io/test-project/web-app:latest",
                    "resource_type": "ContainerImage",
                    "severity": "HIGH",
                    "title": "CVE-2021-44228 - Log4j RCE",
                    "description": "Container image contains vulnerable Log4j version",
                    "package": "log4j-core",
                    "version": "2.14.0",
                    "fixed_version": "2.15.0"
                }
            ]
            
            logger.info(f"Retrieved {len(vulnerabilities)} vulnerabilities from GCP")
            return vulnerabilities
        except Exception as e:
            logger.error(f"Error getting GCP vulnerabilities: {e}")
            return []
    
    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get GCP Asset Inventory compliance status"""
        try:
            await asyncio.sleep(1)
            
            compliance_status = {
                "overall_compliance": "COMPLIANT",
                "compliant_assets": 89,
                "non_compliant_assets": 2,
                "total_assets": 91,
                "compliance_percentage": 97.8,
                "policies": [
                    {
                        "policy_name": "Require Shielded VM",
                        "compliance_type": "COMPLIANT",
                        "resource_count": 15,
                        "severity": "MEDIUM"
                    },
                    {
                        "policy_name": "Disable Legacy APIs",
                        "compliance_type": "NON_COMPLIANT",
                        "resource_count": 2,
                        "severity": "LOW"
                    }
                ]
            }
            
            logger.info("Retrieved GCP compliance status")
            return compliance_status
        except Exception as e:
            logger.error(f"Error getting GCP compliance status: {e}")
            return {}
    
    async def remediate_issue(self, issue_id: str, action: str) -> Dict[str, Any]:
        """Remediate GCP security issue"""
        try:
            await asyncio.sleep(2)
            
            remediation_actions = {
                "disable_service_account": {
                    "action": "disable_service_account_key",
                    "status": "success",
                    "details": "Service account key disabled"
                },
                "delete_public_ip": {
                    "action": "remove_public_ip",
                    "status": "success",
                    "details": "Public IP address removed from instance"
                },
                "update_firewall": {
                    "action": "update_firewall_rules",
                    "status": "success",
                    "details": "Firewall rules updated"
                }
            }
            
            result = remediation_actions.get(action, {
                "action": action,
                "status": "failed",
                "details": "Unknown remediation action"
            })
            
            result["issue_id"] = issue_id
            result["timestamp"] = datetime.now().isoformat()
            
            logger.info(f"Remediated GCP issue {issue_id} with action {action}")
            return result
        except Exception as e:
            logger.error(f"Error remediating GCP issue: {e}")
            return {"status": "failed", "error": str(e)}

class CloudConnectorManager:
    """Manager for all cloud connectors"""
    
    def __init__(self):
        self.connectors = {}
        self.last_sync_times = {}
    
    def register_connector(self, provider: str, connector: CloudConnector):
        """Register a cloud connector"""
        self.connectors[provider] = connector
        logger.info(f"Registered {provider} connector")
    
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
    
    async def get_all_security_events(self, start_time: datetime, end_time: datetime) -> List[CloudSecurityEvent]:
        """Get security events from all providers"""
        all_events = []
        
        for provider, connector in self.connectors.items():
            try:
                events = await connector.get_security_events(start_time, end_time)
                all_events.extend(events)
                logger.info(f"Retrieved {len(events)} events from {provider}")
            except Exception as e:
                logger.error(f"Error getting events from {provider}: {e}")
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        return all_events
    
    async def get_all_vulnerabilities(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get vulnerabilities from all providers"""
        vulnerabilities = {}
        
        for provider, connector in self.connectors.items():
            try:
                vulns = await connector.get_vulnerabilities()
                vulnerabilities[provider] = vulns
                logger.info(f"Retrieved {len(vulns)} vulnerabilities from {provider}")
            except Exception as e:
                logger.error(f"Error getting vulnerabilities from {provider}: {e}")
                vulnerabilities[provider] = []
        
        return vulnerabilities
    
    async def get_all_compliance_status(self) -> Dict[str, Dict[str, Any]]:
        """Get compliance status from all providers"""
        compliance_status = {}
        
        for provider, connector in self.connectors.items():
            try:
                status = await connector.get_compliance_status()
                compliance_status[provider] = status
                logger.info(f"Retrieved compliance status from {provider}")
            except Exception as e:
                logger.error(f"Error getting compliance status from {provider}: {e}")
                compliance_status[provider] = {}
        
        return compliance_status
    
    async def remediate_all_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remediate issues across all providers"""
        results = []
        
        for issue in issues:
            provider = issue.get('provider')
            issue_id = issue.get('issue_id')
            action = issue.get('action')
            
            if provider in self.connectors:
                try:
                    result = await self.connectors[provider].remediate_issue(issue_id, action)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error remediating issue {issue_id} from {provider}: {e}")
                    results.append({
                        "issue_id": issue_id,
                        "provider": provider,
                        "status": "failed",
                        "error": str(e)
                    })
        
        return results

# Global cloud connector manager
cloud_connector_manager = CloudConnectorManager()
