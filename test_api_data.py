import requests
import json
from datetime import datetime

def test_api_data():
    try:
        print("🔍 Testing API data sources...")
        
        # Test alerts API
        print("\n📊 Testing alerts API...")
        alerts_response = requests.get("http://127.0.0.1:8000/api/alerts/?limit=10")
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            print(f"✅ Alerts API returned {len(alerts)} alerts")
            
            if alerts:
                sample_alert = alerts[0]
                print(f"📋 Sample alert:")
                print(f"  ID: {sample_alert.get('_id', 'N/A')}")
                print(f"  Title: {sample_alert.get('title', 'N/A')}")
                print(f"  Timestamp: {sample_alert.get('timestamp', 'N/A')}")
                print(f"  Severity: {sample_alert.get('severity', 'N/A')}")
                
                # Check if timestamp is old
                if 'timestamp' in sample_alert:
                    try:
                        alert_time = datetime.fromisoformat(sample_alert['timestamp'].replace('Z', '+00:00'))
                        current_time = datetime.now(alert_time.tzinfo)
                        time_diff = (current_time - alert_time).total_seconds() / 3600  # hours
                        print(f"  ⏰ Time difference: {time_diff:.1f} hours ago")
                        
                        if time_diff > 4:  # More than 4 hours old
                            print(f"  ❌ OLD DATA DETECTED!")
                        else:
                            print(f"  ✅ Fresh data")
                    except:
                        print(f"  ⚠️ Could not parse timestamp")
            else:
                print("✅ No alerts found - system is fresh")
        else:
            print(f"❌ Alerts API failed: {alerts_response.status_code}")
        
        # Test logs API
        print("\n📝 Testing logs API...")
        logs_response = requests.get("http://127.0.0.1:8000/api/logs/?limit=10")
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"✅ Logs API returned {len(logs)} logs")
            
            if logs:
                sample_log = logs[0]
                print(f"📋 Sample log:")
                print(f"  ID: {sample_log.get('_id', 'N/A')}")
                print(f"  Message: {sample_log.get('message', 'N/A')[:50]}...")
                print(f"  Timestamp: {sample_log.get('timestamp', 'N/A')}")
                print(f"  Level: {sample_log.get('level', 'N/A')}")
                
                # Check if timestamp is old
                if 'timestamp' in sample_log:
                    try:
                        log_time = datetime.fromisoformat(sample_log['timestamp'].replace('Z', '+00:00'))
                        current_time = datetime.now(log_time.tzinfo)
                        time_diff = (current_time - log_time).total_seconds() / 3600  # hours
                        print(f"  ⏰ Time difference: {time_diff:.1f} hours ago")
                        
                        if time_diff > 4:  # More than 4 hours old
                            print(f"  ❌ OLD DATA DETECTED!")
                        else:
                            print(f"  ✅ Fresh data")
                    except:
                        print(f"  ⚠️ Could not parse timestamp")
            else:
                print("✅ No logs found - system is fresh")
        else:
            print(f"❌ Logs API failed: {logs_response.status_code}")
        
        # Test database directly
        print("\n🗄️ Testing database directly...")
        test_database_directly()
        
    except Exception as e:
        print(f"❌ Error testing API: {e}")

def test_database_directly():
    try:
        import asyncio
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        async def check_db():
            from app.core.database import DatabaseManager
            
            db = DatabaseManager()
            await db.connect()
            
            database = db.get_database()
            
            # Check alerts
            alerts_collection = database.alerts
            alerts_count = await alerts_collection.count_documents({})
            print(f"📊 Database alerts count: {alerts_count}")
            
            if alerts_count > 0:
                sample_alert = await alerts_collection.find_one()
                if sample_alert and 'timestamp' in sample_alert:
                    print(f"  📋 Sample DB alert timestamp: {sample_alert['timestamp']}")
            
            # Check logs
            logs_collection = database.logs
            logs_count = await logs_collection.count_documents({})
            print(f"📝 Database logs count: {logs_count}")
            
            if logs_count > 0:
                sample_log = await logs_collection.find_one()
                if sample_log and 'timestamp' in sample_log:
                    print(f"  📋 Sample DB log timestamp: {sample_log['timestamp']}")
            
            await db.disconnect()
        
        asyncio.run(check_db())
        
    except Exception as e:
        print(f"❌ Error testing database: {e}")

if __name__ == "__main__":
    test_api_data()
