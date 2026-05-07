import requests
import json
from datetime import datetime

def debug_browser_logs():
    """Debug what the browser is actually seeing"""
    try:
        print("🔍 DEBUGGING: What browser actually sees...")
        
        # Test direct API call (what browser would call)
        print("\n📡 Testing direct API call...")
        response = requests.get("http://127.0.0.1:8000/api/logs?limit=10")
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ API returned {len(logs)} logs")
            
            # Show raw data structure
            if logs:
                print(f"\n📋 Raw log structure:")
                sample_log = logs[0]
                for key, value in sample_log.items():
                    print(f"  {key}: {str(value)[:50]}...")
                
                # Check timestamp format
                timestamp = sample_log.get('timestamp', '')
                print(f"\n🕐 Timestamp format: {timestamp}")
                
                try:
                    parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    print(f"🕐 Parsed time: {parsed.strftime('%H:%M:%S')}")
                except Exception as e:
                    print(f"❌ Timestamp parse error: {e}")
                
                # Show order
                print(f"\n📊 Log order check:")
                for i, log in enumerate(logs[:5]):
                    ts = log.get('timestamp', '')
                    try:
                        parsed = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        time_str = parsed.strftime('%H:%M:%S')
                        print(f"  {i+1}. {time_str}")
                    except:
                        print(f"  {i+1}. {ts}")
            else:
                print("⚠️ No logs returned from API")
                
        else:
            print(f"❌ API failed: {response.status_code}")
            print(f"Response: {response.text}")
        
        # Test with different parameters
        print(f"\n🔍 Testing with different parameters...")
        
        # Test limit=5
        response5 = requests.get("http://127.0.0.1:8000/api/logs?limit=5")
        if response5.status_code == 200:
            logs5 = response5.json()
            print(f"✅ limit=5: {len(logs5)} logs")
        
        # Test without parameters
        response_default = requests.get("http://127.0.0.1:8000/api/logs")
        if response_default.status_code == 200:
            logs_default = response_default.json()
            print(f"✅ default: {len(logs_default)} logs")
        
        # Check if logs are being generated
        print(f"\n🔄 Checking log generation...")
        for i in range(3):
            response = requests.get("http://127.0.0.1:8000/api/logs?limit=1")
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    latest_timestamp = logs[0].get('timestamp', '')
                    print(f"  Check {i+1}: {latest_timestamp}")
            import time
            time.sleep(2)
            
    except Exception as e:
        print(f"❌ Debug error: {e}")

def check_system_status():
    """Check overall system status"""
    try:
        print(f"\n🔧 System Status Check:")
        
        # Check if system is running
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ System is running")
        else:
            print("❌ System health check failed")
        
        # Check alerts API
        alerts_response = requests.get("http://127.0.0.1:8000/api/alerts?limit=5")
        if alerts_response.status_code == 200:
            alerts = alerts_response.json()
            print(f"✅ Alerts API: {len(alerts)} alerts")
        else:
            print(f"❌ Alerts API failed: {alerts_response.status_code}")
        
        # Check WebSocket endpoint
        print(f"🔌 WebSocket should be available at: ws://127.0.0.1:8000/ws/[client_id]")
        
    except Exception as e:
        print(f"❌ Status check error: {e}")

if __name__ == "__main__":
    debug_browser_logs()
    check_system_status()
