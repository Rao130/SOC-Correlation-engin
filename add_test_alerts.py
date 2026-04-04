import json
import os
from datetime import datetime, timedelta
import random

def add_test_alerts():
    """Add test alerts directly to file database"""
    
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    
    # Load existing alerts
    alerts_file = "data/alerts.json"
    alerts = []
    
    if os.path.exists(alerts_file):
        try:
            with open(alerts_file, 'r', encoding='utf-8') as f:
                alerts = json.load(f)
        except:
            alerts = []
    
    # Create test alerts
    test_alerts = [
        {
            "_id": "alert_1",
            "title": "Brute Force Login Attack Detected",
            "description": "Multiple failed login attempts detected from single IP address",
            "severity": "high",
            "source": "Attack Simulator",
            "category": "intrusion",
            "confidence": 85,
            "status": "new",
            "criticality_score": 85,
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "entities": [
                {
                    "type": "ip",
                    "value": "192.168.1.100",
                    "reputation": {"score": 0.2}
                }
            ],
            "location": {
                "country": "Unknown",
                "country_code": "XX"
            },
            "context": {
                "tags": ["brute_force", "login", "attack"]
            }
        },
        {
            "_id": "alert_2",
            "title": "SQL Injection Attack Detected",
            "description": "SQL injection patterns detected in web requests",
            "severity": "critical",
            "source": "Attack Simulator",
            "category": "intrusion",
            "confidence": 95,
            "status": "new",
            "criticality_score": 95,
            "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            "entities": [
                {
                    "type": "ip",
                    "value": "10.0.0.50",
                    "reputation": {"score": 0.1}
                }
            ],
            "context": {
                "tags": ["sql_injection", "web_attack", "critical"]
            }
        },
        {
            "_id": "alert_3",
            "title": "DDoS Attack Detected",
            "description": "High volume of requests detected from multiple sources",
            "severity": "high",
            "source": "Attack Simulator",
            "category": "ddos",
            "confidence": 90,
            "status": "new",
            "criticality_score": 90,
            "timestamp": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
            "entities": [
                {
                    "type": "ip",
                    "value": "172.16.0.1",
                    "reputation": {"score": 0.3}
                }
            ],
            "context": {
                "tags": ["ddos", "network_attack", "high_volume"]
            }
        },
        {
            "_id": "alert_4",
            "title": "Suspicious IP Activity",
            "description": "Connection from known malicious IP address",
            "severity": "medium",
            "source": "Attack Simulator",
            "category": "intrusion",
            "confidence": 75,
            "status": "new",
            "criticality_score": 75,
            "timestamp": (datetime.utcnow() - timedelta(minutes=1)).isoformat(),
            "created_at": (datetime.utcnow() - timedelta(minutes=1)).isoformat(),
            "entities": [
                {
                    "type": "ip",
                    "value": "203.0.113.1",
                    "reputation": {"score": 0.1}
                }
            ],
            "context": {
                "tags": ["suspicious_ip", "malicious", "threat_intel"]
            }
        },
        {
            "_id": "alert_5",
            "title": "Malware Detection Alert",
            "description": "Malicious file or behavior detected",
            "severity": "critical",
            "source": "Attack Simulator",
            "category": "malware",
            "confidence": 98,
            "status": "new",
            "criticality_score": 98,
            "timestamp": datetime.utcnow().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "entities": [
                {
                    "type": "hash",
                    "value": "a1b2c3d4e5f6789...",
                    "reputation": {"score": 0.05}
                }
            ],
            "context": {
                "tags": ["malware", "virus", "critical"]
            }
        }
    ]
    
    # Add test alerts to existing alerts
    alerts.extend(test_alerts)
    
    # Save to file
    with open(alerts_file, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, indent=2, default=str)
    
    print(f"Added {len(test_alerts)} test alerts to {alerts_file}")
    print(f"Total alerts in database: {len(alerts)}")
    print("\nAlerts added:")
    for alert in test_alerts:
        print(f"  - {alert['title']} ({alert['severity']})")

if __name__ == "__main__":
    add_test_alerts()
