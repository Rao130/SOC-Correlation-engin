"""
SOAR (Security Orchestration, Automation and Response) Engine
Automated security response playbooks and incident management
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging
from dataclasses import dataclass
import uuid

logger = logging.getLogger(__name__)

class PlaybookStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PlaybookAction:
    """Individual action within a playbook"""
    id: str
    name: str
    action_type: str
    parameters: Dict[str, Any]
    status: ActionStatus = ActionStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class PlaybookExecution:
    """Playbook execution instance"""
    id: str
    playbook_id: str
    trigger_data: Dict[str, Any]
    status: PlaybookStatus = PlaybookStatus.PENDING
    actions: List[PlaybookAction] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.context is None:
            self.context = {}

class SOAREngine:
    """Main SOAR Engine for automated security response"""
    
    def __init__(self):
        self.playbooks = {}
        self.executions = {}
        self.action_handlers = {}
        self._register_default_handlers()
        self._load_default_playbooks()
    
    def _register_default_handlers(self):
        """Register default action handlers"""
        self.action_handlers.update({
            'block_ip': self._block_ip_handler,
            'isolate_endpoint': self._isolate_endpoint_handler,
            'disable_user': self._disable_user_handler,
            'create_ticket': self._create_ticket_handler,
            'send_email': self._send_email_handler,
            'run_script': self._run_script_handler,
            'enrich_threat': self._enrich_threat_handler,
            'quarantine_file': self._quarantine_file_handler,
            'update_firewall': self._update_firewall_handler,
            'notify_team': self._notify_team_handler
        })
    
    def _load_default_playbooks(self):
        """Load default security playbooks"""
        
        # Malware Detection Playbook
        self.register_playbook('malware_response', {
            'name': 'Malware Detection Response',
            'description': 'Automated response to malware detection',
            'triggers': ['malware_detected', 'virus_found'],
            'actions': [
                {
                    'id': 'isolate_endpoint',
                    'name': 'Isolate Affected Endpoint',
                    'action_type': 'isolate_endpoint',
                    'parameters': {'endpoint': '${trigger.endpoint}'}
                },
                {
                    'id': 'quarantine_file',
                    'name': 'Quarantine Malicious File',
                    'action_type': 'quarantine_file',
                    'parameters': {'file_hash': '${trigger.file_hash}'},
                    'dependencies': ['isolate_endpoint']
                },
                {
                    'id': 'block_c2',
                    'name': 'Block C2 Communication',
                    'action_type': 'block_ip',
                    'parameters': {'ip': '${trigger.c2_ip}'},
                    'dependencies': ['isolate_endpoint']
                },
                {
                    'id': 'create_incident',
                    'name': 'Create Security Incident',
                    'action_type': 'create_ticket',
                    'parameters': {
                        'title': 'Malware Detection - ${trigger.endpoint}',
                        'severity': 'high',
                        'description': 'Malware detected on endpoint ${trigger.endpoint}'
                    },
                    'dependencies': ['isolate_endpoint']
                },
                {
                    'id': 'notify_team',
                    'name': 'Notify Security Team',
                    'action_type': 'send_email',
                    'parameters': {
                        'to': 'security-team@company.com',
                        'subject': 'Malware Incident - ${trigger.endpoint}',
                        'body': 'Malware detected and isolated. Endpoint: ${trigger.endpoint}'
                    },
                    'dependencies': ['create_incident']
                }
            ]
        })
        
        # Phishing Attack Playbook
        self.register_playbook('phishing_response', {
            'name': 'Phishing Attack Response',
            'description': 'Automated response to phishing attacks',
            'triggers': ['phishing_detected', 'suspicious_email'],
            'actions': [
                {
                    'id': 'block_sender',
                    'name': 'Block Malicious Sender',
                    'action_type': 'disable_user',
                    'parameters': {'user': '${trigger.sender_email}'}
                },
                {
                    'id': 'quarantine_emails',
                    'name': 'Quarantine Similar Emails',
                    'action_type': 'run_script',
                    'parameters': {
                        'script': 'quarantine_phishing_emails.py',
                        'sender': '${trigger.sender_email}',
                        'subject_pattern': '${trigger.subject}'
                    }
                },
                {
                    'id': 'notify_users',
                    'name': 'Notify Affected Users',
                    'action_type': 'send_email',
                    'parameters': {
                        'to': '${trigger.recipients}',
                        'subject': 'Security Alert: Phishing Email Detected',
                        'body': 'A phishing email was detected and blocked. Please be cautious.'
                    }
                },
                {
                    'id': 'create_ticket',
                    'name': 'Create Phishing Investigation Ticket',
                    'action_type': 'create_ticket',
                    'parameters': {
                        'title': 'Phishing Attack - ${trigger.sender_email}',
                        'severity': 'medium',
                        'description': 'Phishing email detected from ${trigger.sender_email}'
                    }
                }
            ]
        })
        
        # Brute Force Attack Playbook
        self.register_playbook('brute_force_response', {
            'name': 'Brute Force Attack Response',
            'description': 'Automated response to brute force attacks',
            'triggers': ['brute_force_detected', 'multiple_failed_logins'],
            'actions': [
                {
                    'id': 'block_source_ip',
                    'name': 'Block Source IP',
                    'action_type': 'block_ip',
                    'parameters': {'ip': '${trigger.source_ip}'}
                },
                {
                    'id': 'lock_account',
                    'name': 'Lock Target Account',
                    'action_type': 'disable_user',
                    'parameters': {'user': '${trigger.target_user}'},
                    'dependencies': ['block_source_ip']
                },
                {
                    'id': 'enrich_ip',
                    'name': 'Enrich IP Intelligence',
                    'action_type': 'enrich_threat',
                    'parameters': {'ip': '${trigger.source_ip}'}
                },
                {
                    'id': 'create_alert',
                    'name': 'Create Security Alert',
                    'action_type': 'create_ticket',
                    'parameters': {
                        'title': 'Brute Force Attack - ${trigger.source_ip}',
                        'severity': 'high',
                        'description': 'Brute force attack detected from ${trigger.source_ip} targeting ${trigger.target_user}'
                    }
                }
            ]
        })
    
    def register_playbook(self, playbook_id: str, playbook_config: Dict[str, Any]):
        """Register a new playbook"""
        self.playbooks[playbook_id] = playbook_config
        logger.info(f"Playbook '{playbook_id}' registered successfully")
    
    def trigger_playbook(self, playbook_id: str, trigger_data: Dict[str, Any]) -> str:
        """Trigger a playbook execution"""
        if playbook_id not in self.playbooks:
            raise ValueError(f"Playbook '{playbook_id}' not found")
        
        execution_id = str(uuid.uuid4())
        playbook = self.playbooks[playbook_id]
        
        # Create actions
        actions = []
        for action_config in playbook['actions']:
            action = PlaybookAction(
                id=action_config['id'],
                name=action_config['name'],
                action_type=action_config['action_type'],
                parameters=self._substitute_parameters(
                    action_config['parameters'], 
                    trigger_data
                ),
                dependencies=action_config.get('dependencies', [])
            )
            actions.append(action)
        
        # Create execution
        execution = PlaybookExecution(
            id=execution_id,
            playbook_id=playbook_id,
            trigger_data=trigger_data,
            actions=actions,
            start_time=datetime.now(),
            context=trigger_data.copy()
        )
        
        self.executions[execution_id] = execution
        
        # Start execution asynchronously
        asyncio.create_task(self._execute_playbook(execution_id))
        
        logger.info(f"Playbook '{playbook_id}' triggered with execution ID: {execution_id}")
        return execution_id
    
    async def _execute_playbook(self, execution_id: str):
        """Execute a playbook"""
        execution = self.executions[execution_id]
        execution.status = PlaybookStatus.RUNNING
        
        try:
            # Execute actions in dependency order
            completed_actions = set()
            
            while len(completed_actions) < len(execution.actions):
                # Find actions that can be executed
                ready_actions = [
                    action for action in execution.actions
                    if action.status == ActionStatus.PENDING and
                       all(dep in completed_actions for dep in action.dependencies)
                ]
                
                if not ready_actions:
                    # Check for circular dependencies or stuck execution
                    pending_actions = [a for a in execution.actions if a.status == ActionStatus.PENDING]
                    if pending_actions:
                        logger.error(f"Execution stuck: {len(pending_actions)} actions pending")
                        execution.status = PlaybookStatus.FAILED
                        return
                
                # Execute ready actions concurrently
                tasks = [self._execute_action(execution_id, action.id) for action in ready_actions]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update completed actions
                for action in execution.actions:
                    if action.status in [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.SKIPPED]:
                        completed_actions.add(action.id)
            
            # Check if all actions completed successfully
            failed_actions = [a for a in execution.actions if a.status == ActionStatus.FAILED]
            if failed_actions:
                execution.status = PlaybookStatus.FAILED
            else:
                execution.status = PlaybookStatus.COMPLETED
                
        except Exception as e:
            logger.error(f"Playbook execution failed: {e}")
            execution.status = PlaybookStatus.FAILED
        finally:
            execution.end_time = datetime.now()
    
    async def _execute_action(self, execution_id: str, action_id: str):
        """Execute a single action"""
        execution = self.executions[execution_id]
        action = next(a for a in execution.actions if a.id == action_id)
        
        action.status = ActionStatus.RUNNING
        start_time = datetime.now()
        
        try:
            # Get the action handler
            handler = self.action_handlers.get(action.action_type)
            if not handler:
                raise ValueError(f"No handler found for action type: {action.action_type}")
            
            # Execute the action
            if asyncio.iscoroutinefunction(handler):
                result = await handler(execution, action)
            else:
                result = handler(execution, action)
            
            action.result = result
            action.status = ActionStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Action '{action_id}' failed: {e}")
            action.error_message = str(e)
            action.status = ActionStatus.FAILED
        
        finally:
            action.execution_time = (datetime.now() - start_time).total_seconds()
    
    def _substitute_parameters(self, parameters: Dict[str, Any], trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute parameters with trigger data"""
        def substitute_value(value):
            if isinstance(value, str):
                # Replace ${trigger.field} with actual values
                import re
                pattern = r'\$\{trigger\.([^}]+)\}'
                matches = re.findall(pattern, value)
                
                for match in matches:
                    placeholder = f"${{trigger.{match}}}"
                    actual_value = self._get_nested_value(trigger_data, match)
                    if actual_value is not None:
                        value = value.replace(placeholder, str(actual_value))
            
            return value
        
        return {k: substitute_value(v) for k, v in parameters.items()}
    
    def _get_nested_value(self, data: Dict[str, Any], path: str):
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    # Default Action Handlers
    async def _block_ip_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Block IP address handler"""
        ip = action.parameters.get('ip')
        logger.info(f"Blocking IP: {ip}")
        
        # Simulate IP blocking
        await asyncio.sleep(1)
        
        return {
            'status': 'success',
            'ip': ip,
            'blocked_at': datetime.now().isoformat(),
            'rule_id': f'BLOCK_{ip.replace(".", "_")}'
        }
    
    async def _isolate_endpoint_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Isolate endpoint handler"""
        endpoint = action.parameters.get('endpoint')
        logger.info(f"Isolating endpoint: {endpoint}")
        
        # Simulate endpoint isolation
        await asyncio.sleep(2)
        
        return {
            'status': 'success',
            'endpoint': endpoint,
            'isolated_at': datetime.now().isoformat(),
            'network_access': False
        }
    
    async def _disable_user_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Disable user account handler"""
        user = action.parameters.get('user')
        logger.info(f"Disabling user: {user}")
        
        # Simulate user disable
        await asyncio.sleep(1)
        
        return {
            'status': 'success',
            'user': user,
            'disabled_at': datetime.now().isoformat(),
            'account_status': 'disabled'
        }
    
    async def _create_ticket_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Create ticket handler"""
        title = action.parameters.get('title')
        severity = action.parameters.get('severity')
        description = action.parameters.get('description')
        
        logger.info(f"Creating ticket: {title}")
        
        # Simulate ticket creation
        await asyncio.sleep(1)
        
        ticket_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
        
        return {
            'status': 'success',
            'ticket_id': ticket_id,
            'title': title,
            'severity': severity,
            'description': description,
            'created_at': datetime.now().isoformat()
        }
    
    async def _send_email_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Send email handler"""
        to = action.parameters.get('to')
        subject = action.parameters.get('subject')
        body = action.parameters.get('body')
        
        logger.info(f"Sending email to: {to}")
        
        # Simulate email sending
        await asyncio.sleep(0.5)
        
        return {
            'status': 'success',
            'to': to,
            'subject': subject,
            'sent_at': datetime.now().isoformat(),
            'message_id': f"MSG-{uuid.uuid4().hex[:8]}"
        }
    
    async def _run_script_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Run script handler"""
        script = action.parameters.get('script')
        logger.info(f"Running script: {script}")
        
        # Simulate script execution
        await asyncio.sleep(2)
        
        return {
            'status': 'success',
            'script': script,
            'executed_at': datetime.now().isoformat(),
            'exit_code': 0,
            'output': 'Script executed successfully'
        }
    
    async def _enrich_threat_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Enrich threat intelligence handler"""
        ip = action.parameters.get('ip')
        logger.info(f"Enriching threat intelligence for IP: {ip}")
        
        # Simulate threat enrichment
        await asyncio.sleep(1)
        
        return {
            'status': 'success',
            'ip': ip,
            'reputation': 'malicious',
            'confidence': 0.95,
            'sources': ['VirusTotal', 'AbuseIPDB', 'OTX'],
            'first_seen': '2024-01-15T10:30:00Z',
            'last_seen': datetime.now().isoformat()
        }
    
    async def _quarantine_file_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Quarantine file handler"""
        file_hash = action.parameters.get('file_hash')
        logger.info(f"Quarantining file: {file_hash}")
        
        # Simulate file quarantine
        await asyncio.sleep(1)
        
        return {
            'status': 'success',
            'file_hash': file_hash,
            'quarantined_at': datetime.now().isoformat(),
            'quarantine_path': f'/quarantine/{file_hash}'
        }
    
    async def _update_firewall_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Update firewall handler"""
        logger.info("Updating firewall rules")
        
        # Simulate firewall update
        await asyncio.sleep(1)
        
        return {
            'status': 'success',
            'updated_at': datetime.now().isoformat(),
            'rules_applied': 1
        }
    
    async def _notify_team_handler(self, execution: PlaybookExecution, action: PlaybookAction) -> Dict[str, Any]:
        """Notify team handler"""
        logger.info("Notifying security team")
        
        # Simulate team notification
        await asyncio.sleep(0.5)
        
        return {
            'status': 'success',
            'notified_at': datetime.now().isoformat(),
            'channels': ['email', 'slack', 'teams']
        }
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            'execution_id': execution.id,
            'playbook_id': execution.playbook_id,
            'status': execution.status.value,
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'actions': [
                {
                    'id': action.id,
                    'name': action.name,
                    'status': action.status.value,
                    'execution_time': action.execution_time,
                    'result': action.result,
                    'error_message': action.error_message
                }
                for action in execution.actions
            ]
        }
    
    def list_playbooks(self) -> List[Dict[str, Any]]:
        """List all available playbooks"""
        return [
            {
                'id': playbook_id,
                'name': playbook['name'],
                'description': playbook['description'],
                'triggers': playbook['triggers'],
                'action_count': len(playbook['actions'])
            }
            for playbook_id, playbook in self.playbooks.items()
        ]
    
    def get_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent executions"""
        executions = sorted(
            self.executions.values(),
            key=lambda x: x.start_time or datetime.min,
            reverse=True
        )
        
        return [
            {
                'execution_id': exec.id,
                'playbook_id': exec.playbook_id,
                'status': exec.status.value,
                'start_time': exec.start_time.isoformat() if exec.start_time else None,
                'end_time': exec.end_time.isoformat() if exec.end_time else None,
                'action_count': len(exec.actions),
                'completed_actions': len([a for a in exec.actions if a.status == ActionStatus.COMPLETED])
            }
            for exec in executions[:limit]
        ]

# Global SOAR engine instance
soar_engine = SOAREngine()
