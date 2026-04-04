import asyncio
import aiohttp
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict

class AttackSimulator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.attack_types = [
            "brute_force_login",
            "sql_injection", 
            "ddos_attack",
            "port_scan",
            "malware_detection",
            "suspicious_ip",
            "data_exfiltration",
            "privilege_escalation"
        ]
        
    async def start_session(self):
        """Start HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def create_alert(self, attack_type: str, severity: str = "medium"):
        """Create a security alert"""
        
        # Map severity strings to API values
        severity_map = {
            "low": "low",
            "medium": "medium", 
            "high": "high",
            "critical": "critical"
        }
        
        # Map attack types to categories
        category_map = {
            "brute_force_login": "intrusion",
            "sql_injection": "intrusion",
            "ddos_attack": "ddos",
            "port_scan": "intrusion",
            "malware_detection": "malware",
            "suspicious_ip": "intrusion",
            "data_exfiltration": "data_breach",
            "privilege_escalation": "intrusion"
        }
        
        alert_data = {
            "title": f"{attack_type.replace('_', ' ').title()} Attack Detected",
            "description": self._get_attack_description(attack_type),
            "severity": severity_map.get(severity, "medium"),
            "source": "Attack Simulator",
            "category": category_map.get(attack_type, "other"),
            "confidence": random.randint(70, 100),
            "entities": [
                {
                    "type": "ip",
                    "value": self._generate_ip(),
                    "reputation": {"score": random.uniform(0.1, 0.9)}
                }
            ]
        }
        
        try:
            url = f"{self.base_url}/api/alerts/"
            async with self.session.post(url, json=alert_data) as response:
                if response.status == 200:
                    print(f"✅ Alert created: {alert_data['title']}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to create alert: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Error creating alert: {e}")
            return False
    
    def _get_attack_description(self, attack_type: str) -> str:
        """Get attack description"""
        descriptions = {
            "brute_force_login": "Multiple failed login attempts detected from single IP address",
            "sql_injection": "SQL injection patterns detected in web requests",
            "ddos_attack": "High volume of requests detected from multiple sources",
            "port_scan": "Network port scanning activity detected",
            "malware_detection": "Malicious file or behavior detected",
            "suspicious_ip": "Connection from known malicious IP address",
            "data_exfiltration": "Unusual data transfer patterns detected",
            "privilege_escalation": "Attempt to gain elevated privileges detected"
        }
        return descriptions.get(attack_type, "Unknown attack detected")
    
    def _generate_ip(self) -> str:
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def _get_target(self) -> str:
        """Get random target"""
        targets = [
            "Web Server",
            "Database Server", 
            "API Endpoint",
            "Authentication Service",
            "File Server",
            "Admin Panel"
        ]
        return random.choice(targets)
    
    def _get_attack_details(self, attack_type: str) -> Dict:
        """Get detailed attack information"""
        return {
            "protocol": random.choice(["HTTP", "HTTPS", "TCP", "UDP"]),
            "port": random.randint(80, 8443),
            "payload_size": random.randint(100, 10000),
            "request_count": random.randint(10, 1000),
            "duration_seconds": random.randint(5, 300),
            "user_agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "curl/7.68.0",
                "python-requests/2.25.1",
                "Custom Attack Tool"
            ]),
            "attack_start_time": datetime.utcnow().isoformat(),
            "attack_signature": f"SIG_{random.randint(1000, 9999)}"
        }
    
    def _get_mitigation_steps(self, attack_type: str) -> List[str]:
        """Get mitigation steps"""
        steps = {
            "brute_force_login": [
                "Block source IP address",
                "Enable rate limiting",
                "Implement 2FA",
                "Review failed login logs"
            ],
            "sql_injection": [
                "Block malicious requests",
                "Update web application firewall",
                "Review database logs",
                "Patch vulnerable code"
            ],
            "ddos_attack": [
                "Activate DDoS protection",
                "Block attacking IPs",
                "Increase rate limits",
                "Notify ISP"
            ],
            "port_scan": [
                "Block scanning IP",
                "Close unnecessary ports",
                "Enable intrusion detection",
                "Review firewall rules"
            ],
            "malware_detection": [
                "Isolate affected system",
                "Run antivirus scan",
                "Update signatures",
                "Review system logs"
            ],
            "suspicious_ip": [
                "Block IP address",
                "Review connection logs",
                "Update threat intelligence",
                "Monitor for further activity"
            ],
            "data_exfiltration": [
                "Block data transfers",
                "Review access logs",
                "Identify compromised accounts",
                "Notify security team"
            ],
            "privilege_escalation": [
                "Block user account",
                "Review permission changes",
                "Audit system logs",
                "Reset credentials"
            ]
        }
        return steps.get(attack_type, ["Contact security team"])
    
    async def simulate_attack_burst(self, count: int = 5):
        """Simulate burst of attacks"""
        print(f"🚀 Starting attack simulation with {count} alerts...")
        
        for i in range(count):
            attack_type = random.choice(self.attack_types)
            severity = random.choice(["low", "medium", "high", "critical"])
            
            success = await self.create_alert(attack_type, severity)
            if success:
                print(f"  📡 Alert {i+1}/{count}: {attack_type} ({severity})")
            
            # Small delay between attacks
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        print(f"✅ Attack simulation completed! Check your dashboard.")
    
    async def simulate_continuous_attack(self, duration_minutes: int = 5):
        """Simulate continuous attacks over time"""
        print(f"🔄 Starting continuous attack simulation for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        alert_count = 0
        
        while time.time() < end_time:
            attack_type = random.choice(self.attack_types)
            severity = random.choice(["low", "medium", "high", "critical"])
            
            success = await self.create_alert(attack_type, severity)
            if success:
                alert_count += 1
                print(f"  ⚠️  Alert {alert_count}: {attack_type} ({severity})")
            
            # Random delay between 10-30 seconds
            await asyncio.sleep(random.uniform(10, 30))
        
        print(f"✅ Continuous simulation completed! Generated {alert_count} alerts.")
    
    async def simulate_specific_attack(self, attack_type: str, count: int = 3):
        """Simulate specific type of attack"""
        print(f"🎯 Simulating {count} {attack_type} attacks...")
        
        for i in range(count):
            severity = random.choice(["medium", "high", "critical"])
            success = await self.create_alert(attack_type, severity)
            
            if success:
                print(f"  💥 {attack_type.title()} attack {i+1}/{count} sent!")
            
            await asyncio.sleep(1.0)
        
        print(f"✅ {attack_type} simulation completed!")

async def main():
    """Main function to run attack simulator"""
    print("🛡️  SOC Correlation Engine - Attack Simulator")
    print("=" * 50)
    
    simulator = AttackSimulator()
    await simulator.start_session()
    
    try:
        print("\nChoose attack simulation:")
        print("1. Quick burst (5 random attacks)")
        print("2. Continuous attack (5 minutes)")
        print("3. Brute force attack simulation")
        print("4. DDoS attack simulation")
        print("5. SQL injection simulation")
        print("6. Custom attack burst")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            await simulator.simulate_attack_burst(5)
        elif choice == "2":
            await simulator.simulate_continuous_attack(5)
        elif choice == "3":
            await simulator.simulate_specific_attack("brute_force_login", 5)
        elif choice == "4":
            await simulator.simulate_specific_attack("ddos_attack", 8)
        elif choice == "5":
            await simulator.simulate_specific_attack("sql_injection", 4)
        elif choice == "6":
            count = int(input("Enter number of attacks: "))
            await simulator.simulate_attack_burst(count)
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n🛑 Attack simulation stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await simulator.close_session()
    
    print("\n🎯 Check your SOC dashboard at http://localhost:8000 to see the alerts!")

if __name__ == "__main__":
    asyncio.run(main())
