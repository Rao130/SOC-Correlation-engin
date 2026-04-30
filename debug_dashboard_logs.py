import requests
import json
from datetime import datetime

def debug_dashboard_logs():
    """Debug what's happening with dashboard logs"""
    try:
        print("🔍 DEBUGGING Dashboard Logs Issue...")
        
        # Check if logs are being generated in backend
        print("\n📊 Backend Log Generation Check:")
        for i in range(3):
            response = requests.get("http://127.0.0.1:8000/api/logs?limit=1")
            if response.status_code == 200:
                logs = response.json()
                if logs:
                    latest_log = logs[0]
                    timestamp = latest_log.get('timestamp', '')
                    message = latest_log.get('message', '')[:50]
                    print(f"  {i+1}. {timestamp} - {message}...")
            import time
            time.sleep(2)
        
        # Check the main dashboard page
        print(f"\n🌐 Testing main dashboard page...")
        dashboard_response = requests.get("http://127.0.0.1:8000/")
        if dashboard_response.status_code == 200:
            print("✅ Dashboard page loads successfully")
            
            # Check if logs.js is included
            content = dashboard_response.text
            if 'logs.js' in content:
                print("✅ logs.js is included in dashboard")
            else:
                print("❌ logs.js is NOT included in dashboard")
                
            if 'logs-tbody' in content:
                print("✅ logs-tbody element exists")
            else:
                print("❌ logs-tbody element NOT found")
                
            if 'logs-section' in content:
                print("✅ logs-section exists")
            else:
                print("❌ logs-section NOT found")
        else:
            print(f"❌ Dashboard page failed: {dashboard_response.status_code}")
        
        # Test direct logs page
        print(f"\n📄 Testing direct test page...")
        test_response = requests.get("http://127.0.0.1:8000/static/test_direct.html")
        if test_response.status_code == 200:
            print("✅ Direct test page available")
            print("🌐 Open http://127.0.0.1:8000/static/test_direct.html in browser")
        else:
            print("❌ Direct test page not available")
        
        # Check WebSocket endpoint
        print(f"\n🔌 WebSocket Connection Test:")
        try:
            import websocket
            import threading
            
            def on_message(ws, message):
                data = json.loads(message)
                print(f"  📨 WebSocket message: {data.type}")
                
            def on_error(ws, error):
                print(f"  ❌ WebSocket error: {error}")
                
            def on_close(ws, close_status_code, close_msg):
                print("  🔌 WebSocket closed")
                
            def on_open(ws):
                print("  ✅ WebSocket connected")
                ws.send(json.dumps({"type": "get_logs"}))
            
            # Test WebSocket connection
            ws = websocket.WebSocketApp(
                f"ws://127.0.0.1:8000/ws/test_client",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run for 3 seconds
            wst = threading.Thread(target=lambda: ws.run_forever())
            wst.daemon = True
            wst.start()
            
            import time
            time.sleep(3)
            ws.close()
            
        except ImportError:
            print("  ⚠️ WebSocket library not available for testing")
        except Exception as e:
            print(f"  ❌ WebSocket test failed: {e}")
        
        # Check console errors by examining logs.js
        print(f"\n🔍 Checking logs.js for potential issues...")
        try:
            with open('static/js/logs.js', 'r') as f:
                content = f.read()
                
            # Check for common issues
            issues = []
            
            if 'console.error' in content:
                error_lines = [line.strip() for line in content.split('\n') if 'console.error' in line]
                issues.append(f"Found {len(error_lines)} console.error statements")
            
            if 'try {' not in content or 'catch' not in content:
                issues.append("Missing try-catch blocks")
            
            if 'getElementById' in content:
                getElementById_count = content.count('getElementById')
                issues.append(f"Found {getElementById_count} getElementById calls")
            
            if issues:
                print("  ⚠️ Potential issues found:")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print("  ✅ No obvious issues in logs.js")
                
        except Exception as e:
            print(f"  ❌ Could not read logs.js: {e}")
            
    except Exception as e:
        print(f"❌ Debug error: {e}")

if __name__ == "__main__":
    debug_dashboard_logs()
