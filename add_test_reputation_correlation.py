import json
import os
from datetime import datetime, timedelta
import random

def add_test_reputation_data():
    """Add test reputation data"""
    
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    
    # Load existing reputation data
    reputation_file = "data/reputation.json"
    reputation_data = []
    
    if os.path.exists(reputation_file):
        try:
            with open(reputation_file, 'r', encoding='utf-8') as f:
                reputation_data = json.load(f)
        except:
            reputation_data = []
    
    # Create test reputation entries
    test_reputations = [
        {
            "_id": "rep_1",
            "entity": "192.168.1.100",
            "entity_type": "ip",
            "aggregated_score": 85.2,
            "risk_level": "malicious",
            "classification": {
                "category": "malware",
                "confidence": 90
            },
            "metrics": {
                "alert_count": 15,
                "false_positive_count": 2,
                "true_positive_count": 13
            },
            "created_at": (datetime.utcnow() - timedelta(days=2)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["malware", "high_risk", "c2_server"]
        },
        {
            "_id": "rep_2",
            "entity": "suspicious-domain.com",
            "entity_type": "domain",
            "aggregated_score": 65.8,
            "risk_level": "suspicious",
            "classification": {
                "category": "phishing",
                "confidence": 75
            },
            "metrics": {
                "alert_count": 8,
                "false_positive_count": 1,
                "true_positive_count": 7
            },
            "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["phishing", "suspicious", "credential_theft"]
        },
        {
            "_id": "rep_3",
            "entity": "10.0.0.50",
            "entity_type": "ip",
            "aggregated_score": 25.3,
            "risk_level": "benign",
            "classification": {
                "category": "trusted",
                "confidence": 85
            },
            "metrics": {
                "alert_count": 2,
                "false_positive_count": 2,
                "true_positive_count": 0
            },
            "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["trusted", "internal", "corporate"]
        },
        {
            "_id": "rep_4",
            "entity": "attacker-tool.exe",
            "entity_type": "hash",
            "aggregated_score": 92.1,
            "risk_level": "malicious",
            "classification": {
                "category": "malware",
                "confidence": 95
            },
            "metrics": {
                "alert_count": 25,
                "false_positive_count": 0,
                "true_positive_count": 25
            },
            "created_at": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["malware", "trojan", "backdoor"]
        },
        {
            "_id": "rep_5",
            "entity": "admin@company.com",
            "entity_type": "email",
            "aggregated_score": 15.7,
            "risk_level": "benign",
            "classification": {
                "category": "trusted",
                "confidence": 90
            },
            "metrics": {
                "alert_count": 1,
                "false_positive_count": 1,
                "true_positive_count": 0
            },
            "created_at": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["trusted", "admin", "internal"]
        },
        {
            "_id": "rep_6",
            "entity": "203.0.113.1",
            "entity_type": "ip",
            "aggregated_score": 78.9,
            "risk_level": "suspicious",
            "classification": {
                "category": "scanner",
                "confidence": 80
            },
            "metrics": {
                "alert_count": 12,
                "false_positive_count": 3,
                "true_positive_count": 9
            },
            "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "last_checked": datetime.utcnow().isoformat(),
            "tags": ["scanner", "reconnaissance", "port_scan"]
        }
    ]
    
    # Add test reputation entries
    reputation_data.extend(test_reputations)
    
    # Save to file
    with open(reputation_file, 'w', encoding='utf-8') as f:
        json.dump(reputation_data, f, indent=2, default=str)
    
    print(f"Added {len(test_reputations)} test reputation entries")
    print(f"Total reputation entries: {len(reputation_data)}")

def add_test_correlation_data():
    """Add test correlation data"""
    
    # Create data directory if not exists
    os.makedirs("data", exist_ok=True)
    
    # Load existing correlation data
    correlation_file = "data/correlation_groups.json"
    correlation_data = []
    
    if os.path.exists(correlation_file):
        try:
            with open(correlation_file, 'r', encoding='utf-8') as f:
                correlation_data = json.load(f)
        except:
            correlation_data = []
    
    # Create test correlation groups
    test_correlations = [
        {
            "_id": "corr_001",
            "name": "Entity Based Correlation - IP 192.168.1.100",
            "description": "5 alerts correlated by shared malicious IP entity",
            "correlation_type": "entity_based",
            "correlation_score": 85.5,
            "confidence": 90,
            "status": "active",
            "alert_ids": ["alert_1", "alert_2", "alert_3", "alert_4", "alert_5"],
            "entities": [
                {"type": "ip", "value": "192.168.1.100", "risk_level": "malicious"}
            ],
            "metrics": {
                "alert_count": 5,
                "unique_entities": 3,
                "severity_score": 7.2,
                "time_span_hours": 2
            },
            "created_at": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "High priority correlation - immediate investigation required"
        },
        {
            "_id": "corr_002",
            "name": "Temporal Correlation - Brute Force Pattern",
            "description": "3 alerts within 30 minutes showing brute force attack pattern",
            "correlation_type": "temporal",
            "correlation_score": 72.3,
            "confidence": 75,
            "status": "active",
            "alert_ids": ["alert_6", "alert_7", "alert_8"],
            "entities": [
                {"type": "ip", "value": "10.0.0.50", "risk_level": "suspicious"},
                {"type": "domain", "value": "attacker.com", "risk_level": "malicious"}
            ],
            "metrics": {
                "alert_count": 3,
                "unique_entities": 2,
                "severity_score": 6.8,
                "time_span_hours": 0.5
            },
            "created_at": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Temporal pattern detected - possible coordinated attack"
        },
        {
            "_id": "corr_003",
            "name": "Geographic Correlation - Unknown Region",
            "description": "4 alerts from unusual geographic location pattern",
            "correlation_type": "geographic",
            "correlation_score": 68.9,
            "confidence": 70,
            "status": "investigating",
            "alert_ids": ["alert_9", "alert_10", "alert_11", "alert_12"],
            "entities": [
                {"type": "country", "value": "XX", "risk_level": "unknown"}
            ],
            "metrics": {
                "alert_count": 4,
                "unique_entities": 1,
                "severity_score": 5.5,
                "time_span_hours": 6
            },
            "created_at": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Unusual geographic pattern - requires investigation"
        },
        {
            "_id": "corr_004",
            "name": "Malware Family Correlation",
            "description": "6 alerts related to same malware family",
            "correlation_type": "pattern_based",
            "correlation_score": 91.2,
            "confidence": 95,
            "status": "active",
            "alert_ids": ["alert_13", "alert_14", "alert_15", "alert_16", "alert_17", "alert_18"],
            "entities": [
                {"type": "hash", "value": "a1b2c3d4e5f6", "risk_level": "malicious"},
                {"type": "domain", "value": "c2-server.com", "risk_level": "malicious"}
            ],
            "metrics": {
                "alert_count": 6,
                "unique_entities": 4,
                "severity_score": 8.9,
                "time_span_hours": 12
            },
            "created_at": (datetime.utcnow() - timedelta(hours=8)).isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "notes": "Advanced persistent threat detected - high priority"
        }
    ]
    
    # Add test correlation entries
    correlation_data.extend(test_correlations)
    
    # Save to file
    with open(correlation_file, 'w', encoding='utf-8') as f:
        json.dump(correlation_data, f, indent=2, default=str)
    
    print(f"Added {len(test_correlations)} test correlation groups")
    print(f"Total correlation groups: {len(correlation_data)}")

if __name__ == "__main__":
    print("🔧 Adding test reputation and correlation data...")
    
    add_test_reputation_data()
    add_test_correlation_data()
    
    print("\n✅ Test data added successfully!")
    print("\n📊 Summary:")
    print("- 6 reputation entities (IPs, domains, hashes, emails)")
    print("- 4 correlation groups (entity, temporal, geographic, pattern-based)")
    print("- Risk levels: malicious, suspicious, benign")
    print("- Correlation types: entity_based, temporal, geographic, pattern_based")
