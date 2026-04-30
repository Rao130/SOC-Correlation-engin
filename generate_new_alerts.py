#!/usr/bin/env python3
"""
Quick script to generate new alerts with current timestamps
"""

import sys
import asyncio
import datetime
from datetime import datetime as dt
sys.path.append('.')

async def generate_current_alerts():
    try:
        from app.core.database import DatabaseManager
        from app.models.alert import AlertDocument, Severity, AlertCategory, AlertStatus
        
        print('🔄 Generating New Alerts with Current Timestamps')
        print('='*50)
        
        db = DatabaseManager()
        await db.connect()
        
        # Generate 5 new alerts with current timestamps
        current_time = dt.now()
        alert_types = [
            {
                'title': 'Real-time Brute Force Attack',
                'severity': Severity.HIGH,
                'category': AlertCategory.NETWORK_ANOMALY,
                'description': 'Active brute force attack detected on authentication server'
            },
            {
                'title': 'Live Malware Detection',
                'severity': Severity.CRITICAL,
                'category': AlertCategory.MALWARE,
                'description': 'Real-time malware signature detected in network traffic'
            },
            {
                'title': 'Active Port Scanning',
                'severity': Severity.MEDIUM,
                'category': AlertCategory.PORT_SCANNING,
                'description': 'Ongoing port scanning activity from external IP'
            },
            {
                'title': 'Current SQL Injection Attempt',
                'severity': Severity.HIGH,
                'category': AlertCategory.OTHER,
                'description': 'SQL injection attempt detected on web application'
            },
            {
                'title': 'Recent Phishing Campaign',
                'severity': Severity.MEDIUM,
                'category': AlertCategory.PHISHING,
                'description': 'New phishing campaign targeting internal users'
            }
        ]
        
        alerts_collection = db.database.alerts
        
        for i, alert_data in enumerate(alert_types):
            # Create alert with current timestamp
            alert = AlertDocument(
                alert_id=f"realtime_{current_time.strftime('%Y%m%d_%H%M%S')}_{i+1}",
                title=alert_data['title'],
                description=alert_data['description'],
                severity=alert_data['severity'],
                category=alert_data['category'],
                status=AlertStatus.NEW,
                source=f"realtime_generator_{i+1}",
                source_ip=f"192.168.1.{100+i}",
                destination_ip="10.0.0.1",
                confidence=85 + i*2,
                timestamp=current_time - datetime.timedelta(minutes=i),  # Slightly different times
                raw_data={
                    'source': 'realtime_generator',
                    'generated_at': current_time.isoformat()
                }
            )
            
            # Save to database
            result = await alerts_collection.insert_one(alert.dict(exclude={'id'}))
            print(f'✅ Generated alert {i+1}: {alert_data["title"]}')
            print(f'   📅 Time: {alert.timestamp}')
            print(f'   🆔 ID: {result.inserted_id}')
            print()
        
        # Verify the alerts were saved
        latest_alerts = await alerts_collection.find().sort('timestamp', -1).limit(5).to_list(None)
        
        print('🔍 Verification - Latest 5 Alerts:')
        for i, alert in enumerate(latest_alerts):
            timestamp = alert.get('timestamp', 'N/A')
            title = alert.get('title', 'N/A')
            print(f'{i+1}. {title}')
            print(f'   📅 Time: {timestamp}')
            print()
        
        await db.disconnect()
        print('🎉 New alerts generated successfully!')
        print('📱 Refresh your web interface to see the new alerts!')
        
    except Exception as e:
        print(f'❌ Error generating alerts: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_current_alerts())
