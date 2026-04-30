"""
WebSocket API Routes for Real-time Updates
Provides live data streaming for dashboard components
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

from app.core.logging import logger
from app.services.real_time_data_ingestion import real_time_ingestion
from app.services.network_monitor import network_monitor
from app.services.geo_threat_mapper import geo_threat_mapper
from app.core.database import get_db

router = APIRouter()

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, connection_type: str = "general"):
        """Register WebSocket connection (assumes already accepted)"""
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            "type": connection_type,
            "connected_at": datetime.utcnow().isoformat(),
            "last_ping": datetime.utcnow().isoformat()
        }
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific WebSocket"""
        try:
            # Check if connection is still open
            if websocket.client_state.name == "OPEN":
                await websocket.send_text(message)
            else:
                self.disconnect(websocket)
        except Exception as e:
            logger.warning(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str, message_type: str = "general"):
        """Broadcast message to all connected WebSockets"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                # Check if connection is still open
                if connection.client_state.name != "OPEN":
                    disconnected.append(connection)
                    continue
                    
                # Only send to connections that are interested in this message type
                conn_data = self.connection_data.get(connection, {})
                if conn_data.get("type") == "general" or message_type == "general":
                    await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast new alert to all connected clients"""
        try:
            message = {
                "type": "new_alert",
                "data": alert_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.broadcast(json.dumps(message, default=str), "alert")
        except Exception as e:
            logger.error(f"Error broadcasting alert: {e}")
    
    async def broadcast_metrics(self, metrics_data: Dict[str, Any]):
        """Broadcast updated metrics to all connected clients"""
        try:
            message = {
                "type": "metrics_update",
                "data": metrics_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.broadcast(json.dumps(message, default=str), "metrics")
        except Exception as e:
            logger.error(f"Error broadcasting metrics: {e}")
    
    async def broadcast_analytics(self, analytics_data: Dict[str, Any]):
        """Broadcast analytics updates to all connected clients"""
        try:
            message = {
                "type": "analytics_update",
                "data": analytics_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.broadcast(json.dumps(message, default=str), "analytics")
        except Exception as e:
            logger.error(f"Error broadcasting analytics: {e}")

# Global connection manager
manager = ConnectionManager()

@router.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """Main WebSocket endpoint for real-time updates"""
    logger.info(f"WebSocket connection attempt for client: {client_id}")
    connection_accepted = False
    try:
        logger.info(f"Accepting WebSocket connection for client: {client_id}")
        await websocket.accept()
        connection_accepted = True
        logger.info(f"WebSocket connection accepted for client: {client_id}")
        
        # Register connection
        await manager.connect(websocket, "general")
        
        # Send initial data
        await send_initial_data(websocket)
        
        # Keep connection alive
        while True:
            try:
                # Wait for message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle different message types
                await handle_client_message(websocket, message)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await asyncio.wait_for(
                        websocket.send_text(json.dumps({
                            "type": "ping",
                            "timestamp": datetime.utcnow().isoformat()
                        })), 
                        timeout=5.0
                    )
                except (asyncio.TimeoutError, Exception):
                    logger.debug(f"Ping timeout for client: {client_id}")
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for client: {client_id}")
                break
                
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON from client {client_id}: {e}")
                try:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                except Exception:
                    break
                    
            except Exception as e:
                logger.error(f"Error handling WebSocket message for client {client_id}: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected during handshake: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        try:
            if connection_accepted and websocket in manager.active_connections:
                try:
                    await websocket.close()
                except Exception as close_error:
                    logger.debug(f"Error closing WebSocket: {close_error}")
        except Exception as e:
            logger.debug(f"Error in connection cleanup: {e}")
        finally:
            manager.disconnect(websocket)

async def send_initial_data(websocket: WebSocket):
    """Send initial data to newly connected client"""
    try:
        # Send recent alerts from database
        db = await get_db()
        if db:
            alerts_collection = db.get_collection("alerts")
            recent_alerts = await alerts_collection.find({}).sort("timestamp", -1).limit(20).to_list()
            
            # Convert ObjectId to string
            def convert_objectid(obj):
                if hasattr(obj, '__iter__') and not isinstance(obj, str):
                    if isinstance(obj, dict):
                        return {k: convert_objectid(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_objectid(item) for item in obj]
                elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                    return str(obj)
                return obj
            
            recent_alerts = [convert_objectid(alert) for alert in recent_alerts]
        else:
            recent_alerts = []
        
        initial_message = {
            "type": "initial_data",
            "recent_alerts": recent_alerts,
            "alert_stats": {"total": len(recent_alerts), "source": "database"}
        }
        await manager.send_personal_message(json.dumps(initial_message, default=str), websocket)
        
    except Exception as e:
        logger.error(f"Error sending initial data: {e}")

async def handle_client_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming messages from WebSocket clients"""
    try:
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping
            pong_response = {"type": "pong"}
            await manager.send_personal_message(json.dumps(pong_response), websocket)
            
        elif message_type == "request_alerts":
            # Send requested alerts from database
            db = await get_db()
            if db:
                alerts_collection = db.get_collection("alerts")
                alerts = await alerts_collection.find({}).sort("timestamp", -1).limit(1000).to_list()
                
                # Convert ObjectId to string
                def convert_objectid(obj):
                    if hasattr(obj, '__iter__') and not isinstance(obj, str):
                        if isinstance(obj, dict):
                            return {k: convert_objectid(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [convert_objectid(item) for item in obj]
                    elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                        return str(obj)
                    return obj
                
                alerts = [convert_objectid(alert) for alert in alerts]
            else:
                alerts = []
                
            response = {
                "type": "alerts_response",
                "alerts": alerts
            }
            await manager.send_personal_message(json.dumps(response, default=str), websocket)
            
    except Exception as e:
        logger.error(f"Error handling client message: {e}")
        # Send error response
        error_response = {"type": "error", "message": "Failed to process request"}
        await manager.send_personal_message(json.dumps(error_response), websocket)

# Background task to continuously broadcast updates
async def start_real_time_broadcasts():
    """Start background task for real-time data broadcasting"""
    logger.info("Starting real-time WebSocket broadcasts...")
    
    while True:
        try:
            # Only broadcast if there are active connections
            if manager.active_connections:
                # Broadcast updated statistics
                try:
                    stats = await real_time_ingestion.get_ingestion_statistics()
                    await manager.broadcast_analytics({
                        "ingestion_statistics": stats,
                        "active_connections": len(manager.active_connections),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Error broadcasting analytics: {e}")
                
                # Broadcast new alerts
                try:
                    db = await get_db()
                    if db:
                        alerts_collection = db.get_collection("alerts")
                        recent_alerts = await alerts_collection.find({}).sort("timestamp", -1).limit(10).to_list()
                        
                        # Convert ObjectId to string
                        def convert_objectid(obj):
                            if hasattr(obj, '__iter__') and not isinstance(obj, str):
                                if isinstance(obj, dict):
                                    return {k: convert_objectid(v) for k, v in obj.items()}
                                elif isinstance(obj, list):
                                    return [convert_objectid(item) for item in obj]
                            elif hasattr(obj, '__str__') and 'ObjectId' in str(type(obj)):
                                return str(obj)
                            return obj
                        
                        recent_alerts = [convert_objectid(alert) for alert in recent_alerts]
                        
                        if recent_alerts:
                            for alert in recent_alerts[:3]:  # Send top 3 most recent
                                await manager.broadcast_alert(alert)
                except Exception as e:
                    logger.warning(f"Error broadcasting alerts: {e}")
                
                # Broadcast network metrics
                try:
                    if network_monitor.monitoring_active:
                        network_stats = {
                            "monitoring_active": True,
                            "memory_alerts_count": len(network_monitor.memory_alerts),
                            "recent_network_alerts": network_monitor.memory_alerts[-5:] if network_monitor.memory_alerts else [],
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        await manager.broadcast_metrics(network_stats)
                except Exception as e:
                    logger.warning(f"Error broadcasting metrics: {e}")
                
                # Broadcast geo threat data
                try:
                    if geo_threat_mapper.active_threats:
                        recent_threats = geo_threat_mapper.active_threats[-3:]  # Send top 3 most recent
                        for threat in recent_threats:
                            await manager.broadcast(json.dumps({
                                "type": "geo_threat",
                                "data": threat
                            }, default=str))
                except Exception as e:
                    logger.warning(f"Error broadcasting geo threats: {e}")
                
                # Broadcast system status
                try:
                    db = await get_db()
                    total_alerts = 0
                    if db:
                        alerts_collection = db.get_collection("alerts")
                        total_alerts = await alerts_collection.count_documents({})
                    
                    system_status = {
                        "data_ingestion_active": real_time_ingestion.active,
                        "network_monitor_active": network_monitor.monitoring_active,
                        "geo_threat_mapper_active": geo_threat_mapper.active,
                        "total_alerts": total_alerts,
                        "total_network_alerts": len(network_monitor.memory_alerts),
                        "total_geo_threats": len(geo_threat_mapper.active_threats),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await manager.broadcast_system_status(system_status)
                except Exception as e:
                    logger.warning(f"Error broadcasting system status: {e}")
            
            await asyncio.sleep(5)  # Further reduced interval for very responsive real-time updates
            
        except Exception as e:
            logger.error(f"Error in real-time broadcast loop: {e}")
            await asyncio.sleep(5)

# Export manager for use in other modules
__all__ = ["manager", "start_real_time_broadcasts", "report_manager", "start_report_metric_broadcasts"]

# Report-specific WebSocket connections
report_manager = ConnectionManager()

@router.websocket("/reports/{client_id}")
async def websocket_reports_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time report updates"""
    logger.info(f"Report WebSocket connection attempt for client: {client_id}")
    connection_accepted = False
    try:
        await websocket.accept()
        connection_accepted = True
        logger.info(f"Report WebSocket connection accepted for client: {client_id}")
        
        # Register connection
        await report_manager.connect(websocket, "reports")
        
        # Send initial report metrics
        await send_initial_report_metrics(websocket)
        
        # Keep connection alive and stream updates
        while True:
            try:
                # Wait for message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle report-specific messages
                await handle_report_client_message(websocket, message)
                
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_text(json.dumps({
                        "type": "ping",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                except Exception:
                    break
                    
            except WebSocketDisconnect:
                logger.info(f"Report WebSocket disconnected for client: {client_id}")
                break
                
            except Exception as e:
                logger.error(f"Error handling report WebSocket message: {e}")
                break
                
    except WebSocketDisconnect:
        logger.info(f"Report WebSocket disconnected during handshake: {client_id}")
    except Exception as e:
        logger.error(f"Report WebSocket connection error: {e}")
    finally:
        try:
            if connection_accepted and websocket in report_manager.active_connections:
                try:
                    await websocket.close()
                except Exception as close_error:
                    logger.debug(f"Error closing report WebSocket: {close_error}")
        except Exception as e:
            logger.debug(f"Error in report connection cleanup: {e}")
        finally:
            report_manager.disconnect(websocket)

async def send_initial_report_metrics(websocket: WebSocket):
    """Send initial report metrics to newly connected client"""
    try:
        from app.services.incident_report_generator import incident_report_generator
        
        # Collect initial metrics
        metrics = incident_report_generator.collect_incident_metrics()
        
        initial_message = {
            "type": "initial_report_metrics",
            "metrics": {
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
            "timestamp": datetime.utcnow().isoformat()
        }
        await report_manager.send_personal_message(json.dumps(initial_message, default=str), websocket)
        
    except Exception as e:
        logger.error(f"Error sending initial report metrics: {e}")

async def handle_report_client_message(websocket: WebSocket, message: Dict[str, Any]):
    """Handle incoming messages from report WebSocket clients"""
    try:
        message_type = message.get("type")
        
        if message_type == "ping":
            # Respond to ping
            pong_response = {"type": "pong"}
            await report_manager.send_personal_message(json.dumps(pong_response), websocket)
            
        elif message_type == "request_metrics":
            # Send requested metrics
            from app.services.incident_report_generator import incident_report_generator
            metrics = incident_report_generator.collect_incident_metrics()
            
            response = {
                "type": "metrics_response",
                "metrics": {
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
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            await report_manager.send_personal_message(json.dumps(response, default=str), websocket)
        
        elif message_type == "request_live_update":
            # Send live metrics update
            from app.services.incident_report_generator import incident_report_generator
            metrics = incident_report_generator.collect_incident_metrics()
            
            live_update = {
                "type": "live_update",
                "metrics": {
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
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            await report_manager.send_personal_message(json.dumps(live_update, default=str), websocket)
            
    except Exception as e:
        logger.error(f"Error handling report client message: {e}")
        # Send error response
        error_response = {"type": "error", "message": "Failed to process request"}
        await report_manager.send_personal_message(json.dumps(error_response), websocket)

# Background task for real-time report metric broadcasts
async def start_report_metric_broadcasts():
    """Start background task for real-time report metric broadcasting"""
    logger.info("Starting real-time report metric broadcasts...")
    
    while True:
        try:
            # Only broadcast if there are active connections
            if report_manager.active_connections:
                try:
                    from app.services.incident_report_generator import incident_report_generator
                    
                    # Collect current metrics
                    metrics = incident_report_generator.collect_incident_metrics()
                    
                    # Broadcast metrics update to all report clients
                    metrics_update = {
                        "type": "report_metrics_update",
                        "metrics": {
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
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await report_manager.broadcast(json.dumps(metrics_update, default=str), "reports")
                    
                except Exception as e:
                    logger.warning(f"Error broadcasting report metrics: {e}")
            
            await asyncio.sleep(3)  # Update report metrics every 3 seconds
            
        except Exception as e:
            logger.error(f"Error in report metric broadcast loop: {e}")
            await asyncio.sleep(3)
