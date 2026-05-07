import requests
import json
import time
from datetime import datetime

def test_logs_frontend_ordering():
    """Test that logs are properly ordered for frontend display"""
    try:
        print("🔍 Testing logs frontend ordering...")
        
        # Get logs from API
        logs_response = requests.get("http://127.0.0.1:8000/api/logs/?limit=20")
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"✅ Retrieved {len(logs)} logs from API")
            
            if logs:
                print("\n📋 Checking log order (newest first):")
                
                # Show first 5 logs with timestamps
                for i, log in enumerate(logs[:5]):
                    timestamp = log.get('timestamp', 'N/A')
                    message = log.get('message', 'N/A')[:40] + "..."
                    level = log.get('level', 'N/A')
                    
                    try:
                        parsed_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = parsed_time.strftime('%H:%M:%S')
                        print(f"  {i+1}. [{level}] {time_str} - {message}")
                    except:
                        print(f"  {i+1}. [{level}] {timestamp} - {message}")
                
                # Check if timestamps are in descending order
                timestamps = []
                for log in logs:
                    ts = log.get('timestamp', '')
                    try:
                        parsed_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps.append(parsed_time)
                    except:
                        timestamps.append(None)
                
                # Verify descending order
                is_descending = True
                for i in range(min(10, len(timestamps)-1)):
                    if timestamps[i] and timestamps[i+1]:
                        if timestamps[i] < timestamps[i+1]:
                            is_descending = False
                            print(f"❌ Order issue at index {i}: {timestamps[i]} < {timestamps[i+1]}")
                            break
                
                if is_descending:
                    print(f"\n✅ PERFECT: Logs are in descending order (newest first)")
                else:
                    print(f"\n❌ ISSUE: Logs are not in proper descending order")
                    
                # Test time difference between first and last
                if timestamps[0] and timestamps[-1]:
                    time_diff = timestamps[0] - timestamps[-1]
                    print(f"📊 Time span: {time_diff.total_seconds():.1f} seconds between newest and oldest")
                
            else:
                print("⚠️ No logs found - waiting for logs to generate...")
                
        else:
            print(f"❌ API failed: {logs_response.status_code}")
            
        # Test real-time updates by checking multiple times
        print("\n🔄 Testing real-time updates...")
        initial_count = 0
        for i in range(3):
            response = requests.get("http://127.0.0.1:8000/api/logs/?limit=50")
            if response.status_code == 200:
                logs = response.json()
                current_count = len(logs)
                if i == 0:
                    initial_count = current_count
                    print(f"📊 Initial log count: {current_count}")
                else:
                    if current_count > initial_count:
                        print(f"✅ New logs detected: {current_count} (was {initial_count})")
                    else:
                        print(f"📊 Current log count: {current_count}")
            time.sleep(3)  # Wait 3 seconds
            
    except Exception as e:
        print(f"❌ Error testing logs: {e}")

def test_log_timestamps():
    """Test that log timestamps are current and properly formatted"""
    try:
        print("\n🕐 Testing log timestamps...")
        
        response = requests.get("http://127.0.0.1:8000/api/logs/?limit=5")
        if response.status_code == 200:
            logs = response.json()
            
            current_time = datetime.now()
            print(f"📋 Current time: {current_time.strftime('%H:%M:%S')}")
            
            for i, log in enumerate(logs[:3]):
                timestamp = log.get('timestamp', 'N/A')
                try:
                    log_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_diff = (current_time - log_time).total_seconds()
                    
                    print(f"  Log {i+1}: {log_time.strftime('%H:%M:%S')} ({time_diff:.1f}s ago)")
                    
                    if time_diff < 300:  # Less than 5 minutes
                        print(f"    ✅ Fresh log")
                    else:
                        print(f"    ⚠️ Old log: {time_diff/60:.1f} minutes ago")
                        
                except Exception as e:
                    print(f"  Log {i+1}: Invalid timestamp format - {timestamp}")
                    
    except Exception as e:
        print(f"❌ Error testing timestamps: {e}")

if __name__ == "__main__":
    test_logs_frontend_ordering()
    test_log_timestamps()
