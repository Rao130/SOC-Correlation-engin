#!/usr/bin/env python3
"""
Direct MongoDB Correlation Data Insert
Creates correlation groups directly in MongoDB without API
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

# MongoDB connection
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "soc_correlation_engine"

async def create_correlation_data_directly():
    """Create correlation data directly in MongoDB"""
    print("🔗 Creating correlation data directly in MongoDB...")
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    correlation_collection = db.correlation_groups
    
    # Sample correlation groups
    correlation_groups = [
        {
            "name": "IP-Based Attack Pattern",
            "description": "Multiple alerts from same source IP addresses",
            "correlation_type": "network",
            "status": "active",
            "severity": "high",
            "confidence_score": 85,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "entities": ["192.168.1.100", "10.0.0.50", "172.16.0.25"],
            "alert_count": 15,
            "correlation_score": 85
        },
        {
            "name": "Critical Alert Cluster",
            "description": "Multiple critical severity alerts detected",
            "correlation_type": "severity",
            "status": "investigating",
            "severity": "critical",
            "confidence_score": 92,
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
            "entities": ["Malware Signature", "DDoS Attack", "Zero-Day Exploit"],
            "alert_count": 8,
            "correlation_score": 92
        },
        {
            "name": "Malware Activity Cluster",
            "description": "Multiple malware-related alerts detected",
            "correlation_type": "category",
            "status": "active",
            "severity": "high",
            "confidence_score": 88,
            "created_at": (datetime.now() - timedelta(hours=3)).isoformat(),
            "entities": ["malware-sample.exe", "trojan.binary"],
            "alert_count": 12,
            "correlation_score": 88
        },
        {
            "name": "Temporal Attack Pattern",
            "description": "Alerts detected within similar timeframes",
            "correlation_type": "temporal",
            "status": "active",
            "severity": "medium",
            "confidence_score": 75,
            "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
            "entities": ["Suspicious Login", "Network Anomaly", "Data Access"],
            "alert_count": 6,
            "correlation_score": 75
        },
        {
            "name": "Authentication System Alerts",
            "description": "Multiple alerts from authentication system",
            "correlation_type": "source",
            "status": "resolved",
            "severity": "medium",
            "confidence_score": 70,
            "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
            "entities": ["Failed Login", "Suspicious Activity"],
            "alert_count": 4,
            "correlation_score": 70
        }
    ]
    
    try:
        # Clear existing correlations
        await correlation_collection.delete_many({})
        print("🗑️ Cleared existing correlation data")
        
        # Insert correlation groups
        result = await correlation_collection.insert_many(correlation_groups)
        print(f"✅ Created {len(result.inserted_ids)} correlation groups")
        
        # Verify data
        count = await correlation_collection.count_documents({})
        print(f"✅ Total correlations in database: {count}")
        
        # Show created correlations
        correlations = await correlation_collection.find().to_list()
        for corr in correlations:
            print(f"  - {corr['name']}: {corr['correlation_type']} ({corr['status']})")
        
    except Exception as e:
        print(f"❌ Error creating correlation data: {e}")
    finally:
        client.close()

async def main():
    """Main function"""
    print("🚀 Direct MongoDB Correlation Data Creation")
    print("=" * 50)
    
    await create_correlation_data_directly()
    
    print("\n" + "=" * 50)
    print("✅ Correlation data creation completed!")
    print("📊 Correlation section should now display data")
    print("\nNext steps:")
    print("1. Open dashboard: http://localhost:8000")
    print("2. Navigate to Correlation section")
    print("3. Verify correlation groups display")

if __name__ == "__main__":
    asyncio.run(main())
