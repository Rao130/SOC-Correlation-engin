#!/usr/bin/env python3
"""
Test Data Generator for SOC Correlation Engine
Creates sample alerts, correlations, and reputation data in MongoDB
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

# Sample data templates
SAMPLE_ALERTS = [
    {
        "title": "Suspicious Login Activity Detected",
        "description": "Multiple failed login attempts from unusual IP address",
        "severity": "high",
        "category": "intrusion",
        "source": "Authentication System",
        "confidence_score": 85
    },
    {
        "title": "Malware Signature Detected",
        "description": "Known malware signature found in downloaded file",
        "severity": "critical",
        "category": "malware",
        "source": "Antivirus Scanner",
        "confidence_score": 95
    },
    {
        "title": "Unusual Network Traffic Pattern",
        "description": "Anomalous traffic detected on internal network",
        "severity": "medium",
        "category": "anomaly",
        "source": "Network Monitor",
        "confidence_score": 70
    },
    {
        "title": "Phishing Email Reported",
        "description": "User reported suspicious email attempting credential theft",
        "severity": "high",
        "category": "phishing",
        "source": "Email Security",
        "confidence_score": 90
    },
    {
        "title": "DDoS Attack in Progress",
        "description": "High volume of requests detected from multiple sources",
        "severity": "critical",
        "category": "ddos",
        "source": "Firewall",
        "confidence_score": 98
    },
    {
        "title": "Data Access Anomaly",
        "description": "Unusual data access patterns detected in database",
        "severity": "medium",
        "category": "data_breach",
        "source": "Database Monitor",
        "confidence_score": 75
    },
    {
        "title": "Policy Violation Detected",
        "description": "User attempting to access restricted resources",
        "severity": "low",
        "category": "policy_violation",
        "source": "Access Control",
        "confidence_score": 60
    },
    {
        "title": "Zero-Day Exploit Attempt",
        "description": "Unknown vulnerability exploitation attempt detected",
        "severity": "critical",
        "category": "intrusion",
        "source": "IDS/IPS",
        "confidence_score": 92
    }
]

SAMPLE_ENTITIES = [
    {"entity": "192.168.1.100", "entity_type": "ip_address"},
    {"entity": "10.0.0.50", "entity_type": "ip_address"},
    {"entity": "suspicious-domain.com", "entity_type": "domain"},
    {"entity": "malware-sample.exe", "entity_type": "file_hash"},
    {"entity": "admin@company.com", "entity_type": "email"},
    {"entity": "external-server.net", "entity_type": "domain"},
    {"entity": "172.16.0.25", "entity_type": "ip_address"},
    {"entity": "trojan.binary", "entity_type": "file_hash"}
]

async def create_test_alerts(session, count=10):
    """Create test alerts in MongoDB"""
    print(f"Creating {count} test alerts...")
    
    for i in range(count):
        alert_data = random.choice(SAMPLE_ALERTS).copy()
        alert_data.update({
            "status": random.choice(["new", "investigating", "resolved", "false_positive"]),
            "source_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "destination_ip": f"10.0.{random.randint(1,255)}.{random.randint(1,255)}",
            "user": f"user{random.randint(1,100)}",
            "timestamp": (datetime.now() - timedelta(hours=random.randint(0,72))).isoformat()
        })
        
        try:
            async with session.post(f"{BASE_URL}/api/alerts/", json=alert_data) as response:
                if response.status == 200:
                    print(f"✅ Alert {i+1} created successfully")
                else:
                    print(f"❌ Failed to create alert {i+1}: {response.status}")
        except Exception as e:
            print(f"❌ Error creating alert {i+1}: {e}")

async def create_test_reputation_data(session):
    """Create test reputation data"""
    print("Creating test reputation data...")
    
    for entity_data in SAMPLE_ENTITIES:
        reputation_data = {
            "entity": entity_data["entity"],
            "entity_type": entity_data["entity_type"],
            "aggregated_score": random.uniform(0, 100),
            "risk_level": random.choice(["malicious", "suspicious", "benign", "unknown"]),
            "classification": {
                "category": random.choice(["malware", "phishing", "botnet", "benign"]),
                "confidence": random.uniform(0.5, 1.0)
            },
            "metrics": {
                "alert_count": random.randint(0, 50),
                "first_seen": (datetime.now() - timedelta(days=random.randint(1,365))).isoformat(),
                "last_seen": datetime.now().isoformat()
            },
            "tags": random.sample(["threat", "blocked", "monitored", "whitelisted"], k=random.randint(1,3))
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/reputation/check", json=reputation_data) as response:
                if response.status == 200:
                    print(f"✅ Reputation data created for {entity_data['entity']}")
                else:
                    print(f"❌ Failed to create reputation data: {response.status}")
        except Exception as e:
            print(f"❌ Error creating reputation data: {e}")

async def create_test_correlations(session):
    """Create test correlation data"""
    print("Creating test correlation data...")
    
    correlation_types = ["temporal", "network", "entity", "behavioral"]
    
    for i in range(5):
        correlation_data = {
            "name": f"Correlation Group {i+1}",
            "description": f"Test correlation group for related security events",
            "correlation_type": random.choice(correlation_types),
            "status": random.choice(["active", "investigating", "resolved"]),
            "severity": random.choice(["low", "medium", "high", "critical"]),
            "alert_count": random.randint(2, 10),
            "confidence_score": random.uniform(0.6, 0.95),
            "created_at": (datetime.now() - timedelta(hours=random.randint(1,48))).isoformat(),
            "entities": random.sample([e["entity"] for e in SAMPLE_ENTITIES], k=random.randint(2,4))
        }
        
        try:
            async with session.post(f"{BASE_URL}/api/correlations/", json=correlation_data) as response:
                if response.status == 200:
                    print(f"✅ Correlation {i+1} created successfully")
                else:
                    print(f"❌ Failed to create correlation {i+1}: {response.status}")
        except Exception as e:
            print(f"❌ Error creating correlation {i+1}: {e}")

async def verify_data():
    """Verify data was created successfully"""
    print("Verifying created data...")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Check alerts
            async with session.get(f"{BASE_URL}/api/alerts/?limit=50") as response:
                if response.status == 200:
                    alerts = await response.json()
                    print(f"✅ Found {len(alerts)} alerts in database")
                else:
                    print(f"❌ Failed to get alerts: {response.status}")
            
            # Check reputation data
            async with session.get(f"{BASE_URL}/api/reputation/?limit=50") as response:
                if response.status == 200:
                    reputation = await response.json()
                    print(f"✅ Found {len(reputation)} reputation entries")
                else:
                    print(f"❌ Failed to get reputation data: {response.status}")
            
            # Check correlations
            async with session.get(f"{BASE_URL}/api/correlations/?limit=50") as response:
                if response.status == 200:
                    correlations = await response.json()
                    print(f"✅ Found {len(correlations)} correlation groups")
                else:
                    print(f"❌ Failed to get correlations: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error verifying data: {e}")

async def main():
    """Main function to generate test data"""
    print("🚀 Starting SOC Correlation Engine Test Data Generation")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        # Create test data
        await create_test_alerts(session, count=15)
        await create_test_reputation_data(session)
        await create_test_correlations(session)
        
        # Verify data
        await verify_data()
    
    print("\n" + "=" * 60)
    print("✅ Test data generation completed!")
    print("📊 Dashboard should now display real data")
    print("🔍 Test filters and functionality")
    print("\nNext steps:")
    print("1. Open dashboard: http://localhost:8000")
    print("2. Test filter functionality")
    print("3. Verify dashboard displays data correctly")
    print("4. Test all CRUD operations")

if __name__ == "__main__":
    asyncio.run(main())
