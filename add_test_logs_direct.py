import json
from datetime import datetime, timedelta
import os

def add_test_logs_direct():
    """Add test logs directly to file database"""
    
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    
    # Load existing logs
    logs_file = "data/logs.json"
    logs = []
    
    if os.path.exists(logs_file):
        try:
            with open(logs_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except:
            logs = []
    
    # Create test logs
    test_logs = [
        {
            "id": "log_1",
            "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            "level": "INFO",
            "category": "SYSTEM",
            "message": "System started successfully",
            "module": "main",
            "function": "lifespan",
            "user_id": "admin",
            "ip_address": "127.0.0.1",
            "request_id": "req_001",
            "duration_ms": 150.5
        },
        {
            "id": "log_2",
            "timestamp": (datetime.utcnow() - timedelta(minutes=25)).isoformat(),
            "level": "INFO",
            "category": "DATABASE",
            "message": "Database connection established",
            "module": "database",
            "function": "connect",
            "user_id": "system",
            "ip_address": "127.0.0.1",
            "request_id": "req_002",
            "duration_ms": 89.2
        },
        {
            "id": "log_3",
            "timestamp": (datetime.utcnow() - timedelta(minutes=20)).isoformat(),
            "level": "WARNING",
            "category": "AUTH",
            "message": "Failed login attempt from unknown IP",
            "module": "auth",
            "function": "login",
            "user_id": None,
            "ip_address": "192.168.1.100",
            "request_id": "req_003",
            "error_code": "AUTH_001"
        },
        {
            "id": "log_4",
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "level": "ERROR",
            "category": "API",
            "message": "API request timeout",
            "module": "api",
            "function": "handle_request",
            "user_id": "user123",
            "ip_address": "127.0.0.1",
            "request_id": "req_004",
            "duration_ms": 5000.0,
            "error_code": "API_TIMEOUT"
        },
        {
            "id": "log_5",
            "timestamp": (datetime.utcnow() - timedelta(minutes=10)).isoformat(),
            "level": "INFO",
            "category": "ALERT",
            "message": "New security alert received",
            "module": "alerts",
            "function": "process_alert",
            "user_id": "analyst1",
            "ip_address": "127.0.0.1",
            "request_id": "req_005",
            "duration_ms": 200.3
        },
        {
            "id": "log_6",
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
            "level": "CRITICAL",
            "category": "SECURITY",
            "message": "Potential security breach detected",
            "module": "security",
            "function": "monitor",
            "user_id": "security_team",
            "ip_address": "127.0.0.1",
            "request_id": "req_006",
            "error_code": "SEC_BREACH",
            "tags": ["critical", "investigation"]
        },
        {
            "id": "log_7",
            "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            "level": "INFO",
            "category": "CORRELATION",
            "message": "Alert correlation completed successfully",
            "module": "correlation",
            "function": "analyze",
            "user_id": "system",
            "ip_address": "127.0.0.1",
            "request_id": "req_007",
            "duration_ms": 350.7
        },
        {
            "id": "log_8",
            "timestamp": (datetime.utcnow() - timedelta(minutes=2)).isoformat(),
            "level": "WARNING",
            "category": "PERFORMANCE",
            "message": "High response time detected",
            "module": "performance",
            "function": "monitor",
            "user_id": "monitor",
            "ip_address": "127.0.0.1",
            "request_id": "req_008",
            "duration_ms": 1200.0,
            "tags": ["performance", "monitoring"]
        },
        {
            "id": "log_9",
            "timestamp": (datetime.utcnow() - timedelta(minutes=1)).isoformat(),
            "level": "ERROR",
            "category": "WEBSOCKET",
            "message": "WebSocket connection lost",
            "module": "websocket",
            "function": "handle_disconnect",
            "user_id": "user456",
            "ip_address": "127.0.0.1",
            "request_id": "req_009",
            "error_code": "WS_DISCONNECT"
        },
        {
            "id": "log_10",
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "category": "REPUTATION",
            "message": "Reputation database updated",
            "module": "reputation",
            "function": "update",
            "user_id": "system",
            "ip_address": "127.0.0.1",
            "request_id": "req_010",
            "duration_ms": 95.8
        }
    ]
    
    # Add test logs to existing logs
    logs.extend(test_logs)
    
    # Save to file
    with open(logs_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=2, default=str)
    
    print(f"Added {len(test_logs)} test logs to {logs_file}")
    print(f"Total logs in database: {len(logs)}")

if __name__ == "__main__":
    add_test_logs_direct()
