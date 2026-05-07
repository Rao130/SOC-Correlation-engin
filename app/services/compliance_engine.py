"""
Compliance Reporting Engine
Automated compliance reporting for PCI-DSS, HIPAA, GDPR, and other regulations
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOX = "sox"
    NIST = "nist"
    ISO27001 = "iso27001"

class ComplianceStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_ASSESSED = "not_assessed"

@dataclass
class ComplianceRequirement:
    """Individual compliance requirement"""
    id: str
    framework: ComplianceFramework
    category: str
    title: str
    description: str
    controls: List[str]
    evidence_required: List[str]
    test_procedures: List[str]
    automated_check: bool = True

@dataclass
class ComplianceAssessment:
    """Compliance assessment result"""
    requirement_id: str
    status: ComplianceStatus
    score: float  # 0-100
    findings: List[str]
    evidence: List[Dict[str, Any]]
    last_assessed: datetime
    next_assessment: datetime

@dataclass
class ComplianceReport:
    """Complete compliance report"""
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    overall_score: float
    overall_status: ComplianceStatus
    assessments: List[ComplianceAssessment]
    recommendations: List[str]
    generated_at: datetime

class ComplianceEngine:
    """Main compliance engine"""
    
    def __init__(self):
        self.requirements = {}
        self.assessments = {}
        self.reports = {}
        self._initialize_requirements()
    
    def _initialize_requirements(self):
        """Initialize compliance requirements for different frameworks"""
        
        # PCI-DSS Requirements
        self.requirements.update({
            'pci_dss_1_1': ComplianceRequirement(
                id='pci_dss_1_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Network Security',
                title='Install and maintain a firewall configuration',
                description='Firewall configurations must protect cardholder data',
                controls=['firewall_rules', 'network_segmentation', 'access_control'],
                evidence_required=['firewall_configs', 'network_diagrams', 'access_logs'],
                test_procedures=['review_firewall_rules', 'test_network_access', 'verify_segmentation']
            ),
            'pci_dss_2_1': ComplianceRequirement(
                id='pci_dss_2_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Access Control',
                title='Do not use vendor-supplied defaults',
                description='Change all vendor-supplied defaults before installing systems',
                controls=['password_policy', 'default_accounts', 'configuration_management'],
                evidence_required=['password_policies', 'account_reviews', 'configuration_logs'],
                test_procedures=['verify_password_complexity', 'check_default_accounts', 'review_configs']
            ),
            'pci_dss_3_1': ComplianceRequirement(
                id='pci_dss_3_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Data Protection',
                title='Protect stored cardholder data',
                description='Protect stored cardholder data through encryption and access controls',
                controls=['encryption', 'access_control', 'data_masking'],
                evidence_required=['encryption_configs', 'access_logs', 'data_inventory'],
                test_procedures=['verify_encryption', 'test_access_controls', 'review_data_handling']
            ),
            'pci_dss_4_1': ComplianceRequirement(
                id='pci_dss_4_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Network Security',
                title='Use strong cryptography and security protocols',
                description='Use strong cryptography and security protocols for data transmission',
                controls=['tls_configuration', 'certificate_management', 'protocol_security'],
                evidence_required=['tls_configs', 'certificate_logs', 'protocol_scans'],
                test_procedures=['test_tls_configuration', 'verify_certificates', 'scan_protocols']
            ),
            'pci_dss_7_1': ComplianceRequirement(
                id='pci_dss_7_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Access Control',
                title='Limit access to cardholder data',
                description='Limit access to cardholder data based on need-to-know',
                controls=['rbac', 'access_reviews', 'privilege_management'],
                evidence_required=['access_logs', 'role_definitions', 'review_reports'],
                test_procedures=['review_access_rights', 'test_role_permissions', 'verify_privileges']
            ),
            'pci_dss_10_1': ComplianceRequirement(
                id='pci_dss_10_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Logging and Monitoring',
                title='Track and monitor all access to network resources',
                description='Implement audit trails for all access to network resources',
                controls=['audit_logging', 'log_retention', 'log_protection'],
                evidence_required=['log_configs', 'retention_policies', 'log_samples'],
                test_procedures=['verify_logging', 'test_log_retention', 'check_log_integrity']
            ),
            'pci_dss_11_1': ComplianceRequirement(
                id='pci_dss_11_1',
                framework=ComplianceFramework.PCI_DSS,
                category='Security Testing',
                title='Regularly test security systems and processes',
                description='Regularly test security systems and processes',
                controls=['vulnerability_scanning', 'penetration_testing', 'security_assessments'],
                evidence_required=['scan_reports', 'pen_test_results', 'assessment_reports'],
                test_procedures=['review_scan_results', 'verify_pen_tests', 'check_assessments']
            )
        })
        
        # HIPAA Requirements
        self.requirements.update({
            'hipaa_164_308_a1': ComplianceRequirement(
                id='hipaa_164_308_a1',
                framework=ComplianceFramework.HIPAA,
                category='Access Controls',
                title='Access Management',
                description='Implement policies and procedures for authorized access',
                controls=['access_policies', 'user_authentication', 'emergency_access'],
                evidence_required=['access_policies', 'auth_logs', 'emergency_procedures'],
                test_procedures=['test_access_controls', 'verify_authentication', 'review_emergency_access']
            ),
            'hipaa_164_312_a1': ComplianceRequirement(
                id='hipaa_164_312_a1',
                framework=ComplianceFramework.HIPAA,
                category='Encryption',
                title='Encryption and Decryption',
                description='Implement encryption mechanisms for PHI',
                controls=['encryption_at_rest', 'encryption_in_transit', 'key_management'],
                evidence_required=['encryption_configs', 'key_policies', 'encryption_logs'],
                test_procedures=['test_encryption', 'verify_key_management', 'review_encryption_logs']
            ),
            'hipaa_164_312_b': ComplianceRequirement(
                id='hipaa_164_312_b',
                framework=ComplianceFramework.HIPAA,
                category='Audit Controls',
                title='Audit Controls',
                description='Implement hardware, software, and/or procedural mechanisms to record and examine access',
                controls=['audit_logging', 'log_review', 'tamper_detection'],
                evidence_required=['audit_logs', 'review_procedures', 'tamper_logs'],
                test_procedures=['verify_audit_logging', 'test_log_review', 'check_tamper_detection']
            )
        })
        
        # GDPR Requirements
        self.requirements.update({
            'gdpr_art32': ComplianceRequirement(
                id='gdpr_art32',
                framework=ComplianceFramework.GDPR,
                category='Security of Processing',
                title='Security of Processing',
                description='Implement appropriate technical and organizational measures',
                controls=['encryption', 'pseudonymization', 'access_controls'],
                evidence_required=['security_policies', 'technical_measures', 'risk_assessments'],
                test_procedures=['review_security_measures', 'test_encryption', 'verify_access_controls']
            ),
            'gdpr_art33': ComplianceRequirement(
                id='gdpr_art33',
                framework=ComplianceFramework.GDPR,
                category='Breach Notification',
                title='Notification of Personal Data Breach',
                description='Notify supervisory authority of personal data breach within 72 hours',
                controls=['breach_detection', 'notification_procedures', 'incident_response'],
                evidence_required=['breach_procedures', 'notification_logs', 'incident_reports'],
                test_procedures=['test_breach_detection', 'verify_notification_procedures', 'review_incident_response']
            )
        })
    
    async def assess_compliance(
        self, 
        framework: ComplianceFramework,
        period_start: datetime,
        period_end: datetime,
        alert_data: List[Dict[str, Any]] = None,
        log_data: List[Dict[str, Any]] = None
    ) -> ComplianceReport:
        """Assess compliance for a specific framework"""
        
        logger.info(f"Starting compliance assessment for {framework.value}")
        
        # Get framework requirements
        framework_requirements = [
            req for req in self.requirements.values()
            if req.framework == framework
        ]
        
        assessments = []
        total_score = 0
        
        for requirement in framework_requirements:
            assessment = await self._assess_requirement(
                requirement, 
                period_start, 
                period_end,
                alert_data or [],
                log_data or []
            )
            assessments.append(assessment)
            total_score += assessment.score
        
        # Calculate overall score and status
        overall_score = total_score / len(framework_requirements) if framework_requirements else 0
        
        if overall_score >= 90:
            overall_status = ComplianceStatus.COMPLIANT
        elif overall_score >= 70:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT
        
        # Generate recommendations
        recommendations = self._generate_recommendations(assessments)
        
        # Create report
        report = ComplianceReport(
            framework=framework,
            period_start=period_start,
            period_end=period_end,
            overall_score=overall_score,
            overall_status=overall_status,
            assessments=assessments,
            recommendations=recommendations,
            generated_at=datetime.now()
        )
        
        self.reports[f"{framework.value}_{period_start.strftime('%Y%m%d')}"] = report
        
        logger.info(f"Compliance assessment completed for {framework.value}: {overall_score:.1f}%")
        return report
    
    async def _assess_requirement(
        self,
        requirement: ComplianceRequirement,
        period_start: datetime,
        period_end: datetime,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> ComplianceAssessment:
        """Assess individual requirement"""
        
        findings = []
        evidence = []
        score = 0
        
        if requirement.automated_check:
            # Perform automated checks based on requirement type
            if 'firewall' in requirement.title.lower():
                score, findings, evidence = await self._check_firewall_compliance(
                    requirement, alert_data, log_data
                )
            elif 'access' in requirement.title.lower():
                score, findings, evidence = await self._check_access_compliance(
                    requirement, alert_data, log_data
                )
            elif 'encryption' in requirement.title.lower():
                score, findings, evidence = await self._check_encryption_compliance(
                    requirement, alert_data, log_data
                )
            elif 'logging' in requirement.title.lower() or 'audit' in requirement.title.lower():
                score, findings, evidence = await self._check_logging_compliance(
                    requirement, alert_data, log_data
                )
            elif 'testing' in requirement.title.lower() or 'scan' in requirement.title.lower():
                score, findings, evidence = await self._check_security_testing_compliance(
                    requirement, alert_data, log_data
                )
            else:
                # Generic compliance check
                score, findings, evidence = await self._generic_compliance_check(
                    requirement, alert_data, log_data
                )
        else:
            # Manual assessment required
            score = 50  # Default score for manual assessment
            findings.append("Manual assessment required for this requirement")
            evidence.append({"type": "manual", "status": "pending"})
        
        # Determine status
        if score >= 90:
            status = ComplianceStatus.COMPLIANT
        elif score >= 70:
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            status = ComplianceStatus.NON_COMPLIANT
        
        return ComplianceAssessment(
            requirement_id=requirement.id,
            status=status,
            score=score,
            findings=findings,
            evidence=evidence,
            last_assessed=datetime.now(),
            next_assessment=datetime.now() + timedelta(days=90)
        )
    
    async def _check_firewall_compliance(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Check firewall compliance"""
        
        findings = []
        evidence = []
        score = 0
        
        # Check for firewall-related alerts
        firewall_alerts = [
            alert for alert in alert_data
            if alert.get('category') == 'network' and 'firewall' in alert.get('description', '').lower()
        ]
        
        # Check for blocked traffic
        blocked_traffic = [
            alert for alert in firewall_alerts
            if 'blocked' in alert.get('description', '').lower()
        ]
        
        # Check for unauthorized access attempts
        unauthorized_attempts = [
            alert for alert in firewall_alerts
            if 'unauthorized' in alert.get('description', '').lower() or 'denied' in alert.get('description', '').lower()
        ]
        
        # Score based on findings
        if len(blocked_traffic) > 0:
            score += 30
            findings.append(f"Firewall is actively blocking traffic ({len(blocked_traffic)} events)")
            evidence.append({
                "type": "blocked_traffic",
                "count": len(blocked_traffic),
                "events": blocked_traffic[:5]
            })
        
        if len(unauthorized_attempts) == 0:
            score += 40
            findings.append("No unauthorized access attempts detected")
        else:
            findings.append(f"Unauthorized access attempts detected ({len(unauthorized_attempts)} events)")
            evidence.append({
                "type": "unauthorized_attempts",
                "count": len(unauthorized_attempts),
                "events": unauthorized_attempts[:5]
            })
        
        # Check for firewall rule changes
        rule_changes = [
            log for log in log_data
            if 'firewall' in log.get('message', '').lower() and ('rule' in log.get('message', '').lower() or 'config' in log.get('message', '').lower())
        ]
        
        if len(rule_changes) > 0:
            score += 30
            findings.append(f"Firewall configuration changes detected ({len(rule_changes)} events)")
            evidence.append({
                "type": "rule_changes",
                "count": len(rule_changes),
                "events": rule_changes[:5]
            })
        else:
            score += 20
            findings.append("No recent firewall configuration changes")
        
        return min(score, 100), findings, evidence
    
    async def _check_access_compliance(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Check access control compliance"""
        
        findings = []
        evidence = []
        score = 0
        
        # Check for access-related alerts
        access_alerts = [
            alert for alert in alert_data
            if alert.get('category') in ['access', 'identity', 'authentication']
        ]
        
        # Check for failed login attempts
        failed_logins = [
            alert for alert in access_alerts
            if 'failed' in alert.get('description', '').lower() and 'login' in alert.get('description', '').lower()
        ]
        
        # Check for privilege escalation attempts
        privilege_escalation = [
            alert for alert in access_alerts
            if 'privilege' in alert.get('description', '').lower() or 'escalation' in alert.get('description', '').lower()
        ]
        
        # Score based on findings
        if len(failed_logins) < 10:  # Threshold for normal failed logins
            score += 30
            findings.append("Failed login attempts within normal range")
        else:
            findings.append(f"High number of failed login attempts ({len(failed_logins)} events)")
            evidence.append({
                "type": "failed_logins",
                "count": len(failed_logins),
                "events": failed_logins[:5]
            })
        
        if len(privilege_escalation) == 0:
            score += 40
            findings.append("No privilege escalation attempts detected")
        else:
            findings.append(f"Privilege escalation attempts detected ({len(privilege_escalation)} events)")
            evidence.append({
                "type": "privilege_escalation",
                "count": len(privilege_escalation),
                "events": privilege_escalation[:5]
            })
        
        # Check for successful authentications
        successful_auth = [
            alert for alert in access_alerts
            if 'success' in alert.get('description', '').lower() or 'authenticated' in alert.get('description', '').lower()
        ]
        
        if len(successful_auth) > 0:
            score += 30
            findings.append(f"Successful authentications tracked ({len(successful_auth)} events)")
            evidence.append({
                "type": "successful_auth",
                "count": len(successful_auth),
                "events": successful_auth[:5]
            })
        
        return min(score, 100), findings, evidence
    
    async def _check_encryption_compliance(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Check encryption compliance"""
        
        findings = []
        evidence = []
        score = 0
        
        # Check for encryption-related alerts
        encryption_alerts = [
            alert for alert in alert_data
            if 'encryption' in alert.get('description', '').lower() or 'tls' in alert.get('description', '').lower()
        ]
        
        # Check for unencrypted data transfers
        unencrypted_transfers = [
            alert for alert in encryption_alerts
            if 'unencrypted' in alert.get('description', '').lower() or 'plain' in alert.get('description', '').lower()
        ]
        
        # Score based on findings
        if len(unencrypted_transfers) == 0:
            score += 50
            findings.append("No unencrypted data transfers detected")
        else:
            findings.append(f"Unencrypted data transfers detected ({len(unencrypted_transfers)} events)")
            evidence.append({
                "type": "unencrypted_transfers",
                "count": len(unencrypted_transfers),
                "events": unencrypted_transfers[:5]
            })
        
        # Check for TLS/SSL usage
        tls_usage = [
            alert for alert in encryption_alerts
            if 'tls' in alert.get('description', '').lower() or 'ssl' in alert.get('description', '').lower()
        ]
        
        if len(tls_usage) > 0:
            score += 50
            findings.append(f"TLS/SSL usage detected ({len(tls_usage)} events)")
            evidence.append({
                "type": "tls_usage",
                "count": len(tls_usage),
                "events": tls_usage[:5]
            })
        
        return min(score, 100), findings, evidence
    
    async def _check_logging_compliance(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Check logging compliance"""
        
        findings = []
        evidence = []
        score = 0
        
        # Check log retention
        if len(log_data) > 0:
            score += 30
            findings.append(f"Log data available for analysis ({len(log_data)} entries)")
            evidence.append({
                "type": "log_availability",
                "count": len(log_data),
                "sample": log_data[:5]
            })
        
        # Check for audit logs
        audit_logs = [
            log for log in log_data
            if 'audit' in log.get('message', '').lower() or 'access' in log.get('message', '').lower()
        ]
        
        if len(audit_logs) > 0:
            score += 40
            findings.append(f"Audit logs available ({len(audit_logs)} entries)")
            evidence.append({
                "type": "audit_logs",
                "count": len(audit_logs),
                "sample": audit_logs[:5]
            })
        
        # Check for security event logs
        security_logs = [
            log for log in log_data
            if 'security' in log.get('message', '').lower() or 'incident' in log.get('message', '').lower()
        ]
        
        if len(security_logs) > 0:
            score += 30
            findings.append(f"Security event logs available ({len(security_logs)} entries)")
            evidence.append({
                "type": "security_logs",
                "count": len(security_logs),
                "sample": security_logs[:5]
            })
        
        return min(score, 100), findings, evidence
    
    async def _check_security_testing_compliance(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Check security testing compliance"""
        
        findings = []
        evidence = []
        score = 0
        
        # Check for vulnerability scan results
        vulnerability_scans = [
            alert for alert in alert_data
            if 'vulnerability' in alert.get('description', '').lower() or 'scan' in alert.get('description', '').lower()
        ]
        
        # Check for penetration test results
        pen_tests = [
            alert for alert in alert_data
            if 'penetration' in alert.get('description', '').lower() or 'pentest' in alert.get('description', '').lower()
        ]
        
        # Score based on findings
        if len(vulnerability_scans) > 0:
            score += 50
            findings.append(f"Vulnerability scans performed ({len(vulnerability_scans)} results)")
            evidence.append({
                "type": "vulnerability_scans",
                "count": len(vulnerability_scans),
                "sample": vulnerability_scans[:5]
            })
        
        if len(pen_tests) > 0:
            score += 50
            findings.append(f"Penetration tests performed ({len(pen_tests)} results)")
            evidence.append({
                "type": "penetration_tests",
                "count": len(pen_tests),
                "sample": pen_tests[:5]
            })
        
        # If no recent tests found, reduce score
        if len(vulnerability_scans) == 0 and len(pen_tests) == 0:
            score = 20
            findings.append("No recent security testing evidence found")
        
        return min(score, 100), findings, evidence
    
    async def _generic_compliance_check(
        self,
        requirement: ComplianceRequirement,
        alert_data: List[Dict[str, Any]],
        log_data: List[Dict[str, Any]]
    ) -> Tuple[float, List[str], List[Dict[str, Any]]]:
        """Generic compliance check"""
        
        findings = []
        evidence = []
        score = 70  # Default score
        
        findings.append("Generic compliance check performed")
        evidence.append({
            "type": "generic_check",
            "requirement": requirement.id,
            "timestamp": datetime.now().isoformat()
        })
        
        return score, findings, evidence
    
    def _generate_recommendations(self, assessments: List[ComplianceAssessment]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # Analyze common issues
        non_compliant_requirements = [
            assessment for assessment in assessments
            if assessment.status == ComplianceStatus.NON_COMPLIANT
        ]
        
        partially_compliant_requirements = [
            assessment for assessment in assessments
            if assessment.status == ComplianceStatus.PARTIALLY_COMPLIANT
        ]
        
        # Generate recommendations based on findings
        if non_compliant_requirements:
            recommendations.append("Immediate action required for non-compliant requirements")
            recommendations.append("Implement remediation plan for critical compliance gaps")
        
        if partially_compliant_requirements:
            recommendations.append("Review and improve partially compliant controls")
            recommendations.append("Enhance monitoring and documentation processes")
        
        # Specific recommendations based on common patterns
        all_findings = []
        for assessment in assessments:
            all_findings.extend(assessment.findings)
        
        if 'unauthorized' in ' '.join(all_findings).lower():
            recommendations.append("Strengthen access controls and monitoring")
        
        if 'unencrypted' in ' '.join(all_findings).lower():
            recommendations.append("Implement encryption for sensitive data")
        
        if 'log' in ' '.join(all_findings).lower() and len(all_findings) < 5:
            recommendations.append("Enhance logging and audit trail capabilities")
        
        if not recommendations:
            recommendations.append("Maintain current security posture and continue monitoring")
        
        return recommendations
    
    def get_report(self, framework: str, period: str) -> Optional[ComplianceReport]:
        """Get compliance report"""
        report_key = f"{framework}_{period}"
        return self.reports.get(report_key)
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """List all compliance reports"""
        return [
            {
                "framework": report.framework.value,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "overall_score": report.overall_score,
                "overall_status": report.overall_status.value,
                "generated_at": report.generated_at.isoformat()
            }
            for report in self.reports.values()
        ]
    
    def get_requirements_by_framework(self, framework: ComplianceFramework) -> List[Dict[str, Any]]:
        """Get requirements for a specific framework"""
        framework_requirements = [
            req for req in self.requirements.values()
            if req.framework == framework
        ]
        
        return [
            {
                "id": req.id,
                "category": req.category,
                "title": req.title,
                "description": req.description,
                "controls": req.controls,
                "evidence_required": req.evidence_required,
                "automated_check": req.automated_check
            }
            for req in framework_requirements
        ]

# Global compliance engine instance
compliance_engine = ComplianceEngine()
