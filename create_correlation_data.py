#!/usr/bin/env python3
"""
Create Sample Correlation Data for SOC Correlation Engine
Creates correlation groups based on existing alerts
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

async def create_sample_correlations():
    """Create sample correlation groups based on existing alerts"""
    print("🔗 Creating sample correlation groups...")
    
    # First, get existing alerts
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/alerts/?limit=50") as response:
                if response.status != 200:
                    print("❌ Failed to get alerts for correlation")
                    return
                
                alerts = await response.json()
                print(f"✅ Found {len(alerts)} alerts for correlation")
                
                # Create correlation groups based on similar properties
                correlation_groups = []
                
                # Group 1: IP-based correlations
                ip_alerts = [alert for alert in alerts if alert.get('source_ip')]
                if len(ip_alerts) >= 2:
                    correlation_groups.append({
                        "name": "IP-Based Attack Pattern",
                        "description": "Multiple alerts from same source IP addresses",
                        "correlation_type": "network",
                        "status": "active",
                        "severity": "high",
                        "confidence_score": 85,
                        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "entities": list(set([alert.get('source_ip') for alert in ip_alerts[:5]])),
                        "alert_count": len(ip_alerts)
                    })
                
                # Group 2: Severity-based correlations
                critical_alerts = [alert for alert in alerts if alert.get('severity') == 'critical']
                if len(critical_alerts) >= 2:
                    correlation_groups.append({
                        "name": "Critical Alert Cluster",
                        "description": "Multiple critical severity alerts detected",
                        "correlation_type": "severity",
                        "status": "investigating",
                        "severity": "critical",
                        "confidence_score": 92,
                        "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
                        "entities": [alert.get('title', 'Unknown') for alert in critical_alerts[:3]],
                        "alert_count": len(critical_alerts)
                    })
                
                # Group 3: Category-based correlations
                malware_alerts = [alert for alert in alerts if alert.get('category') == 'malware']
                if len(malware_alerts) >= 2:
                    correlation_groups.append({
                        "name": "Malware Activity Cluster",
                        "description": "Multiple malware-related alerts detected",
                        "correlation_type": "category",
                        "status": "active",
                        "severity": "high",
                        "confidence_score": 88,
                        "created_at": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "entities": [alert.get('source_ip', 'Unknown') for alert in malware_alerts[:3]],
                        "alert_count": len(malware_alerts)
                    })
                
                # Group 4: Time-based correlations
                recent_alerts = [alert for alert in alerts if alert.get('timestamp')]
                if len(recent_alerts) >= 3:
                    correlation_groups.append({
                        "name": "Temporal Attack Pattern",
                        "description": "Alerts detected within similar timeframes",
                        "correlation_type": "temporal",
                        "status": "active",
                        "severity": "medium",
                        "confidence_score": 75,
                        "created_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                        "entities": [alert.get('title', 'Unknown') for alert in recent_alerts[:4]],
                        "alert_count": len(recent_alerts)
                    })
                
                # Group 5: Source-based correlations
                source_alerts = [alert for alert in alerts if alert.get('source') == 'Authentication System']
                if len(source_alerts) >= 2:
                    correlation_groups.append({
                        "name": "Authentication System Alerts",
                        "description": "Multiple alerts from authentication system",
                        "correlation_type": "source",
                        "status": "resolved",
                        "severity": "medium",
                        "confidence_score": 70,
                        "created_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                        "entities": [alert.get('title', 'Unknown') for alert in source_alerts[:3]],
                        "alert_count": len(source_alerts)
                    })
                
                # Create correlation groups
                for i, group in enumerate(correlation_groups):
                    try:
                        # Try different endpoint formats
                        endpoints_to_try = [
                            f"{BASE_URL}/api/correlations/",
                            f"{BASE_URL}/api/correlations"
                        ]
                        
                        for endpoint in endpoints_to_try:
                            async with session.post(endpoint, json=group) as response:
                                if response.status == 200:
                                    print(f"✅ Correlation group {i+1} created: {group['name']}")
                                    break
                                elif response.status == 422:
                                    # Try with minimal required fields
                                    minimal_group = {
                                        "name": group["name"],
                                        "correlation_type": group["correlation_type"],
                                        "status": group["status"],
                                        "severity": group["severity"],
                                        "confidence_score": group["confidence_score"],
                                        "created_at": group["created_at"]
                                    }
                                    async with session.post(endpoint, json=minimal_group) as min_response:
                                        if min_response.status == 200:
                                            print(f"✅ Correlation group {i+1} created (minimal): {group['name']}")
                                            break
                        else:
                            print(f"❌ Failed to create correlation group {i+1}")
                            
                    except Exception as e:
                        print(f"❌ Error creating correlation group {i+1}: {e}")
                
                # Verify correlations
                await verify_correlations()
                
        except Exception as e:
            print(f"❌ Error in correlation creation: {e}")

async def verify_correlations():
    """Verify correlation groups were created"""
    print("🔍 Verifying correlation groups...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/correlations/?limit=20") as response:
                if response.status == 200:
                    correlations = await response.json()
                    print(f"✅ Found {len(correlations)} correlation groups")
                    
                    for corr in correlations:
                        print(f"  - {corr.get('name', 'Unknown')}: {corr.get('correlation_type', 'unknown')}")
                else:
                    print(f"❌ Failed to get correlations: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error verifying correlations: {e}")

async def main():
    """Main function"""
    print("🚀 Creating Sample Correlation Data")
    print("=" * 50)
    
    await create_sample_correlations()
    
    print("\n" + "=" * 50)
    print("✅ Correlation data creation completed!")
    print("📊 Correlation section should now display data")
    print("\nNext steps:")
    print("1. Open dashboard: http://localhost:8000")
    print("2. Navigate to Correlation section")
    print("3. Verify correlation groups display")

if __name__ == "__main__":
    asyncio.run(main())
