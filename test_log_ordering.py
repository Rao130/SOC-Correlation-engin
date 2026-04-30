import requests
import json
from datetime import datetime

def test_log_ordering():
    try:
        print("🔍 Testing log ordering...")
        
        # Test logs API
        print("\n📝 Testing logs API ordering...")
        logs_response = requests.get("http://127.0.0.1:8000/api/logs/?limit=10")
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"✅ Logs API returned {len(logs)} logs")
            
            if logs:
                print(f"\n📋 Log timestamps (should be newest first):")
                for i, log in enumerate(logs[:5]):
                    timestamp = log.get('timestamp', 'N/A')
                    message = log.get('message', 'N/A')[:50] + "..."
                    level = log.get('level', 'N/A')
                    
                    # Parse timestamp to check order
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
                        timestamps.append(ts)
                
                # Check if first few are in descending order
                is_descending = True
                for i in range(min(4, len(timestamps)-1)):
                    if isinstance(timestamps[i], datetime) and isinstance(timestamps[i+1], datetime):
                        if timestamps[i] < timestamps[i+1]:
                            is_descending = False
                            break
                
                if is_descending:
                    print(f"\n✅ PERFECT: Logs are in descending order (newest first)")
                else:
                    print(f"\n❌ ISSUE: Logs are not in proper descending order")
            else:
                print("✅ No logs found - system is fresh")
        else:
            print(f"❌ Logs API failed: {logs_response.status_code}")
        
        # Test with more logs to see ordering
        print("\n📊 Testing with more logs...")
        more_logs_response = requests.get("http://127.0.0.1:8000/api/logs/?limit=20")
        if more_logs_response.status_code == 200:
            more_logs = more_logs_response.json()
            print(f"✅ Got {len(more_logs)} logs")
            
            # Show first and last timestamps
            if more_logs:
                first_ts = more_logs[0].get('timestamp', 'N/A')
                last_ts = more_logs[-1].get('timestamp', 'N/A')
                
                try:
                    first_time = datetime.fromisoformat(first_ts.replace('Z', '+00:00'))
                    last_time = datetime.fromisoformat(last_ts.replace('Z', '+00:00'))
                    
                    print(f"📋 First log (newest): {first_time.strftime('%H:%M:%S')}")
                    print(f"📋 Last log (oldest): {last_time.strftime('%H:%M:%S')}")
                    
                    if first_time > last_time:
                        print("✅ PERFECT: Newest logs are showing first!")
                    else:
                        print("❌ ISSUE: Ordering is not correct")
                        
                except:
                    print(f"⚠️ Could not parse timestamps: {first_ts}, {last_ts}")
        
    except Exception as e:
        print(f"❌ Error testing log ordering: {e}")

if __name__ == "__main__":
    test_log_ordering()
