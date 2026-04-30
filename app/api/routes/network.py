"""
Network Monitoring API Routes
Provides real network data and metrics
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.logging import logger
from app.services.network_monitor import network_monitor

router = APIRouter()

@router.get("/status")
async def get_network_status():
    """Get current network monitoring status"""
    try:
        system_info = await network_monitor.get_system_info()
        return {
            "monitoring_active": network_monitor.monitoring_active,
            "system_info": system_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get network status")

@router.get("/metrics")
async def get_network_metrics():
    """Get real network metrics"""
    try:
        import psutil
        
        # Get current network I/O
        net_io = psutil.net_io_counters()
        
        # Get network connections
        connections = psutil.net_connections(kind='inet')
        active_connections = [conn for conn in connections if conn.status == 'ESTABLISHED']
        
        # Calculate metrics
        metrics = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "active_connections": len(active_connections),
            "total_connections": len(connections),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting network metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get network metrics")

@router.get("/connections")
async def get_active_connections():
    """Get list of active network connections"""
    try:
        import psutil
        
        connections = psutil.net_connections(kind='inet')
        active_connections = []
        
        for conn in connections:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                connection_info = {
                    "local_address": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    "remote_address": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    "status": conn.status,
                    "pid": conn.pid,
                    "timestamp": datetime.utcnow().isoformat()
                }
                active_connections.append(connection_info)
        
        return {
            "connections": active_connections,
            "total_count": len(active_connections),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting connections: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connections")

@router.get("/interfaces")
async def get_network_interfaces():
    """Get network interfaces information"""
    try:
        import netifaces
        
        interfaces = []
        
        for interface_name in netifaces.interfaces():
            try:
                addrs = netifaces.ifaddresses(interface_name)
                interface_info = {
                    "name": interface_name,
                    "addresses": []
                }
                
                # Get IPv4 addresses
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        interface_info["addresses"].append({
                            "family": "IPv4",
                            "address": addr.get('addr', 'N/A'),
                            "netmask": addr.get('netmask', 'N/A'),
                            "broadcast": addr.get('broadcast', 'N/A')
                        })
                
                # Get IPv6 addresses
                if netifaces.AF_INET6 in addrs:
                    for addr in addrs[netifaces.AF_INET6]:
                        interface_info["addresses"].append({
                            "family": "IPv6",
                            "address": addr.get('addr', 'N/A'),
                            "netmask": addr.get('netmask', 'N/A')
                        })
                
                # Get MAC addresses
                if netifaces.AF_LINK in addrs:
                    for addr in addrs[netifaces.AF_LINK]:
                        interface_info["addresses"].append({
                            "family": "MAC",
                            "address": addr.get('addr', 'N/A')
                        })
                
                interfaces.append(interface_info)
                
            except Exception as e:
                logger.warning(f"Error getting interface {interface_name}: {e}")
                continue
        
        return {
            "interfaces": interfaces,
            "total_count": len(interfaces),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
        raise HTTPException(status_code=500, detail="Failed to get interfaces")

@router.get("/realtime-alerts")
async def get_realtime_alerts(db = Depends(get_db)):
    """Get alerts generated by real network monitoring"""
    try:
        # Get alerts from memory storage
        from app.services.network_monitor import network_monitor
        memory_alerts = network_monitor.memory_alerts
        
        # Try to get database alerts as well
        db_alerts = []
        try:
            file_db = db.get_database()
            if file_db:
                collection = file_db.alerts
                
                # Get recent network-related alerts (last 1 hour)
                one_hour_ago = datetime.utcnow() - timedelta(hours=1)
                
                query = {
                    "source": "Network Monitor",
                    "timestamp": {"$gte": one_hour_ago.isoformat()}
                }
                
                cursor = collection.find(query).sort("timestamp", -1).limit(50)
                db_alerts = await cursor.to_list()
                
                # Convert ObjectId to string
                for alert in db_alerts:
                    if "_id" in alert:
                        alert["_id"] = str(alert["_id"])
                    for key, value in alert.items():
                        if hasattr(value, '__str__') and 'ObjectId' in str(type(value)):
                            alert[key] = str(value)
                            
        except Exception as db_error:
            logger.warning(f"Database query failed: {db_error}")
        
        # Combine memory and database alerts, prioritize memory alerts
        all_alerts = memory_alerts + db_alerts
        
        # Remove duplicates and sort by timestamp
        seen_ids = set()
        unique_alerts = []
        for alert in all_alerts:
            alert_id = alert.get('_id', str(alert))
            if alert_id not in seen_ids:
                seen_ids.add(alert_id)
                unique_alerts.append(alert)
        
        # Sort by timestamp (newest first)
        unique_alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return {
            "alerts": unique_alerts[:50],  # Return max 50 alerts
            "count": len(unique_alerts),
            "time_range": "real_time",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting realtime alerts: {e}")
        return {
            "alerts": [],
            "count": 0,
            "error": str(e)
        }
