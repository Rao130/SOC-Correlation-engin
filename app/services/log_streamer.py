"""
Real-time Log Streaming and Analysis Service
Generates and processes security logs in real-time
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import re
from app.core.logging import logger
from app.core.database import get_db

class LogStreamer:
    """Real-time log generation and analysis service"""
    
    def __init__(self):
        self.active = False
        self.generated_logs = []
        self.log_patterns = self._initialize_log_patterns()
        self.log_sources = [
            "firewall", "ids", "web_server", "auth_server", 
            "dns_server", "proxy", "endpoint", "mail_server"
        ]
        self.severity_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        self.ip_addresses = self._generate_ip_addresses()
        
    def _initialize_log_patterns(self) -> Dict[str, List[str]]:
        """Initialize realistic log message patterns"""
        return {
            "firewall": [
                "ACCEPT {src_ip}:{src_port} -> {dst_ip}:{dst_port} {protocol}",
                "DENY {src_ip}:{src_port} -> {dst_ip}:{dst_port} {protocol} (Rule: {rule_id})",
                "BLOCK {src_ip} attempted connection to {dst_ip}:{dst_port}",
                "ALLOW established connection {src_ip} -> {dst_ip}"
            ],
            "ids": [
                "ALERT: {attack_type} detected from {src_ip} targeting {dst_ip}",
                "SUSPICIOUS: Port scan detected from {src_ip} on ports {ports}",
                "WARNING: Brute force attempt from {src_ip} to {dst_ip}",
                "CRITICAL: Malware communication detected {src_ip} -> {dst_ip}"
            ],
            "web_server": [
                "{method} {url} {status_code} {response_size} bytes from {src_ip}",
                "ERROR: {error_code} on {url} from {src_ip}",
                "WARNING: Suspicious URL pattern: {url} from {src_ip}",
                "INFO: User {user} accessed {url} from {src_ip}"
            ],
            "auth_server": [
                "LOGIN SUCCESS: User {user} from {src_ip}",
                "LOGIN FAILED: User {user} from {src_ip} (Reason: {reason})",
                "PASSWORD CHANGE: User {user} from {src_ip}",
                "ACCOUNT LOCKED: User {user} after {attempts} failed attempts"
            ],
            "dns_server": [
                "QUERY: {domain} from {src_ip} -> {result_ip}",
                "SUSPICIOUS: DNS query for malicious domain {domain} from {src_ip}",
                "BLOCKED: DNS query for {domain} from {src_ip}",
                "INFO: DNS response {domain} -> {result_ip} to {src_ip}"
            ],
            "proxy": [
                "CONNECT {user}@{src_ip} -> {dst_ip}:{dst_port}",
                "DENIED: {user} attempted to access {url} from {src_ip}",
                "WARNING: Large download {size}MB by {user} from {url}",
                "INFO: Cache HIT for {url} requested by {user}"
            ],
            "endpoint": [
                "PROCESS_START: {process} PID {pid} by {user}",
                "FILE_MODIFIED: {file_path} by {process}",
                "ALERT: Suspicious registry change by {process}",
                "WARNING: Unusual network activity from {process} to {dst_ip}"
            ],
            "mail_server": [
                "EMAIL_SENT: From {sender} to {recipient} via {src_ip}",
                "SPAM_DETECTED: From {sender} to {recipient} (Score: {score})",
                "PHISHING_ATTEMPT: {subject} from {sender} to {recipient}",
                "BOUNCE: Email to {recipient} failed ({reason})"
            ]
        }
    
    def _generate_ip_addresses(self) -> List[str]:
        """Generate realistic IP addresses for logs"""
        ips = []
        
        # Internal network ranges
        for i in range(1, 255):
            ips.append(f"192.168.1.{i}")
        for i in range(1, 255):
            ips.append(f"10.0.0.{i}")
            
        # External IPs
        external_ranges = [
            "203.0.113", "198.51.100", "192.0.2", "172.16.0",
            "172.31.255", "169.254.0", "8.8.8", "1.1.1"
        ]
        
        for base in external_ranges:
            for i in range(1, 20):
                ips.append(f"{base}.{i}")
                
        return ips
    
    def _generate_log_entry(self) -> Dict[str, Any]:
        """Generate a single realistic log entry"""
        source = random.choice(self.log_sources)
        severity = random.choices(
            self.severity_levels,
            weights=[10, 40, 30, 15, 5]  # Weight distribution
        )[0]
        
        # Get pattern for this source
        patterns = self.log_patterns.get(source, ["Generic log message"])
        pattern = random.choice(patterns)
        
        # Generate log message with realistic data
        message = self._fill_log_pattern(pattern, source)
        
        # Create log entry with all required fields
        log_entry = {
            "id": f"log_{random.randint(100000, 999999)}",
            "timestamp": datetime.now().isoformat(),
            "level": severity,
            "category": self._get_log_category(source, severity),
            "message": message,
            "module": source,
            "function": self._get_function_name(source),
            "user_id": "system",
            "ip_address": random.choice(self.ip_addresses),
            "host": f"{source}-server-{random.randint(1, 10)}",
            "process": self._get_process_name(source),
            "pid": random.randint(1000, 9999),
            "raw_log": f"{datetime.utcnow().strftime('%b %d %H:%M:%S')} {source} [{severity}] {message}"
        }
        
        # Add analysis if it's a security-relevant log
        if severity in ["WARNING", "ERROR", "CRITICAL"] or self._is_security_relevant(message):
            log_entry["analysis"] = self._analyze_log_message(message, source)
            log_entry["security_relevant"] = True
        
        return log_entry
    
    def _fill_log_pattern(self, pattern: str, source: str) -> str:
        """Fill log pattern with realistic data"""
        replacements = {
            "{src_ip}": random.choice(self.ip_addresses),
            "{dst_ip}": random.choice(self.ip_addresses),
            "{src_port}": str(random.randint(1024, 65535)),
            "{dst_port}": str(random.choice([22, 80, 443, 3389, 5900, 1433, 3306, 25, 53, 110])),
            "{protocol}": random.choice(["TCP", "UDP", "ICMP"]),
            "{rule_id}": f"RULE-{random.randint(1000, 9999)}",
            "{attack_type}": random.choice(["SQL Injection", "XSS", "Command Injection", "Directory Traversal", "Buffer Overflow"]),
            "{ports}": ",".join(map(str, random.sample(range(1, 65535), random.randint(3, 8)))),
            "{method}": random.choice(["GET", "POST", "PUT", "DELETE", "HEAD"]),
            "{url}": self._generate_url(),
            "{status_code}": str(random.choice([200, 201, 301, 302, 400, 401, 403, 404, 500, 502])),
            "{response_size}": str(random.randint(100, 100000)),
            "{error_code}": random.choice(["404 Not Found", "500 Internal Server Error", "403 Forbidden", "401 Unauthorized"]),
            "{user}": self._generate_username(),
            "{reason}": random.choice(["Invalid credentials", "Account locked", "IP blocked", "Rate limit exceeded"]),
            "{attempts}": str(random.randint(3, 10)),
            "{domain}": self._generate_domain(),
            "{result_ip}": random.choice(self.ip_addresses),
            "{size}": str(random.randint(1, 1000)),
            "{process}": self._get_process_name(source),
            "{pid}": str(random.randint(1000, 9999)),
            "{file_path}": self._generate_file_path(),
            "{sender}": f"user{random.randint(1, 100)}@{self._generate_domain()}",
            "{recipient}": f"user{random.randint(1, 100)}@{self._generate_domain()}",
            "{score}": str(random.randint(70, 99)),
            "{subject}": random.choice(["Urgent: Account Verification", "Your Package Has Arrived", "Security Alert", "Invoice Attached"])
        }
        
        message = pattern
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        
        return message
    
    def _generate_url(self) -> str:
        """Generate realistic URL"""
        paths = [
            "/api/v1/users", "/login", "/admin/dashboard", "/search", "/download/file",
            "/upload", "/config", "/backup", "/logs", "/database/query"
        ]
        return random.choice(paths) + f"?id={random.randint(1, 1000)}"
    
    def _generate_username(self) -> str:
        """Generate realistic username"""
        prefixes = ["admin", "user", "guest", "service", "app", "web", "db", "backup"]
        numbers = random.randint(1, 999)
        return f"{random.choice(prefixes)}{numbers}"
    
    def _generate_domain(self) -> str:
        """Generate realistic domain name"""
        domains = [
            "example.com", "test.org", "demo.net", "company.co", "service.io",
            "malicious-site.xyz", "suspicious-domain.biz", "phishing-attempt.info"
        ]
        return random.choice(domains)
    
    def _get_log_category(self, source: str, severity: str) -> str:
        """Get log category based on source and severity"""
        from app.models.log import LogCategory
        
        category_mapping = {
            "firewall": LogCategory.SECURITY,
            "ids": LogCategory.SECURITY,
            "web_server": LogCategory.API,
            "auth_server": LogCategory.AUTH,
            "dns_server": LogCategory.SYSTEM,
            "proxy": LogCategory.API,
            "endpoint": LogCategory.SECURITY,
            "mail_server": LogCategory.SYSTEM
        }
        
        # Override for high severity logs
        if severity in ["ERROR", "CRITICAL"]:
            return LogCategory.SYSTEM
        
        return category_mapping.get(source, LogCategory.SYSTEM)
    
    def _get_function_name(self, source: str) -> str:
        """Get realistic function name for log source"""
        function_mapping = {
            "firewall": "process_packet",
            "ids": "analyze_signature",
            "web_server": "handle_request",
            "auth_server": "authenticate_user",
            "dns_server": "resolve_query",
            "proxy": "forward_request",
            "endpoint": "monitor_process",
            "mail_server": "process_email"
        }
        
        return function_mapping.get(source, "log_event")
    
    def _get_process_name(self, source: str) -> str:
        """Get realistic process name for log source"""
        process_map = {
            "firewall": "iptables",
            "ids": "snort",
            "web_server": "apache2",
            "auth_server": "sshd",
            "dns_server": "named",
            "proxy": "squid",
            "endpoint": "explorer.exe",
            "mail_server": "postfix"
        }
        return process_map.get(source, "system")
    
    def _generate_file_path(self) -> str:
        """Generate realistic file path"""
        paths = [
            "/etc/passwd", "/var/log/auth.log", "/home/user/documents/secret.txt",
            "C:\\Windows\\System32\\config\\SAM", "/tmp/malware.exe",
            "/var/www/html/index.php", "/home/user/.ssh/authorized_keys"
        ]
        return random.choice(paths)
    
    def _is_security_relevant(self, message: str) -> bool:
        """Check if log message is security-relevant"""
        security_keywords = [
            "attack", "malware", "intrusion", "unauthorized", "blocked",
            "denied", "failed", "suspicious", "alert", "critical", "breach",
            "exploit", "vulnerability", "phishing", "spam", "injection"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in security_keywords)
    
    def _analyze_log_message(self, message: str, source: str) -> Dict[str, Any]:
        """Analyze log message for security insights"""
        analysis = {
            "threat_level": "low",
            "indicators": [],
            "mitre_tactics": [],
            "recommended_actions": []
        }
        
        # Extract IP addresses
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        ips = re.findall(ip_pattern, message)
        if ips:
            analysis["indicators"].extend([{"type": "ip_address", "value": ip} for ip in ips])
        
        # Determine threat level based on keywords
        if any(word in message.lower() for word in ["critical", "malware", "breach", "exploit"]):
            analysis["threat_level"] = "critical"
            analysis["mitre_tactics"] = ["Execution", "Persistence"]
            analysis["recommended_actions"] = ["Isolate affected system", "Collect forensic evidence"]
        elif any(word in message.lower() for word in ["attack", "intrusion", "unauthorized"]):
            analysis["threat_level"] = "high"
            analysis["mitre_tactics"] = ["Initial Access", "Discovery"]
            analysis["recommended_actions"] = ["Investigate source", "Check for lateral movement"]
        elif any(word in message.lower() for word in ["suspicious", "blocked", "denied"]):
            analysis["threat_level"] = "medium"
            analysis["mitre_tactics"] = ["Reconnaissance"]
            analysis["recommended_actions"] = ["Monitor for follow-up activity"]
        
        # Source-specific analysis
        if source == "firewall" and "DENY" in message:
            analysis["threat_level"] = "medium"
            analysis["indicators"].append({"type": "blocked_connection", "value": True})
        elif source == "ids" and "ALERT" in message:
            analysis["threat_level"] = "high"
            analysis["indicators"].append({"type": "ids_alert", "value": True})
        
        return analysis
    
    def _is_recent_log(self, timestamp_str: str) -> bool:
        """Check if log is recent (within last minute)"""
        try:
            if not timestamp_str:
                return False
            
            # Handle different timestamp formats
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str.replace('Z', '+00:00')
            
            log_time = datetime.fromisoformat(timestamp_str)
            return log_time > datetime.utcnow() - timedelta(minutes=1)
        except (ValueError, TypeError, AttributeError):
            return False
    
    async def generate_log_burst(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate a burst of log entries"""
        logs = []
        for _ in range(count):
            log_entry = self._generate_log_entry()
            logs.append(log_entry)
            self.generated_logs.append(log_entry)
        
        # Keep only last 1000 logs in memory
        if len(self.generated_logs) > 1000:
            self.generated_logs = self.generated_logs[-1000:]
        
        # Try to save to database
        try:
            from app.core.database import db_manager
            from bson import ObjectId
            db = db_manager.get_database()
            logs_collection = db.logs
            
            # Convert log entries to be JSON serializable
            serializable_logs = []
            for log in logs:
                log_copy = log.copy()
                # Convert any non-serializable objects
                if '_id' in log_copy:
                    log_copy['_id'] = str(log_copy['_id'])
                serializable_logs.append(log_copy)
            
            await logs_collection.insert_many(serializable_logs)
        except Exception as e:
            logger.warning(f"Failed to save logs to database: {e}")
        
        logger.info(f"Generated {count} log entries")
        return logs
    
    async def start_continuous_generation(self):
        """Start continuous log generation"""
        self.active = True
        logger.info("Starting continuous log generation...")
        
        while self.active:
            try:
                # Generate 3-8 logs every 2-6 seconds for more frequent updates
                log_count = random.randint(3, 8)
                await self.generate_log_burst(log_count)
                
                # Reduced delay for more frequent real-time updates
                delay = random.randint(2, 6)
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in continuous log generation: {e}")
                await asyncio.sleep(5)
    
    def stop_generation(self):
        """Stop continuous log generation"""
        self.active = False
        logger.info("Stopping log generation...")
    
    def get_recent_logs(self, limit: int = 100, severity: Optional[str] = None, 
                       source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent log entries with filtering"""
        # Sort by timestamp (newest first) - proper datetime parsing
        def get_timestamp(log):
            ts = log.get('timestamp', '')
            try:
                # Parse ISO format timestamp
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except:
                # Fallback to string comparison
                return ts
        
        logs = sorted(self.generated_logs, key=get_timestamp, reverse=True)
        
        # Apply filters
        if severity:
            logs = [log for log in logs if log.get('level') == severity]  # Changed from severity to level
        if source:
            logs = [log for log in logs if log.get('module') == source]  # Changed from source to module
        
        # Ensure logs are JSON serializable
        serializable_logs = []
        for log in logs[:limit]:
            log_copy = log.copy()
            # Convert any ObjectId to string
            if '_id' in log_copy:
                log_copy['_id'] = str(log_copy['_id'])
            serializable_logs.append(log_copy)
        
        return serializable_logs
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about generated logs"""
        if not self.generated_logs:
            return {"total": 0, "by_severity": {}, "by_source": {}}
        
        severity_counts = {}
        source_counts = {}
        security_relevant_count = 0
        
        for log in self.generated_logs:
            severity = log.get('severity', 'unknown')
            source = log.get('source', 'unknown')
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            
            if log.get('security_relevant', False):
                security_relevant_count += 1
        
        return {
            "total": len(self.generated_logs),
            "by_severity": severity_counts,
            "by_source": source_counts,
            "security_relevant": security_relevant_count,
            "last_minute": len([log for log in self.generated_logs 
                              if self._is_recent_log(log.get('timestamp', ''))])
        }

# Global instance
log_streamer = LogStreamer()
