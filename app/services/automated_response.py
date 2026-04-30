import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from enum import Enum

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import logger

class ResponseAction(Enum):
    BLOCK = "block"
    QUARANTINE = "quarantine"
    ISOLATE = "isolate"
    MONITOR = "monitor"
    NOTIFY = "notify"
    IGNORE = "ignore"

class AutomatedResponse:
    """Automated incident response and remediation"""
    
    def __init__(self):
        self.db = db_manager
        self.response_rules = {}
        self.action_history = []
        self._load_rules()
    
    def _load_rules(self):
        """Load automated response rules"""
        try:
            # Predefined response rules
            self.response_rules = {
                'high_risk_ip': {
                    'action': ResponseAction.BLOCK,
                    'conditions': {'risk_score': 80, 'entity_type': 'ip'},
                    'description': 'Automatically block high-risk IP addresses',
                    'automation_level': 'full'
                },
                'malware_hash': {
                    'action': ResponseAction.QUARANTINE,
                    'conditions': {'threat_intelligence_score': 70, 'entity_type': 'hash'},
                    'description': 'Quarantine files with known malware signatures',
                    'automation_level': 'full'
                },
                'phishing_domain': {
                    'action': ResponseAction.BLOCK,
                    'conditions': {'threat_intelligence_score': 60, 'entity_type': 'domain'},
                    'description': 'Block access to known phishing domains',
                    'automation_level': 'full'
                },
                'repeated_failed_logins': {
                    'action': ResponseAction.BLOCK,
                    'conditions': {'frequency': 5, 'timeframe': '1h'},
                    'description': 'Block IP after 5 failed login attempts',
                    'automation_level': 'full'
                },
                'suspicious_file_hash': {
                    'action': ResponseAction.QUARANTINE,
                    'conditions': {'threat_intelligence_score': 40, 'entity_type': 'hash'},
                    'description': 'Quarantine suspicious files for manual review',
                    'automation_level': 'semi'
                },
                'off_hours_admin_access': {
                    'action': ResponseAction.MONITOR,
                    'conditions': {'time_pattern': 'off_hours', 'user_role': 'admin'},
                    'description': 'Monitor admin access during off hours',
                    'automation_level': 'semi'
                },
                'brute_force_detected': {
                    'action': ResponseAction.BLOCK,
                    'conditions': {'pattern_type': 'brute_force', 'frequency': 10},
                    'description': 'Block source IP immediately',
                    'automation_level': 'full'
                },
                'data_exfiltration_pattern': {
                    'action': ResponseAction.ISOLATE,
                    'conditions': {'pattern_type': 'data_exfiltration', 'data_volume': 'large'},
                    'description': 'Isolate system and investigate potential data breach',
                    'automation_level': 'full'
                }
            }
            
            logger.info(f"Loaded {len(self.response_rules)} automated response rules")
            
        except Exception as e:
            logger.error(f"Error loading response rules: {e}")
    
    async def evaluate_alert(self, alert: Dict) -> Dict[str, Any]:
        """Evaluate alert and determine automated response"""
        try:
            # Check each rule
            matched_rules = []
            
            for rule_name, rule_config in self.response_rules.items():
                if await self._check_rule_conditions(alert, rule_config.get('conditions', {})):
                    matched_rules.append({
                        'rule': rule_name,
                        'action': rule_config.get('action'),
                        'description': rule_config.get('description'),
                        'automation_level': rule_config.get('automation_level'),
                        'confidence': 0.8
                    })
            
            if not matched_rules:
                return {
                    'alert_id': alert.get('alertId'),
                    'evaluation': 'no_rules_matched',
                    'recommended_action': ResponseAction.NOTIFY,
                    'confidence': 0.5,
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Select the highest confidence rule
            best_rule = max(matched_rules, key=lambda x: x.get('confidence', 0))
            
            # Execute automated response
            if best_rule.get('automation_level') == 'full':
                result = await self._execute_automated_response(alert, best_rule)
            elif best_rule.get('automation_level') == 'semi':
                result = await self._execute_semi_automated_response(alert, best_rule)
            else:
                result = await self._execute_monitoring_response(alert, best_rule)
            
            result['matched_rules'] = matched_rules
            result['selected_rule'] = best_rule
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating alert {alert.get('alertId')}: {e}")
            return {'error': str(e)}
    
    async def _check_rule_conditions(self, alert: Dict, conditions: Dict) -> bool:
        """Check if alert meets rule conditions"""
        try:
            # Risk score condition
            if 'risk_score' in conditions:
                alert_score = alert.get('criticalityScore', 50)
                if alert_score >= conditions['risk_score']:
                    return True
            
            # Entity type condition
            if 'entity_type' in conditions:
                entities = alert.get('entities', [])
                for entity in entities:
                    if entity.get('type') == conditions['entity_type']:
                        return True
            
            # Threat intelligence score condition
            if 'threat_intelligence_score' in conditions:
                # This would need to be populated by threat intelligence service
                ti_score = alert.get('threatIntelligenceScore', 0)
                if ti_score >= conditions['threat_intelligence_score']:
                    return True
            
            # Frequency condition
            if 'frequency' in conditions:
                # This would need historical analysis
                return True  # Simplified for demo
            
            # Time pattern condition
            if 'time_pattern' in conditions:
                # This would need time-based analysis
                return True  # Simplified for demo
            
            # Pattern type condition
            if 'pattern_type' in conditions:
                # This would need pattern recognition
                return True  # Simplified for demo
            
            # User role condition
            if 'user_role' in conditions:
                # This would need user context
                return True  # Simplified for demo
            
            # Data volume condition
            if 'data_volume' in conditions:
                # This would need data analysis
                return True  # Simplified for demo
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking rule conditions: {e}")
            return False
    
    async def _execute_automated_response(self, alert: Dict, rule: Dict) -> Dict[str, Any]:
        """Execute fully automated response"""
        try:
            action = rule.get('action')
            
            if action == ResponseAction.BLOCK:
                return await self._block_entity(alert, rule)
            elif action == ResponseAction.QUARANTINE:
                return await self._quarantine_entity(alert, rule)
            elif action == ResponseAction.ISOLATE:
                return await self._isolate_entity(alert, rule)
            else:
                return await self._notify_response(alert, rule)
                
        except Exception as e:
            logger.error(f"Error executing automated response: {e}")
            return {'error': str(e)}
    
    async def _execute_semi_automated_response(self, alert: Dict, rule: Dict) -> Dict[str, Any]:
        """Execute semi-automated response"""
        try:
            action = rule.get('action')
            
            if action == ResponseAction.BLOCK:
                return await self._block_entity(alert, rule, require_approval=True)
            elif action == ResponseAction.QUARANTINE:
                return await self._quarantine_entity(alert, rule, require_approval=True)
            else:
                return await self._notify_response(alert, rule, require_approval=True)
                
        except Exception as e:
            logger.error(f"Error executing semi-automated response: {e}")
            return {'error': str(e)}
    
    async def _execute_monitoring_response(self, alert: Dict, rule: Dict) -> Dict[str, Any]:
        """Execute monitoring response"""
        try:
            # Create monitoring task
            monitoring_task = {
                'alert_id': alert.get('alertId'),
                'action': ResponseAction.MONITOR,
                'description': f"Monitor {rule.get('description')}",
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'requires_review': True
            }
            
            # Save to database
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert.get('alertId')},
                {'$set': {
                    'automatedResponse': monitoring_task,
                    'status': 'monitoring',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            return {
                'action': ResponseAction.MONITOR,
                'description': f"Monitoring alert: {rule.get('description')}",
                'monitoring_task_id': monitoring_task.get('task_id', f"monitor_{alert.get('alertId')}"),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing monitoring response: {e}")
            return {'error': str(e)}
    
    async def _block_entity(self, alert: Dict, rule: Dict, require_approval: bool = False) -> Dict[str, Any]:
        """Block entity (IP, domain, hash)"""
        try:
            entities = alert.get('entities', [])
            blocked_entities = []
            
            for entity in entities:
                if entity.get('type') in ['ip', 'domain']:
                    blocked_entities.append({
                        'entity': entity.get('value'),
                        'type': entity.get('type'),
                        'blocked_at': datetime.utcnow().isoformat(),
                        'rule': rule.get('description'),
                        'permanent': False
                    })
            
            # Update alert with block action
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert.get('alertId')},
                {'$set': {
                    'automatedResponse': {
                        'action': ResponseAction.BLOCK,
                        'blocked_entities': blocked_entities,
                        'description': f"Blocked {len(blocked_entities)} entities",
                        'executed_at': datetime.utcnow().isoformat()
                    },
                    'status': 'auto_resolved',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            # Log action
            await self._log_response_action(alert, ResponseAction.BLOCK, rule, require_approval)
            
            return {
                'action': ResponseAction.BLOCK,
                'blocked_entities': blocked_entities,
                'description': f"Blocked {len(blocked_entities)} entities",
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error blocking entities: {e}")
            return {'error': str(e)}
    
    async def _quarantine_entity(self, alert: Dict, rule: Dict, require_approval: bool = False) -> Dict[str, Any]:
        """Quarantine suspicious files"""
        try:
            entities = alert.get('entities', [])
            quarantined_entities = []
            
            for entity in entities:
                if entity.get('type') == 'hash':
                    quarantined_entities.append({
                        'entity': entity.get('value'),
                        'type': entity.get('type'),
                        'quarantined_at': datetime.utcnow().isoformat(),
                        'rule': rule.get('description'),
                        'location': f'/quarantine/{entity.get("value")[:8]}'
                    })
            
            # Update alert with quarantine action
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert.get('alertId')},
                {'$set': {
                    'automatedResponse': {
                        'action': ResponseAction.QUARANTINE,
                        'quarantined_entities': quarantined_entities,
                        'description': f"Quarantined {len(quarantined_entities)} files",
                        'executed_at': datetime.utcnow().isoformat()
                    },
                    'status': 'quarantined',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            # Log action
            await self._log_response_action(alert, ResponseAction.QUARANTINE, rule, require_approval)
            
            return {
                'action': ResponseAction.QUARANTINE,
                'quarantined_entities': quarantined_entities,
                'description': f"Quarantined {len(quarantined_entities)} files",
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error quarantining entities: {e}")
            return {'error': str(e)}
    
    async def _isolate_entity(self, alert: Dict, rule: Dict) -> Dict[str, Any]:
        """Isolate system from potential breach"""
        try:
            # Create isolation task
            isolation_task = {
                'alert_id': alert.get('alertId'),
                'action': ResponseAction.ISOLATE,
                'description': f"Isolate system due to: {rule.get('description')}",
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'affected_systems': ['network', 'database', 'file_system'],
                'requires_review': True
            }
            
            # Update alert with isolation action
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert.get('alertId')},
                {'$set': {
                    'automatedResponse': isolation_task,
                    'status': 'isolated',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            # Log action
            await self._log_response_action(alert, ResponseAction.ISOLATE, rule)
            
            return {
                'action': ResponseAction.ISOLATE,
                'description': f"System isolated due to: {rule.get('description')}",
                'isolation_task_id': isolation_task.get('task_id', f"isolate_{alert.get('alertId')}"),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error isolating system: {e}")
            return {'error': str(e)}
    
    async def _notify_response(self, alert: Dict, rule: Dict, require_approval: bool = False) -> Dict[str, Any]:
        """Send notification and create review task"""
        try:
            # Create notification task
            notification_task = {
                'alert_id': alert.get('alertId'),
                'action': ResponseAction.NOTIFY,
                'description': f"Notification required: {rule.get('description')}",
                'created_at': datetime.utcnow().isoformat(),
                'status': 'pending_review',
                'requires_approval': require_approval,
                'notification_sent': False
            }
            
            # Update alert with notification action
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert.get('alertId')},
                {'$set': {
                    'automatedResponse': notification_task,
                    'status': 'pending_review',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            # Log action
            await self._log_response_action(alert, ResponseAction.NOTIFY, rule, require_approval)
            
            return {
                'action': ResponseAction.NOTIFY,
                'description': f"Notification sent: {rule.get('description')}",
                'notification_task_id': notification_task.get('task_id', f"notify_{alert.get('alertId')}"),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return {'error': str(e)}
    
    async def _log_response_action(self, alert: Dict, action: ResponseAction, rule: Dict, require_approval: bool = False):
        """Log automated response action"""
        try:
            action_log = {
                'alert_id': alert.get('alertId'),
                'action': action.value,
                'rule_description': rule.get('description'),
                'automation_level': rule.get('automation_level'),
                'executed_at': datetime.utcnow().isoformat(),
                'requires_approval': require_approval,
                'entities': alert.get('entities', []),
                'alert_severity': alert.get('severity'),
                'alert_source': alert.get('source')
            }
            
            # Save to action history
            self.action_history.append(action_log)
            
            # Save to database
            response_collection = self.db.get_database().get('automated_responses', MockCollection([]))
            await response_collection.insert_one(action_log)
            
            logger.info(f"Logged automated response: {action.value} for alert {alert.get('alertId')}")
            
        except Exception as e:
            logger.error(f"Error logging response action: {e}")
    
    async def get_response_history(self, limit: int = 50) -> Dict[str, Any]:
        """Get automated response history"""
        try:
            response_collection = self.db.get_database().get('automated_responses', MockCollection([]))
            history = await response_collection.find().sort('executed_at', -1).limit(limit).to_list(length=None)
            
            return {
                'history': history,
                'total_count': len(self.action_history),
                'limit': limit,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def get_pending_approvals(self) -> Dict[str, Any]:
        """Get pending approval tasks"""
        try:
            alerts_collection = self.db.get_database().alerts
            pending_alerts = await alerts_collection.find({
                'status': {'$in': ['pending_review', 'quarantined', 'isolated']}
            }).to_list(length=None)
            
            return {
                'pending_approvals': pending_alerts,
                'count': len(pending_alerts),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def approve_action(self, alert_id: str, action: str, analyst_id: str) -> Dict[str, Any]:
        """Approve or reject automated response action"""
        try:
            # Update alert status
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert_id},
                {'$set': {
                    'status': 'investigating',
                    'analystId': analyst_id,
                    'approvedAction': action,
                    'approvedAt': datetime.utcnow().isoformat(),
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            logger.info(f"Approved {action} for alert {alert_id} by analyst {analyst_id}")
            
            return {
                'alert_id': alert_id,
                'action': action,
                'analyst_id': analyst_id,
                'approved': True,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
