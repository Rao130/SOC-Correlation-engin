"""
Reports API Routes
Handles incident response report generation and management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from typing import Dict, Any, Optional
from datetime import datetime
import os
import tempfile

from app.core.logging import logger
from app.services.incident_report_generator import incident_report_generator

router = APIRouter()

# Global state for tracking report generation
report_generation_state = {
    "is_generating": False,
    "progress": 0,
    "current_report": None,
    "last_generated": None
}

@router.get("/viewer")
async def get_report_viewer():
    """Serve real-time report viewer page"""
    try:
        with open("static/report_viewer.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Report viewer not found")
    except Exception as e:
        logger.error(f"Error serving report viewer: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to serve report viewer: {str(e)}")

@router.post("/generate")
async def generate_incident_report(background_tasks: BackgroundTasks):
    """Generate comprehensive incident response PDF report with real data"""
    try:
        if report_generation_state["is_generating"]:
            raise HTTPException(status_code=409, detail="Report generation already in progress")
        
        logger.info("Starting incident response report generation with real data...")
        report_generation_state["is_generating"] = True
        report_generation_state["progress"] = 0
        
        # Generate report in background
        def generate_report():
            try:
                report_generation_state["progress"] = 25
                report_path = incident_report_generator.generate_pdf_report()
                report_generation_state["progress"] = 100
                report_generation_state["current_report"] = report_path
                report_generation_state["last_generated"] = datetime.utcnow().isoformat()
                logger.info(f"Incident response report generated: {report_path}")
                return report_path
            except Exception as e:
                logger.error(f"Error generating incident report: {e}")
                report_generation_state["is_generating"] = False
                raise e
            finally:
                report_generation_state["is_generating"] = False
        
        # Execute report generation
        report_path = generate_report()
        
        if report_path and os.path.exists(report_path):
            return {
                "success": True,
                "message": "Incident response report generated successfully with real data",
                "report_path": report_path,
                "filename": os.path.basename(report_path),
                "generated_at": datetime.utcnow().isoformat(),
                "file_size": os.path.getsize(report_path)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate report")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_incident_report: {e}")
        report_generation_state["is_generating"] = False
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/preview")
async def preview_report_data():
    """Preview incident response report data without generating PDF"""
    try:
        from app.services.incident_report_generator import IncidentMetrics
        
        # Collect metrics for preview using real data
        metrics = incident_report_generator.collect_incident_metrics()
        
        return {
            "success": True,
            "preview_data": {
                "total_alerts": metrics.total_alerts,
                "critical_alerts": metrics.critical_alerts,
                "high_alerts": metrics.high_alerts,
                "medium_alerts": metrics.medium_alerts,
                "low_alerts": metrics.low_alerts,
                "affected_systems": metrics.affected_systems,
                "blocked_ips": metrics.blocked_ips,
                "resolved_incidents": metrics.resolved_incidents,
                "ongoing_incidents": metrics.ongoing_incidents,
                "mean_time_to_detect": metrics.mean_time_to_detect,
                "mean_time_to_respond": metrics.mean_time_to_respond,
                "mean_time_to_resolve": metrics.mean_time_to_resolve,
                "geo_threats": metrics.geo_threats,
                "top_threat_actors": metrics.top_threat_actors[:5],
                "top_attack_vectors": metrics.top_attack_vectors[:5],
                "top_affected_countries": metrics.top_affected_countries[:5]
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error previewing report data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to preview report data: {str(e)}")

@router.get("/list")
async def list_reports():
    """List all generated reports"""
    try:
        reports_dir = "reports"
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        
        reports = []
        if os.path.exists(reports_dir):
            for filename in os.listdir(reports_dir):
                if filename.endswith('.pdf'):
                    filepath = os.path.join(reports_dir, filename)
                    file_stat = os.stat(filepath)
                    reports.append({
                        "filename": filename,
                        "size": file_stat.st_size,
                        "created_at": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                        "file_path": filepath
                    })
        
        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "success": True,
            "total_reports": len(reports),
            "reports": reports
        }
    except Exception as e:
        logger.error(f"Error in list_reports: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")

@router.get("/status")
async def get_report_generation_status():
    """Get status of report generation system"""
    try:
        from app.services.real_data_generator import data_generator
        from app.services.network_monitor import network_monitor
        from app.services.log_streamer import log_streamer
        from app.services.geo_threat_mapper import geo_threat_mapper
        
        return {
            "success": True,
            "generation_status": {
                "is_generating": report_generation_state["is_generating"],
                "progress": report_generation_state["progress"],
                "current_report": report_generation_state["current_report"],
                "last_generated": report_generation_state["last_generated"]
            },
            "data_sources": {
                "real_data_generator": {
                    "available": data_generator is not None,
                    "alerts_count": len(data_generator.generated_alerts) if data_generator else 0
                },
                "network_monitor": {
                    "available": network_monitor is not None,
                    "alerts_count": len(network_monitor.memory_alerts) if network_monitor else 0
                },
                "log_streamer": {
                    "available": log_streamer is not None,
                    "logs_count": len(log_streamer.generated_logs) if log_streamer else 0
                },
                "geo_threat_mapper": {
                    "available": geo_threat_mapper is not None,
                    "threats_count": len(geo_threat_mapper.active_threats) if geo_threat_mapper else 0
                }
            },
            "features": {
                "severity_charts": True,
                "timeline_charts": True,
                "geo_distribution_charts": True,
                "threat_intelligence": True,
                "response_metrics": True,
                "recommendations": True,
                "real_time_updates": True
            },
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting report generation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/live-metrics")
async def get_live_metrics():
    """Get live metrics for real-time report updates"""
    try:
        from app.services.incident_report_generator import IncidentMetrics
        
        # Collect live metrics using real data
        metrics = incident_report_generator.collect_incident_metrics()
        
        return {
            "success": True,
            "metrics": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_alerts": metrics.total_alerts,
                "critical_alerts": metrics.critical_alerts,
                "high_alerts": metrics.high_alerts,
                "medium_alerts": metrics.medium_alerts,
                "low_alerts": metrics.low_alerts,
                "affected_systems": metrics.affected_systems,
                "blocked_ips": metrics.blocked_ips,
                "resolved_incidents": metrics.resolved_incidents,
                "ongoing_incidents": metrics.ongoing_incidents,
                "mean_time_to_detect": metrics.mean_time_to_detect,
                "mean_time_to_respond": metrics.mean_time_to_respond,
                "mean_time_to_resolve": metrics.mean_time_to_resolve,
                "geo_threats": metrics.geo_threats
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting live metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get live metrics: {str(e)}")

@router.get("/download/{filename}")
async def download_report(filename: str):
    """Download a specific report"""
    try:
        # Security check - only allow PDF files
        if not filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check both current directory and reports subdirectory
        possible_paths = [
            os.path.join(os.getcwd(), filename),
            os.path.join("reports", filename)
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Security check - ensure file is in allowed directory
        if not (os.path.abspath(file_path).startswith(os.path.abspath(os.getcwd())) or 
                os.path.abspath(file_path).startswith(os.path.abspath(os.path.join(os.getcwd(), "reports")))):
            raise HTTPException(status_code=403, detail="Access denied")
        
        logger.info(f"Downloading incident report: {filename}")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in download_report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download report: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_report(filename: str):
    """Delete a specific report"""
    try:
        # Security check - only allow PDF files
        if not filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check both current directory and reports subdirectory
        possible_paths = [
            os.path.join(os.getcwd(), filename),
            os.path.join("reports", filename)
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Security check - ensure file is in allowed directory
        if not (os.path.abspath(file_path).startswith(os.path.abspath(os.getcwd())) or 
                os.path.abspath(file_path).startswith(os.path.abspath(os.path.join(os.getcwd(), "reports")))):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete file
        os.remove(file_path)
        logger.info(f"Report deleted: {filename}")
        
        return {
            "success": True,
            "message": f"Report {filename} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")
