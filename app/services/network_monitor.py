"""
Real Network Data Collector for SOC Correlation Engine
Monitors system network activity and generates real security alerts
"""

import asyncio
import psutil
import socket
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import netifaces
from app.core.logging import logger
from app.core.database import get_db
from app.models.alert import AlertDocument


class NetworkMonitor:
    """Real-time network monitoring service"""
    
    def __init__(self):
        self.previous_connections = set()
        self.suspicious_ips = set()
        self.monitoring_active = False
        self.alert_thresholds = {
            'failed_logins': 5,
            'connection_rate': 100,
            'data_transfer_mb': 500
        }
        # In-memory alert storage for real-time display
        self.memory_alerts = []
        
    async def start_monitoring(self):
        """Start continuous network monitoring"""
        self.monitoring_active = True
        logger.info("Starting real network monitoring...")
        
        while self.monitoring_active:
            try:
                # Collect network metrics
                await self.collect_network_metrics()
                
                # Check for suspicious activity
                await self.detect_anomalies()
                
                # Wait before next collection
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in network monitoring: {e}")
                await asyncio.sleep(60)
    
    async def collect_network_metrics(self):
        """Collect real network metrics"""
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            current_connections = set()
            
            for conn in connections:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    current_connections.add((conn.laddr.ip, conn.laddr.port, conn.raddr.ip, conn.raddr.port))
            
            # Detect new connections
            new_connections = current_connections - self.previous_connections
            if new_connections:
                await self.process_new_connections(new_connections)
            
            self.previous_connections = current_connections
            
            # Get network I/O stats
            net_io = psutil.net_io_counters()
            if net_io.bytes_sent > 0:
                await self.check_data_transfer_anomalies(net_io)
                
        except Exception as e:
            logger.error(f"Error collecting network metrics: {e}")
    
    async def process_new_connections(self, new_connections):
        """Process newly established connections"""
        for local_ip, local_port, remote_ip, remote_port in new_connections:
            # Check if connection is suspicious
            if await self.is_suspicious_connection(remote_ip, remote_port):
                await self.create_network_alert(
                    title="Suspicious Network Connection Detected",
                    description=f"New connection to {remote_ip}:{remote_port} from {local_ip}:{local_port}",
                    severity="medium",
                    category="network_anomaly",
                    source="Network Monitor",
                    entities=[
                        {"type": "ip_address", "value": remote_ip},
                        {"type": "port", "value": str(remote_port)}
                    ]
                )
    
    async def is_suspicious_connection(self, ip: str, port: int) -> bool:
        """Check if connection is suspicious"""
        try:
            # Check for known suspicious ports
            suspicious_ports = [22, 23, 80, 443, 3389, 5900, 1433, 3306]
            if port in suspicious_ports and not self.is_internal_ip(ip):
                return True
            
            # Check for high-numbered ports (potential backdoors)
            if port > 10000 and not self.is_internal_ip(ip):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking suspicious connection: {e}")
            return False
    
    def is_internal_ip(self, ip: str) -> bool:
        """Check if IP is internal/private"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            # Private IP ranges
            if parts[0] == '10':
                return True
            if parts[0] == '172' and 16 <= int(parts[1]) <= 31:
                return True
            if parts[0] == '192' and parts[1] == '168':
                return True
            if parts[0] == '127':
                return True
                
            return False
            
        except:
            return False
    
    async def check_data_transfer_anomalies(self, net_io):
        """Check for unusual data transfer patterns"""
        try:
            # Convert bytes to MB
            mb_sent = net_io.bytes_sent / (1024 * 1024)
            mb_recv = net_io.bytes_recv / (1024 * 1024)
            
            # Check for high data transfer
            if mb_sent > self.alert_thresholds['data_transfer_mb']:
                await self.create_network_alert(
                    title="High Data Transfer Detected",
                    description=f"Unusual outbound data transfer: {mb_sent:.2f} MB",
                    severity="high",
                    category="data_exfiltration",
                    source="Network Monitor",
                    entities=[{"type": "anomaly", "value": "high_transfer"}]
                )
                
        except Exception as e:
            logger.error(f"Error checking data transfer: {e}")
    
    async def detect_anomalies(self):
        """Detect various network anomalies"""
        try:
            # Check for port scanning activity
            await self.detect_port_scanning()
            
            # Check for unusual connection patterns
            await self.detect_connection_patterns()
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
    
    async def detect_port_scanning(self):
        """Detect potential port scanning activity"""
        try:
            connections = psutil.net_connections(kind='inet')
            ip_connection_count = {}
            
            for conn in connections:
                if conn.raddr and not self.is_internal_ip(conn.raddr.ip):
                    ip = conn.raddr.ip
                    ip_connection_count[ip] = ip_connection_count.get(ip, 0) + 1
            
            # Flag IPs with many connections
            for ip, count in ip_connection_count.items():
                if count > 20:  # Threshold for potential scanning
                    await self.create_network_alert(
                        title="Potential Port Scanning Detected",
                        description=f"IP {ip} has {count} connections",
                        severity="high",
                        category="port_scanning",
                        source="Network Monitor",
                        entities=[{"type": "ip_address", "value": ip}]
                    )
                    
        except Exception as e:
            logger.error(f"Error detecting port scanning: {e}")
    
    async def detect_connection_patterns(self):
        """Detect unusual connection patterns"""
        try:
            # Get active interfaces
            interfaces = netifaces.interfaces()
            
            for interface in interfaces:
                try:
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr['addr']
                            if not self.is_internal_ip(ip):
                                await self.create_network_alert(
                                    title="External IP Interface Detected",
                                    description=f"External IP {ip} found on interface {interface}",
                                    severity="medium",
                                    category="network_configuration",
                                    source="Network Monitor",
                                    entities=[{"type": "ip_address", "value": ip}]
                                )
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error detecting connection patterns: {e}")
    
    async def create_network_alert(self, title: str, description: str, severity: str, 
                                category: str, source: str, entities: List[Dict[str, str]]):
        """Create a network security alert"""
        try:
            alert_doc = AlertDocument(
                title=title,
                description=description,
                severity=severity,
                source=source,
                category=category,
                confidence=75,  # Default confidence for network detections
                entities=entities,
                location={"type": "network", "source": "system_monitor"},
                context={"detection_method": "real_time_monitoring"},
                raw_data={"timestamp": datetime.now().isoformat()}
            )
            
            # Calculate criticality score
            alert_doc.update_criticality_score()
            
            # Store in memory for real-time display
            alert_data = alert_doc.dict()
            alert_data['_id'] = str(len(self.memory_alerts))  # Simple ID
            alert_data['timestamp'] = datetime.now().isoformat()
            self.memory_alerts.append(alert_data)
            
            # Keep only last 50 alerts in memory
            if len(self.memory_alerts) > 50:
                self.memory_alerts = self.memory_alerts[-50:]
            
            # Try to save to database
            from app.core.database import db_manager
            try:
                db = db_manager.get_database()
                alerts_collection = db.alerts
                await alerts_collection.insert_one(alert_doc.dict())
                logger.info(f"Network alert saved to database: {title}")
            except Exception as db_error:
                logger.error(f"Database save failed: {db_error}")
                # Memory storage is enough for real-time display
                logger.info(f"Network alert stored in memory: {title} - {description}")
        
        except Exception as e:
            logger.error(f"Error creating network alert: {e}")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get current system network information"""
        try:
            return {
                "interfaces": netifaces.interfaces(),
                "connections": len(psutil.net_connections(kind='inet')),
                "io_stats": psutil.net_io_counters()._asdict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring_active = False
        logger.info("Network monitoring stopped")


# Global monitor instance
network_monitor = NetworkMonitor()
