"""
Real-time Security Data Generator for SOC Correlation Engine
WARNING: This is for testing/demo only. Disable in production SIEM mode via ENABLE_DATA_GENERATION=false

Generates realistic security events, alerts, and analytics data
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import ipaddress
from app.core.logging import logger
from app.core.database import get_db
from app.core.config import settings
from app.models.alert import AlertDocument

class RealDataGenerator:
    """Generates realistic security data for testing/demo purposes only"""
    
    # Class-level flag to track if generation is enabled
    _enabled = False
    
    def __init__(self):
        self.active = False
        self.generated_alerts = []
        self.threat_actors = [
            "APT28", "Lazarus Group", "Fin7", "Carbanak", "Equation Group",
            "DarkSide", "Conti", "REvil", "Wizard Spider", "Tick"
        ]
        
        self.attack_types = [
            "brute_force", "port_scan", "malware", "phishing", "ddos",
            "sql_injection", "xss", "ransomware", "data_exfiltration", "command_injection"
        ]
        
        self.severity_weights = {
            "critical": 0.1,
            "high": 0.2,
            "medium": 0.4,
            "low": 0.3
        }
        
        self.categories = [
            "network_anomaly", "malware", "phishing", "ddos", "intrusion",
            "data_breach", "policy_violation", "anomaly", "other",
            "port_scanning", "data_exfiltration", "network_configuration", "network_monitoring"
        ]
        
        self.source_ips = self._generate_source_ips()
        self.target_assets = [
            "web-server-01", "db-server-01", "file-server-01", "dc-01", "fw-01",
            "vpn-gateway", "mail-server", "app-server-01", "api-gateway", "bastion-host"
        ]
        
    def _generate_source_ips(self) -> List[str]:
        """Generate realistic source IP addresses"""
        ips = []
        
        # Internal IPs
        for i in range(10, 50):
            ips.append(f"192.168.1.{i}")
        for i in range(10, 30):
            ips.append(f"10.0.0.{i}")
            
        # External malicious IPs (simulated)
        malicious_ranges = [
            "185.220.101", "198.98.51", "172.93.95", "199.249.230",
            "45.61.185", "104.244.72", "89.46.232", "176.123.8"
        ]
        
        for base in malicious_ranges:
            for i in range(1, 10):
                ips.append(f"{base}.{i}")
                
        return ips
    
    def _get_random_severity(self) -> str:
        """Get weighted random severity"""
        rand = random.random()
        cumulative = 0
        for severity, weight in self.severity_weights.items():
            cumulative += weight
            if rand <= cumulative:
                return severity
        return "low"
    
    def _generate_geo_location(self, ip: str) -> Dict[str, Any]:
        """Generate realistic geo location for IP"""
        # Simulated geo data based on IP patterns
        if ip.startswith("192.168.") or ip.startswith("10."):
            return {"country": "Internal", "city": "Local Network", "latitude": 0, "longitude": 0}
        elif ip.startswith("185.220"):
            return {"country": "Germany", "city": "Berlin", "latitude": 52.5200, "longitude": 13.4050}
        elif ip.startswith("198.98"):
            return {"country": "Panama", "city": "Panama City", "latitude": 8.9824, "longitude": -79.5199}
        elif ip.startswith("172.93"):
            return {"country": "USA", "city": "Los Angeles", "latitude": 34.0522, "longitude": -118.2437}
        elif ip.startswith("45.61"):
            return {"country": "USA", "city": "Seattle", "latitude": 47.6062, "longitude": -122.3321}
        elif ip.startswith("104.244"):
            return {"country": "Canada", "city": "Toronto", "latitude": 43.6532, "longitude": -79.3832}
        elif ip.startswith("89.46"):
            return {"country": "Russia", "city": "Moscow", "latitude": 55.7558, "longitude": 37.6173}
        elif ip.startswith("176.123"):
            return {"country": "China", "city": "Beijing", "latitude": 39.9042, "longitude": 116.4074}
        else:
            return {"country": "Unknown", "city": "Unknown", "latitude": 0, "longitude": 0}
    
    def _generate_network_alert(self) -> Dict[str, Any]:
        """Generate realistic network security alert"""
        source_ip = random.choice(self.source_ips)
        target_asset = random.choice(self.target_assets)
        attack_type = random.choice(self.attack_types)
        severity = self._get_random_severity()
        category = random.choice(self.categories)
        threat_actor = random.choice(self.threat_actors) if random.random() < 0.3 else None
        
        # Generate alert title and description based on attack type
        alert_templates = {
            "brute_force": {
                "title": f"Brute Force Attack Detected on {target_asset}",
                "description": f"Multiple failed login attempts detected from {source_ip} targeting {target_asset}"
            },
            "port_scan": {
                "title": f"Port Scanning Activity from {source_ip}",
                "description": f"Systematic port scanning detected from {source_ip} targeting multiple services"
            },
            "malware": {
                "title": f"Malware Detection on {target_asset}",
                "description": f"Suspicious malware signature detected on {target_asset}, originating from {source_ip}"
            },
            "phishing": {
                "title": f"Phishing Campaign Detected",
                "description": f"Phishing emails detected targeting users, traced back to {source_ip}"
            },
            "ddos": {
                "title": f"DDoS Attack Against {target_asset}",
                "description": f"Distributed denial of service attack detected against {target_asset} from multiple sources"
            },
            "sql_injection": {
                "title": f"SQL Injection Attempt on {target_asset}",
                "description": f"SQL injection attack detected targeting web application on {target_asset} from {source_ip}"
            },
            "data_exfiltration": {
                "title": f"Data Exfiltration Detected",
                "description": f"Unusual data transfer detected from {target_asset} to external IP {source_ip}"
            }
        }
        
        template = alert_templates.get(attack_type, alert_templates["malware"])
        geo_location = self._generate_geo_location(source_ip)
        
        alert = {
            "title": template["title"],
            "description": template["description"],
            "severity": severity,
            "source": threat_actor if threat_actor else "Security Monitor",
            "category": category,
            "confidence": random.randint(60, 95),
            "status": "new",
            "entities": [
                {"type": "ip_address", "value": source_ip},
                {"type": "domain", "value": target_asset},
                {"type": "anomaly", "value": attack_type}
            ],
            "location": geo_location,
            "context": {
                "attack_pattern": attack_type,
                "threat_actor": threat_actor,
                "mitre_tactics": self._get_mitre_tactics(attack_type),
                "affected_system": target_asset
            },
            "raw_data": {
                "source_ip": source_ip,
                "target_asset": target_asset,
                "attack_type": attack_type,
                "detection_method": "behavioral_analysis",
                "sensor_id": f"sensor_{random.randint(1000, 9999)}"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return alert
    
    def _get_mitre_tactics(self, attack_type: str) -> List[str]:
        """Get MITRE ATT&CK tactics for attack type"""
        tactics_map = {
            "brute_force": ["Credential Access", "Initial Access"],
            "port_scan": ["Discovery", "Reconnaissance"],
            "malware": ["Execution", "Persistence"],
            "phishing": ["Initial Access", "Execution"],
            "ddos": ["Impact"],
            "sql_injection": ["Initial Access", "Execution"],
            "data_exfiltration": ["Collection", "Exfiltration"],
            "ransomware": ["Impact", "Execution"]
        }
        return tactics_map.get(attack_type, ["Execution"])
    
    async def generate_alert_burst(self, count: int = 5):
        """Generate a burst of alerts (for testing/demo)"""
        alerts = []
        for _ in range(count):
            alert_data = self._generate_network_alert()
            alerts.append(alert_data)
            
            # Create alert document
            alert_doc = AlertDocument(**alert_data)
            alert_doc.update_criticality_score()
            
            # Store in memory
            alert_dict = alert_doc.dict()
            alert_dict['_id'] = f"gen_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
            self.generated_alerts.append(alert_dict)
            
            # Try to save to database
            try:
                from app.core.database import db_manager
                db = db_manager.get_database()
                alerts_collection = db.alerts
                await alerts_collection.insert_one(alert_doc.dict())
            except Exception as e:
                logger.warning(f"Failed to save generated alert to database: {e}")
        
        # Keep only last 100 alerts in memory
        if len(self.generated_alerts) > 100:
            self.generated_alerts = self.generated_alerts[-100:]
            
        logger.info(f"Generated {count} security alerts")
        return alerts
    
    async def start_continuous_generation(self):
        """Start continuous alert generation (only if enabled in config)"""
        # Check if data generation is enabled
        if not settings.ENABLE_DATA_GENERATION:
            logger.info("Data generation disabled (ENABLE_DATA_GENERATION=false). Skipping...")
            self.active = False
            return
            
        self.active = True
        RealDataGenerator._enabled = True
        logger.info("Starting continuous security data generation (TESTING/DEMO MODE)...")
        
        while self.active:
            try:
                # Generate 1-2 alerts every 3-8 seconds for more frequent updates
                alert_count = random.randint(1, 2)
                await self.generate_alert_burst(alert_count)
                
                # Reduced delay for more frequent real-time updates
                delay = random.randint(3, 8)
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in continuous generation: {e}")
                await asyncio.sleep(5)
    
    def stop_generation(self):
        """Stop continuous generation"""
        self.active = False
        RealDataGenerator._enabled = False
        logger.info("Stopping security data generation...")
    
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recently generated alerts"""
        return sorted(self.generated_alerts, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics of generated alerts"""
        if not self.generated_alerts:
            return {"total": 0, "by_severity": {}, "by_category": {}}
        
        severity_counts = {}
        category_counts = {}
        
        for alert in self.generated_alerts:
            severity = alert.get('severity', 'unknown')
            category = alert.get('category', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Calculate last hour alerts with error handling
        last_hour_count = 0
        try:
            for a in self.generated_alerts:
                timestamp = a.get('timestamp', '')
                if not timestamp:
                    continue
                    
                try:
                    # Handle both string and datetime objects
                    if isinstance(timestamp, str):
                        # Handle different timestamp formats
                        if timestamp.endswith('Z'):
                            timestamp = timestamp.replace('Z', '+00:00')
                        alert_time = datetime.fromisoformat(timestamp)
                    elif isinstance(timestamp, datetime):
                        alert_time = timestamp
                    else:
                        continue
                        
                    if alert_time > datetime.utcnow() - timedelta(hours=1):
                        last_hour_count += 1
                except (ValueError, TypeError, AttributeError) as e:
                    logger.debug(f"Error parsing timestamp {timestamp}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"Error calculating last hour statistics: {e}")
        
        return {
            "total": len(self.generated_alerts),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "last_hour": last_hour_count
        }

# Global instance
data_generator = RealDataGenerator()
