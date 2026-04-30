import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from enum import Enum

from app.core.config import settings
from app.core.database import db_manager
from app.core.logging import logger

class ComplianceFramework(Enum):
    ISO_27001 = "ISO 27001"
    ISO_27002 = "ISO 27002"
    ISO_27017 = "ISO 27017"
    ISO_27018 = "ISO 27018"
    ISO_27019 = "ISO 27019"
    ISO_27035 = "ISO 27035"
    NIST_CSF = "NIST CSF"
    GDPR = "GDPR"
    PCI_DSS = "PCI DSS"
    HIPAA = "HIPAA"
    SOX = "Sarbanes-Oxley"

class ComplianceManager:
    """Compliance management and reporting service"""
    
    def __init__(self):
        self.db = db_manager
        self.compliance_rules = {}
        self.audit_logs = []
        self._load_compliance_rules()
    
    def _load_compliance_rules(self):
        """Load compliance rules for different frameworks"""
        try:
            # ISO 27001 controls
            self.compliance_rules[ComplianceFramework.ISO_27001] = {
                'access_control': {
                    'name': 'Access Control',
                    'controls': [
                        {'id': 'A.9.1', 'description': 'Access control policy', 'requirement': 'Documented access control policy'},
                        {'id': 'A.9.2', 'description': 'User access management', 'requirement': 'Formal user access management'},
                        {'id': 'A.9.3', 'description': 'Password policy', 'requirement': 'Strong password policies'},
                        {'id': 'A.9.4', 'description': 'Privileged access', 'requirement': 'Control privileged access'}
                    ],
                    'automated_checks': ['password_complexity', 'account_lockout', 'session_timeout']
                },
                'audit_trail': {
                    'name': 'Audit Trail',
                    'controls': [
                        {'id': 'A.12.1', 'description': 'Audit data generation', 'requirement': 'Generate audit records for all events'},
                        {'id': 'A.12.2', 'description': 'Audit trail protection', 'requirement': 'Protect audit trail from modification'},
                        {'id': 'A.12.3', 'description': 'Audit review', 'requirement': 'Regular review of audit logs'}
                    ],
                    'automated_checks': ['log_integrity', 'audit_coverage']
                }
            }
            
            # GDPR controls
            self.compliance_rules[ComplianceFramework.GDPR] = {
                'data_protection': {
                    'name': 'Data Protection',
                    'controls': [
                        {'id': 'Art.5', 'description': 'Lawfulness of processing', 'requirement': 'Legal basis for data processing'},
                        {'id': 'Art.6', 'description': 'Purpose limitation', 'requirement': 'Collect only necessary data'},
                        {'id': 'Art.7', 'description': 'Data minimization', 'requirement': 'Minimize personal data collection'},
                        {'id': 'Art.8', 'description': 'Accuracy', 'requirement': 'Ensure data accuracy'},
                        {'id': 'Art.9', 'description': 'Storage limitation', 'requirement': 'Limit data retention'},
                        {'id': 'Art.10', 'description': 'Security', 'requirement': 'Implement appropriate security measures'}
                    ],
                    'automated_checks': ['data_classification', 'retention_policy', 'consent_management']
                }
            }
            
            # PCI DSS controls
            self.compliance_rules[ComplianceFramework.PCI_DSS] = {
                'network_security': {
                    'name': 'Network Security',
                    'controls': [
                        {'id': '1.1', 'description': 'Firewall configuration', 'requirement': 'Maintain secure firewall configuration'},
                        {'id': '1.2', 'description': 'Secure network architecture', 'requirement': 'Design secure network infrastructure'},
                        {'id': '1.3', 'description': 'Secure protocols', 'requirement': 'Use secure cryptographic protocols'}
                    ],
                    'automated_checks': ['firewall_rules', 'ssl_configuration', 'port_scanning']
                }
            }
            
            logger.info(f"Loaded compliance rules for {len(self.compliance_rules)} frameworks")
            
        except Exception as e:
            logger.error(f"Error loading compliance rules: {e}")
    
    async def run_compliance_check(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Run compliance assessment for specified framework"""
        try:
            if framework not in self.compliance_rules:
                return {'error': f'Unsupported compliance framework: {framework}'}
            
            rules = self.compliance_rules[framework]
            assessment_results = []
            
            # Get system data for assessment
            system_data = await self._collect_system_data()
            
            # Check each control
            for control_category, control_config in rules.items():
                category_results = []
                
                for control in control_config.get('controls', []):
                    control_result = await self._assess_control(control, system_data)
                    category_results.append(control_result)
                
                assessment_results.append({
                    'category': control_category,
                    'category_name': control_config.get('name'),
                    'controls': category_results,
                    'overall_score': self._calculate_category_score(category_results)
                })
            
            # Calculate overall compliance score
            overall_score = sum(result.get('overall_score', 0) for result in assessment_results) / len(assessment_results)
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(assessment_results, overall_score)
            
            # Save assessment
            assessment_id = f"compliance_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            assessment_data = {
                'assessment_id': assessment_id,
                'framework': framework.value,
                'overall_score': overall_score,
                'assessment_date': datetime.utcnow().isoformat(),
                'results': assessment_results,
                'recommendations': recommendations,
                'system_data': system_data
            }
            
            # Save to database
            compliance_collection = self.db.get_database().get('compliance_assessments', MockCollection([]))
            await compliance_collection.insert_one(assessment_data)
            
            logger.info(f"Completed compliance assessment for {framework.value}")
            
            return {
                'assessment_id': assessment_id,
                'framework': framework.value,
                'overall_score': overall_score,
                'results': assessment_results,
                'recommendations': recommendations,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running compliance check: {e}")
            return {'error': str(e)}
    
    async def _collect_system_data(self) -> Dict[str, Any]:
        """Collect system data for compliance assessment"""
        try:
            # Get recent alerts for analysis
            alerts_collection = self.db.get_database().alerts
            recent_alerts = await alerts_collection.find({
                'timestamp': {'$gte': datetime.utcnow() - timedelta(days=30)}
            }).to_list(length=100)
            
            # Get user access patterns
            access_patterns = await self._analyze_access_patterns(recent_alerts)
            
            # Get security configuration
            security_config = await self._analyze_security_config()
            
            # Get data handling practices
            data_practices = await self._analyze_data_practices(recent_alerts)
            
            return {
                'alert_analysis': {
                    'total_alerts': len(recent_alerts),
                    'severity_distribution': self._calculate_severity_distribution(recent_alerts),
                    'source_analysis': self._analyze_sources(recent_alerts),
                    'time_patterns': self._analyze_time_patterns(recent_alerts)
                },
                'access_patterns': access_patterns,
                'security_configuration': security_config,
                'data_practices': data_practices,
                'collection_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error collecting system data: {e}")
            return {}
    
    async def _assess_control(self, control: Dict, system_data: Dict) -> Dict[str, Any]:
        """Assess individual compliance control"""
        try:
            control_id = control.get('id')
            control_description = control.get('description')
            requirement = control.get('requirement')
            
            # Simulate assessment based on system data
            if control_id == 'A.9.1':  # Access control policy
                score = await self._assess_access_control_policy(system_data)
            elif control_id == 'A.12.1':  # Audit data generation
                score = await self._assess_audit_trail_protection(system_data)
            elif control_id == 'Art.5':  # Lawfulness of processing
                score = await self._assess_lawfulness(system_data)
            elif control_id == '1.1':  # Firewall configuration
                score = await self._assess_firewall_configuration(system_data)
            else:
                # Default assessment
                score = {
                    'score': 50,
                    'status': 'partial_compliance',
                    'findings': ['Manual assessment required'],
                    'evidence': []
                }
            
            return {
                'control_id': control_id,
                'control_description': control_description,
                'requirement': requirement,
                'score': score.get('score', 0),
                'status': score.get('status', 'non_compliant'),
                'findings': score.get('findings', []),
                'evidence': score.get('evidence', []),
                'assessment_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing control {control_id}: {e}")
            return {'error': str(e)}
    
    async def _assess_access_control_policy(self, system_data: Dict) -> Dict[str, Any]:
        """Assess access control policy implementation"""
        try:
            score = 70  # Base score
            findings = []
            evidence = []
            
            # Check for documented policy
            has_policy = await self._check_access_policy_documentation()
            if not has_policy:
                findings.append('No documented access control policy')
                score -= 20
            
            # Check password policy implementation
            password_strength = await self._assess_password_policy()
            if password_strength < 3:
                findings.append('Weak password policy implementation')
                score -= 15
            
            # Check account management
            account_management = await self._assess_account_management()
            if account_management < 3:
                findings.append('Poor account management practices')
                score -= 15
            
            status = 'compliant' if score >= 80 else 'partial_compliance'
            
            return {
                'score': score,
                'status': status,
                'findings': findings,
                'evidence': evidence,
                'assessment_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing access control policy: {e}")
            return {'score': 0, 'status': 'error', 'findings': [str(e)]}
    
    async def _assess_audit_trail_protection(self, system_data: Dict) -> Dict[str, Any]:
        """Assess audit trail protection"""
        try:
            score = 80  # Base score
            findings = []
            evidence = []
            
            # Check log integrity
            log_integrity = await self._check_log_integrity()
            if not log_integrity:
                findings.append('Poor log integrity protection')
                score -= 20
            
            # Check audit coverage
            audit_coverage = await self._check_audit_coverage()
            if audit_coverage < 80:
                findings.append('Insufficient audit coverage')
                score -= 20
            
            status = 'compliant' if score >= 80 else 'partial_compliance'
            
            return {
                'score': score,
                'status': status,
                'findings': findings,
                'evidence': evidence,
                'assessment_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assessing audit trail protection: {e}")
            return {'score': 0, 'status': 'error', 'findings': [str(e)]}
    
    def _calculate_category_score(self, controls: List[Dict]) -> float:
        """Calculate overall score for a control category"""
        if not controls:
            return 0.0
        
        total_score = sum(control.get('score', 0) for control in controls)
        return total_score / len(controls)
    
    async def _generate_compliance_recommendations(self, results: List[Dict], overall_score: float) -> List[str]:
        """Generate compliance improvement recommendations"""
        try:
            recommendations = []
            
            # High-priority recommendations
            if overall_score < 60:
                recommendations.extend([
                    'Implement formal access control policy',
                    'Establish comprehensive audit trail',
                    'Enhance network security controls',
                    'Conduct regular security awareness training'
                ])
            
            # Medium-priority recommendations
            elif overall_score < 80:
                recommendations.extend([
                    'Review and update security configurations',
                    'Implement automated compliance monitoring',
                    'Conduct gap analysis for controls',
                    'Establish incident response procedures'
                ])
            
            # Low-priority recommendations
            else:
                recommendations.extend([
                    'Maintain current security posture',
                    'Continue regular monitoring and review',
                    'Plan for continuous improvement',
                    'Document security procedures'
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ['Error generating recommendations']
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            # Get recent assessments
            compliance_collection = self.db.get_database().get('compliance_assessments', MockCollection([]))
            recent_assessments = await compliance_collection.find().sort('assessment_date', -1).limit(10).to_list(length=None)
            
            # Calculate compliance scores by framework
            framework_scores = {}
            for assessment in recent_assessments:
                framework = assessment.get('framework')
                score = assessment.get('overall_score', 0)
                if framework not in framework_scores:
                    framework_scores[framework] = []
                framework_scores[framework].append(score)
            
            # Calculate trends
            compliance_trends = {}
            for framework, scores in framework_scores.items():
                if len(scores) >= 2:
                    trend = 'improving' if scores[-1] > scores[-2] else 'declining'
                    compliance_trends[framework] = trend
            
            return {
                'recent_assessments': recent_assessments,
                'framework_scores': framework_scores,
                'compliance_trends': compliance_trends,
                'overall_compliance_score': sum(sum(scores) for scores in framework_scores.values()) / sum(len(scores) for scores in framework_scores.values() if scores) if framework_scores else 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance dashboard: {e}")
            return {'error': str(e)}
    
    # Helper methods (simplified for demo)
    async def _check_access_policy_documentation(self) -> bool:
        """Check if access control policy is documented"""
        return True  # Simplified - assume documented
    
    async def _assess_password_policy(self) -> int:
        """Assess password policy strength"""
        return 4  # Simplified - assume strong policy
    
    async def _assess_account_management(self) -> int:
        """Assess account management practices"""
        return 4  # Simplified - assume good practices
    
    async def _analyze_access_patterns(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze user access patterns"""
        return {
            'unique_users': len(set(alert.get('source', 'unknown') for alert in alerts)),
            'peak_hours': '14:00-16:00',  # Simplified pattern
            'failed_login_attempts': len([a for a in alerts if 'failed' in a.get('description', '').lower()]),
            'geographic_distribution': {}  # Would need location data
        }
    
    async def _analyze_security_config(self) -> Dict[str, Any]:
        """Analyze security configuration"""
        return {
            'firewall_configured': True,
            'ssl_enabled': True,
            'intrusion_detection': True,
            'antivirus_updated': True,
            'last_security_scan': datetime.utcnow().isoformat()
        }
    
    async def _analyze_data_practices(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze data handling practices"""
        return {
            'encryption_standards': 'AES-256',
            'data_retention_days': 90,
            'backup_frequency': 'daily',
            'access_controls': 'role-based',
            'audit_logging': True
        }
    
    def _calculate_severity_distribution(self, alerts: List[Dict]) -> Dict[str, int]:
        """Calculate severity distribution"""
        distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for alert in alerts:
            severity = alert.get('severity', 'low').lower()
            if severity in distribution:
                distribution[severity] += 1
        return distribution
    
    def _analyze_sources(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze alert sources"""
        source_counts = {}
        for alert in alerts:
            source = alert.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        return source_counts
    
    def _analyze_time_patterns(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze time patterns in alerts"""
        return {
            'peak_hours': '09:00-17:00',
            'weekend_activity': 'reduced',
            'after_hours_activity': 'increased',
            'average_response_time': '15 minutes'
        }
    
    async def _check_log_integrity(self) -> bool:
        """Check log integrity"""
        return True  # Simplified - assume logs are protected
    
    async def _check_audit_coverage(self) -> float:
        """Check audit coverage"""
        return 85.0  # Simplified - assume good coverage
    
    async def _analyze_sources(self, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze alert sources"""
        source_counts = {}
        for alert in alerts:
            source = alert.get('source', 'unknown')
            source_counts[source] = source_counts.get(source, 0) + 1
        return source_counts
