"""
Compliance Reporting API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from app.services.compliance_engine import compliance_engine, ComplianceFramework
from app.core.auth import get_current_user
from app.core.logging import logger

router = APIRouter()

# Pydantic models
class ComplianceAssessmentRequest(BaseModel):
    framework: str = Field(..., description="Compliance framework (pci_dss, hipaa, gdpr, sox, nist, iso27001)")
    period_start: datetime = Field(..., description="Assessment period start")
    period_end: datetime = Field(..., description="Assessment period end")
    include_alerts: bool = Field(default=True, description="Include alert data in assessment")
    include_logs: bool = Field(default=True, description="Include log data in assessment")

class ComplianceReportRequest(BaseModel):
    frameworks: List[str] = Field(..., description="List of frameworks to assess")
    period_start: datetime = Field(..., description="Report period start")
    period_end: datetime = Field(..., description="Report period end")
    auto_generate: bool = Field(default=True, description="Auto-generate assessments if needed")

@router.get("/frameworks")
async def list_frameworks(current_user: dict = Depends(get_current_user)):
    """List available compliance frameworks"""
    try:
        frameworks = [
            {
                "id": framework.value,
                "name": framework.value.replace("_", " ").upper(),
                "description": f"{framework.value.replace('_', ' ').upper()} compliance framework"
            }
            for framework in ComplianceFramework
        ]
        
        return {
            "status": "success",
            "frameworks": frameworks,
            "total": len(frameworks)
        }
    except Exception as e:
        logger.error(f"Error listing frameworks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frameworks/{framework}/requirements")
async def get_framework_requirements(
    framework: str,
    current_user: dict = Depends(get_current_user)
):
    """Get requirements for a specific framework"""
    try:
        # Convert string to enum
        try:
            framework_enum = ComplianceFramework(framework)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid framework: {framework}")
        
        requirements = compliance_engine.get_requirements_by_framework(framework_enum)
        
        return {
            "status": "success",
            "framework": framework,
            "requirements": requirements,
            "total": len(requirements)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting framework requirements: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assess")
async def assess_compliance(
    request: ComplianceAssessmentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Perform compliance assessment"""
    try:
        # Convert string to enum
        try:
            framework_enum = ComplianceFramework(request.framework)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid framework: {request.framework}")
        
        # Get data for assessment
        alert_data = []
        log_data = []
        
        if request.include_alerts:
            # This would normally fetch from database
            # For now, we'll simulate with sample data
            alert_data = await _get_alert_data(request.period_start, request.period_end)
        
        if request.include_logs:
            # This would normally fetch from database
            # For now, we'll simulate with sample data
            log_data = await _get_log_data(request.period_start, request.period_end)
        
        # Perform assessment
        report = await compliance_engine.assess_compliance(
            framework_enum,
            request.period_start,
            request.period_end,
            alert_data,
            log_data
        )
        
        return {
            "status": "success",
            "message": f"Compliance assessment completed for {request.framework}",
            "report": _serialize_report(report)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in compliance assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reports/generate")
async def generate_compliance_report(
    request: ComplianceReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive compliance report"""
    try:
        reports = []
        
        for framework in request.frameworks:
            try:
                framework_enum = ComplianceFramework(framework)
                
                # Get data for assessment
                alert_data = await _get_alert_data(request.period_start, request.period_end)
                log_data = await _get_log_data(request.period_start, request.period_end)
                
                # Perform assessment
                report = await compliance_engine.assess_compliance(
                    framework_enum,
                    request.period_start,
                    request.period_end,
                    alert_data,
                    log_data
                )
                
                reports.append(_serialize_report(report))
                
            except ValueError:
                logger.warning(f"Invalid framework skipped: {framework}")
                continue
            except Exception as e:
                logger.error(f"Error assessing framework {framework}: {e}")
                continue
        
        return {
            "status": "success",
            "message": f"Generated compliance reports for {len(reports)} frameworks",
            "reports": reports,
            "summary": _generate_report_summary(reports)
        }
    except Exception as e:
        logger.error(f"Error generating compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports")
async def list_compliance_reports(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of reports"),
    current_user: dict = Depends(get_current_user)
):
    """List compliance reports"""
    try:
        reports = compliance_engine.list_reports()
        
        # Filter by framework if specified
        if framework:
            reports = [r for r in reports if r["framework"] == framework]
        
        # Sort by generated_at (newest first)
        reports.sort(key=lambda x: x["generated_at"], reverse=True)
        
        # Limit results
        reports = reports[:limit]
        
        return {
            "status": "success",
            "reports": reports,
            "total": len(reports)
        }
    except Exception as e:
        logger.error(f"Error listing compliance reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/reports/{framework}/{period}")
async def get_compliance_report(
    framework: str,
    period: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific compliance report"""
    try:
        report = compliance_engine.get_report(framework, period)
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "status": "success",
            "report": _serialize_report(report)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting compliance report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_compliance_dashboard(
    current_user: dict = Depends(get_current_user)
):
    """Get compliance dashboard data"""
    try:
        reports = compliance_engine.list_reports()
        
        # Calculate overall compliance status
        if not reports:
            return {
                "status": "success",
                "message": "No compliance reports available",
                "dashboard": {
                    "overall_score": 0,
                    "framework_status": {},
                    "recent_assessments": [],
                    "compliance_trends": [],
                    "recommendations": []
                }
            }
        
        # Group by framework
        framework_reports = {}
        for report in reports:
            framework = report["framework"]
            if framework not in framework_reports:
                framework_reports[framework] = []
            framework_reports[framework].append(report)
        
        # Get latest report for each framework
        latest_reports = {}
        framework_status = {}
        total_score = 0
        framework_count = 0
        
        for framework, fw_reports in framework_reports.items():
            latest = max(fw_reports, key=lambda x: x["generated_at"])
            latest_reports[framework] = latest
            framework_status[framework] = latest["overall_status"]
            total_score += latest["overall_score"]
            framework_count += 1
        
        overall_score = total_score / framework_count if framework_count > 0 else 0
        
        # Get recent assessments
        recent_assessments = sorted(
            reports,
            key=lambda x: x["generated_at"],
            reverse=True
        )[:10]
        
        # Calculate trends (simplified)
        compliance_trends = []
        for framework, fw_reports in framework_reports.items():
            if len(fw_reports) >= 2:
                sorted_reports = sorted(fw_reports, key=lambda x: x["generated_at"])
                latest_score = sorted_reports[-1]["overall_score"]
                previous_score = sorted_reports[-2]["overall_score"]
                trend = "improving" if latest_score > previous_score else "declining" if latest_score < previous_score else "stable"
                
                compliance_trends.append({
                    "framework": framework,
                    "trend": trend,
                    "latest_score": latest_score,
                    "previous_score": previous_score,
                    "change": latest_score - previous_score
                })
        
        # Get recommendations from latest reports
        all_recommendations = []
        for report in latest_reports.values():
            report_key = f"{report['framework']}_{report['period_start'][:8]}"
            full_report = compliance_engine.get_report(report['framework'], report['period_start'][:8])
            if full_report and full_report.recommendations:
                all_recommendations.extend(full_report.recommendations)
        
        # Remove duplicates and limit
        recommendations = list(set(all_recommendations))[:10]
        
        return {
            "status": "success",
            "dashboard": {
                "overall_score": round(overall_score, 1),
                "framework_status": framework_status,
                "latest_reports": latest_reports,
                "recent_assessments": recent_assessments,
                "compliance_trends": compliance_trends,
                "recommendations": recommendations,
                "total_frameworks": len(framework_status),
                "last_updated": max(r["generated_at"] for r in reports) if reports else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting compliance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_compliance_stats(current_user: dict = Depends(get_current_user)):
    """Get compliance statistics"""
    try:
        reports = compliance_engine.list_reports()
        
        if not reports:
            return {
                "status": "success",
                "stats": {
                    "total_reports": 0,
                    "framework_distribution": {},
                    "status_distribution": {},
                    "average_scores": {},
                    "assessment_frequency": {}
                }
            }
        
        # Framework distribution
        framework_distribution = {}
        for report in reports:
            framework = report["framework"]
            framework_distribution[framework] = framework_distribution.get(framework, 0) + 1
        
        # Status distribution
        status_distribution = {}
        for report in reports:
            status = report["overall_status"]
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # Average scores by framework
        framework_scores = {}
        for report in reports:
            framework = report["framework"]
            if framework not in framework_scores:
                framework_scores[framework] = []
            framework_scores[framework].append(report["overall_score"])
        
        average_scores = {
            framework: sum(scores) / len(scores)
            for framework, scores in framework_scores.items()
        }
        
        # Assessment frequency (by month)
        assessment_frequency = {}
        for report in reports:
            month = report["generated_at"][:7]  # YYYY-MM
            assessment_frequency[month] = assessment_frequency.get(month, 0) + 1
        
        return {
            "status": "success",
            "stats": {
                "total_reports": len(reports),
                "framework_distribution": framework_distribution,
                "status_distribution": status_distribution,
                "average_scores": average_scores,
                "assessment_frequency": assessment_frequency,
                "latest_assessment": max(r["generated_at"] for r in reports),
                "oldest_assessment": min(r["generated_at"] for r in reports)
            }
        }
    except Exception as e:
        logger.error(f"Error getting compliance stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/requirements/{requirement_id}")
async def get_requirement_details(
    requirement_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed requirement information"""
    try:
        requirement = compliance_engine.requirements.get(requirement_id)
        
        if not requirement:
            raise HTTPException(status_code=404, detail="Requirement not found")
        
        return {
            "status": "success",
            "requirement": {
                "id": requirement.id,
                "framework": requirement.framework.value,
                "category": requirement.category,
                "title": requirement.title,
                "description": requirement.description,
                "controls": requirement.controls,
                "evidence_required": requirement.evidence_required,
                "test_procedures": requirement.test_procedures,
                "automated_check": requirement.automated_check
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting requirement details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
async def _get_alert_data(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Get alert data for compliance assessment"""
    # This would normally fetch from database
    # For now, return sample data
    return [
        {
            "id": "alert_1",
            "timestamp": start_date.isoformat(),
            "category": "network",
            "description": "Firewall blocked unauthorized access attempt",
            "severity": "medium",
            "source": "firewall"
        },
        {
            "id": "alert_2",
            "timestamp": (start_date + timedelta(hours=1)).isoformat(),
            "category": "access",
            "description": "Failed login attempt detected",
            "severity": "low",
            "source": "authentication"
        }
    ]

async def _get_log_data(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
    """Get log data for compliance assessment"""
    # This would normally fetch from database
    # For now, return sample data
    return [
        {
            "id": "log_1",
            "timestamp": start_date.isoformat(),
            "level": "INFO",
            "message": "User authentication successful",
            "source": "auth_service"
        },
        {
            "id": "log_2",
            "timestamp": (start_date + timedelta(minutes=30)).isoformat(),
            "level": "WARNING",
            "message": "Firewall rule updated",
            "source": "firewall"
        }
    ]

def _serialize_report(report) -> Dict[str, Any]:
    """Serialize compliance report for API response"""
    return {
        "framework": report.framework.value,
        "period_start": report.period_start.isoformat(),
        "period_end": report.period_end.isoformat(),
        "overall_score": report.overall_score,
        "overall_status": report.overall_status.value,
        "assessments": [
            {
                "requirement_id": assessment.requirement_id,
                "status": assessment.status.value,
                "score": assessment.score,
                "findings": assessment.findings,
                "evidence": assessment.evidence,
                "last_assessed": assessment.last_assessed.isoformat(),
                "next_assessment": assessment.next_assessment.isoformat()
            }
            for assessment in report.assessments
        ],
        "recommendations": report.recommendations,
        "generated_at": report.generated_at.isoformat()
    }

def _generate_report_summary(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary of multiple compliance reports"""
    if not reports:
        return {"message": "No reports generated"}
    
    total_score = sum(r["overall_score"] for r in reports)
    average_score = total_score / len(reports)
    
    status_counts = {}
    for report in reports:
        status = report["overall_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "total_frameworks": len(reports),
        "average_score": round(average_score, 1),
        "status_distribution": status_counts,
        "highest_score": max(r["overall_score"] for r in reports),
        "lowest_score": min(r["overall_score"] for r in reports),
        "compliant_frameworks": status_counts.get("compliant", 0),
        "needs_attention": status_counts.get("non_compliant", 0) + status_counts.get("partially_compliant", 0)
    }
