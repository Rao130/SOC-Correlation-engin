import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import hashlib
import json
from pathlib import Path

from app.core.config import settings
from app.core.database import get_db
from app.utils.logger import setup_logging

logger = setup_logging()

class Forensics:
    """Digital forensics and incident investigation service"""
    
    def __init__(self):
        self.db = get_db()
        self.evidence_store = Path("data/forensics")
        self.evidence_store.mkdir(exist_ok=True)
        self.case_files = {}
        self._initialize_case_templates()
    
    def _initialize_case_templates(self):
        """Initialize forensics case templates"""
        try:
            self.case_files = {
                'malware_investigation': {
                    'name': 'Malware Investigation',
                    'description': 'Investigation of malware-related security incident',
                    'checklist': [
                        'Identify affected systems',
                        'Collect malware samples',
                        'Analyze attack vector',
                        'Determine persistence mechanism',
                        'Assess data exfiltration',
                        'Document IOCs',
                        'Review network logs'
                    ],
                    'evidence_types': ['hashes', 'files', 'logs', 'memory_dump', 'network_traffic']
                },
                'phishing_analysis': {
                    'name': 'Phishing Attack Analysis',
                    'description': 'Analysis of phishing campaign and victim impact',
                    'checklist': [
                        'Analyze email headers',
                        'Examine URLs and redirects',
                        'Check SSL certificates',
                        'Identify target credentials',
                        'Analyze landing page',
                        'Document attack infrastructure',
                        'Assess victim data exposure',
                        'Review email logs'
                    ],
                    'evidence_types': ['emails', 'urls', 'screenshots', 'headers', 'ssl_certs']
                },
                'data_breach_investigation': {
                    'name': 'Data Breach Investigation',
                    'description': 'Investigation of suspected data breach incident',
                    'checklist': [
                        'Identify breach scope',
                        'Determine data types exposed',
                        'Assess breach timeline',
                        'Identify affected users',
                        'Review access logs',
                        'Analyze data exfiltration methods',
                        'Check for insider threat indicators',
                        'Document compliance requirements',
                        'Notify affected parties'
                    ],
                    'evidence_types': ['logs', 'user_data', 'access_records', 'system_logs', 'network_data']
                },
                'network_intrusion': {
                    'name': 'Network Intrusion Investigation',
                    'description': 'Investigation of unauthorized network access',
                    'checklist': [
                        'Analyze network traffic patterns',
                        'Review authentication logs',
                        'Identify source IP addresses',
                        'Examine session data',
                        'Check for lateral movement',
                        'Review firewall logs',
                        'Analyze malware artifacts',
                        'Document attack timeline',
                        'Assess system modifications'
                    ],
                    'evidence_types': ['network_logs', 'firewall_logs', 'session_data', 'system_logs', 'malware_artifacts']
                },
                'insider_threat': {
                    'name': 'Insider Threat Investigation',
                    'description': 'Investigation of potential insider security threat',
                    'checklist': [
                        'Review user activity logs',
                        'Analyze access patterns',
                        'Check for privilege escalation',
                        'Review data access patterns',
                        'Examine USB/removable media usage',
                        'Assess after-hours activity',
                        'Review email communications',
                        'Check for data exfiltration indicators'
                    ],
                    'evidence_types': ['user_logs', 'access_logs', 'activity_patterns', 'usb_logs', 'email_logs']
                }
            }
            
            logger.info("Forensics case templates initialized")
            
        except Exception as e:
            logger.error(f"Error initializing forensics: {e}")
    
    async def create_case(self, case_type: str, alert_id: str, analyst_id: str, description: str = "") -> Dict[str, Any]:
        """Create new forensics case"""
        try:
            if case_type not in self.case_files:
                return {'error': f'Unknown case type: {case_type}'}
            
            case_template = self.case_files[case_type]
            case_id = f"case_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create case file
            case_data = {
                'case_id': case_id,
                'case_type': case_type,
                'case_name': case_template['name'],
                'case_description': case_template['description'],
                'alert_id': alert_id,
                'analyst_id': analyst_id,
                'description': description,
                'status': 'open',
                'priority': 'medium',
                'created_at': datetime.utcnow().isoformat(),
                'checklist': {item: False for item in case_template['checklist']},
                'evidence': [],
                'notes': [],
                'timeline': [
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'event': 'Case created',
                        'description': f'Forensics case {case_id} opened for {case_template["name"]}'
                    }
                ]
            }
            
            # Save case file
            case_file_path = self.evidence_store / f"{case_id}.json"
            with open(case_file_path, 'w') as f:
                json.dump(case_data, f, indent=2)
            
            # Update alert with case reference
            alerts_collection = self.db.get_database().alerts
            await alerts_collection.update_one(
                {'alertId': alert_id},
                {'$set': {
                    'forensics_case_id': case_id,
                    'status': 'under_investigation',
                    'updatedAt': datetime.utcnow().isoformat()
                }}
            )
            
            logger.info(f"Created forensics case {case_id} of type {case_type}")
            
            return {
                'case_id': case_id,
                'case_type': case_type,
                'status': 'created',
                'case_file': str(case_file_path),
                'checklist': case_data['checklist'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating forensics case: {e}")
            return {'error': str(e)}
    
    async def add_evidence(self, case_id: str, evidence_type: str, evidence_data: Dict, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Add evidence to forensics case"""
        try:
            # Load case file
            case_file_path = self.evidence_store / f"{case_id}.json"
            
            if not case_file_path.exists():
                return {'error': f'Case file not found: {case_id}'}
            
            with open(case_file_path, 'r') as f:
                case_data = json.load(f)
            
            # Create evidence entry
            evidence_entry = {
                'evidence_id': f"evid_{datetime.utcnow().strftime('%H%M%S')}",
                'evidence_type': evidence_type,
                'added_at': datetime.utcnow().isoformat(),
                'added_by': 'system',
                'hash': self._calculate_evidence_hash(evidence_data),
                'size': len(str(evidence_data)) if isinstance(evidence_data, str) else 0,
                'description': f"{evidence_type} evidence"
            }
            
            # Handle file evidence
            if evidence_type == 'file' and file_path:
                try:
                    # Copy file to evidence store
                    evidence_filename = f"{case_id}_{evidence_entry['evidence_id']}{Path(file_path).suffix}"
                    evidence_file_path = self.evidence_store / evidence_filename
                    
                    with open(file_path, 'rb') as source_file:
                        with open(evidence_file_path, 'wb') as dest_file:
                            dest_file.write(source_file.read())
                    
                    evidence_entry.update({
                        'file_path': str(evidence_file_path),
                        'original_path': file_path,
                        'file_hash': self._calculate_file_hash(evidence_file_path)
                    })
                    
                except Exception as e:
                    logger.error(f"Error copying evidence file: {e}")
                    evidence_entry['error'] = str(e)
            
            case_data['evidence'].append(evidence_entry)
            case_data['timeline'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': f'Evidence added: {evidence_type}',
                'description': f"Added {evidence_type} evidence to case {case_id}"
            })
            
            # Update checklist if evidence type matches template
            if evidence_type in self.case_files.get(case_type, {}).get('evidence_types', []):
                case_data['checklist'][evidence_type] = True
            
            # Save updated case
            with open(case_file_path, 'w') as f:
                json.dump(case_data, f, indent=2)
            
            logger.info(f"Added {evidence_type} evidence to case {case_id}")
            
            return {
                'evidence_id': evidence_entry['evidence_id'],
                'case_id': case_id,
                'evidence_type': evidence_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding evidence: {e}")
            return {'error': str(e)}
    
    def _calculate_evidence_hash(self, evidence_data: Any) -> str:
        """Calculate hash for evidence data"""
        try:
            if isinstance(evidence_data, str):
                return hashlib.sha256(evidence_data.encode()).hexdigest()
            elif isinstance(evidence_data, bytes):
                return hashlib.sha256(evidence_data).hexdigest()
            else:
                return hashlib.sha256(json.dumps(evidence_data).encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating evidence hash: {e}")
            return ""
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
            return ""
    
    async def update_checklist(self, case_id: str, checklist_item: str, completed: bool = True) -> Dict[str, Any]:
        """Update forensics case checklist"""
        try:
            case_file_path = self.evidence_store / f"{case_id}.json"
            
            if not case_file_path.exists():
                return {'error': f'Case file not found: {case_id}'}
            
            with open(case_file_path, 'r') as f:
                case_data = json.load(f)
            
            # Update checklist
            if checklist_item in case_data.get('checklist', {}):
                case_data['checklist'][checklist_item] = completed
            
            # Add timeline entry
            case_data['timeline'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': f'Checklist item {checklist_item} {"marked" if completed else "unmarked"}',
                'description': f'{checklist_item}: {"completed" if completed else "pending"}'
            })
            
            # Save updated case
            with open(case_file_path, 'w') as f:
                json.dump(case_data, f, indent=2)
            
            action = "completed" if completed else "pending"
            logger.info(f"Updated checklist {checklist_item} to {action} for case {case_id}")
            
            return {
                'case_id': case_id,
                'checklist_item': checklist_item,
                'completed': completed,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating checklist: {e}")
            return {'error': str(e)}
    
    async def add_note(self, case_id: str, note: str, analyst_id: str) -> Dict[str, Any]:
        """Add note to forensics case"""
        try:
            case_file_path = self.evidence_store / f"{case_id}.json"
            
            if not case_file_path.exists():
                return {'error': f'Case file not found: {case_id}'}
            
            with open(case_file_path, 'r') as f:
                case_data = json.load(f)
            
            # Add note
            note_entry = {
                'note_id': f"note_{datetime.utcnow().strftime('%H%M%S')}",
                'note': note,
                'analyst_id': analyst_id,
                'added_at': datetime.utcnow().isoformat()
            }
            
            case_data['notes'].append(note_entry)
            case_data['timeline'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'Note added',
                'description': f'Analyst {analyst_id} added note to case {case_id}'
            })
            
            # Save updated case
            with open(case_file_path, 'w') as f:
                json.dump(case_data, f, indent=2)
            
            logger.info(f"Added note to case {case_id} by analyst {analyst_id}")
            
            return {
                'note_id': note_entry['note_id'],
                'case_id': case_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding note: {e}")
            return {'error': str(e)}
    
    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """Get forensics case details"""
        try:
            case_file_path = self.evidence_store / f"{case_id}.json"
            
            if not case_file_path.exists():
                return {'error': f'Case file not found: {case_id}'}
            
            with open(case_file_path, 'r') as f:
                case_data = json.load(f)
            
            return case_data
            
        except Exception as e:
            logger.error(f"Error getting case {case_id}: {e}")
            return {'error': str(e)}
    
    async def list_cases(self, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """List forensics cases"""
        try:
            cases = []
            
            # Get all case files
            for case_file in self.evidence_store.glob("*.json"):
                try:
                    with open(case_file, 'r') as f:
                        case_data = json.load(f)
                        
                        if status is None or case_data.get('status') == status:
                            cases.append(case_data)
                except Exception as e:
                    logger.error(f"Error reading case file {case_file}: {e}")
            
            # Sort by creation date and limit
            cases.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            cases = cases[:limit]
            
            return {
                'cases': cases,
                'total_count': len(cases),
                'limit': limit,
                'status_filter': status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            return {'error': str(e)}
    
    async def close_case(self, case_id: str, analyst_id: str, final_report: str = "") -> Dict[str, Any]:
        """Close forensics case"""
        try:
            case_file_path = self.evidence_store / f"{case_id}.json"
            
            if not case_file_path.exists():
                return {'error': f'Case file not found: {case_id}'}
            
            with open(case_file_path, 'r') as f:
                case_data = json.load(f)
            
            # Update case status
            case_data['status'] = 'closed'
            case_data['closed_at'] = datetime.utcnow().isoformat()
            case_data['closed_by'] = analyst_id
            case_data['final_report'] = final_report
            
            # Add timeline entry
            case_data['timeline'].append({
                'timestamp': datetime.utcnow().isoformat(),
                'event': 'Case closed',
                'description': f'Case {case_id} closed by analyst {analyst_id}'
            })
            
            # Save updated case
            with open(case_file_path, 'w') as f:
                json.dump(case_data, f, indent=2)
            
            logger.info(f"Closed forensics case {case_id}")
            
            return {
                'case_id': case_id,
                'status': 'closed',
                'closed_at': case_data['closed_at'],
                'final_report': final_report,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error closing case {case_id}: {e}")
            return {'error': str(e)}
    
    async def get_case_statistics(self) -> Dict[str, Any]:
        """Get forensics case statistics"""
        try:
            cases = []
            status_counts = {}
            
            # Get all case files
            for case_file in self.evidence_store.glob("*.json"):
                try:
                    with open(case_file, 'r') as f:
                        case_data = json.load(f)
                        cases.append(case_data)
                        
                        # Count by status
                        status = case_data.get('status', 'unknown')
                        status_counts[status] = status_counts.get(status, 0) + 1
                except Exception as e:
                    logger.error(f"Error reading case file {case_file}: {e}")
            
            # Calculate statistics
            total_cases = len(cases)
            avg_duration_days = 0  # Would need date calculation
            
            return {
                'total_cases': total_cases,
                'open_cases': status_counts.get('open', 0),
                'investigating_cases': status_counts.get('under_investigation', 0),
                'closed_cases': status_counts.get('closed', 0),
                'average_duration_days': avg_duration_days,
                'cases_by_type': {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting case statistics: {e}")
            return {'error': str(e)}
