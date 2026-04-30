#!/usr/bin/env python3
"""
Firewall Integration Deployment Script
Deploy SOC Correlation Engine with firewall integration
"""

import os
import sys
import subprocess
import yaml
import json
import time
from pathlib import Path

class FirewallDeployment:
    def __init__(self):
        self.config_file = "config/firewall_deployment.yml"
        self.docker_compose_file = "docker-compose.firewall.yml"
        self.integration_dir = "app/integrations"
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking firewall integration prerequisites...")
        
        prerequisites = {
            "docker": self.check_command("docker --version"),
            "docker-compose": self.check_command("docker-compose --version"),
            "curl": self.check_command("curl --version"),
            "python3": self.check_command("python3 --version"),
            "ssh": self.check_command("ssh -V"),
            "openssl": self.check_command("openssl version")
        }
        
        all_good = True
        for tool, available in prerequisites.items():
            if available:
                print(f"✅ {tool}: Available")
            else:
                print(f"❌ {tool}: Missing - Please install {tool}")
                all_good = False
        
        if not all_good:
            print("\n❌ Prerequisites check failed. Please install missing tools.")
            sys.exit(1)
        
        print("✅ All prerequisites satisfied!")
    
    def check_command(self, command):
        """Check if command is available"""
        try:
            subprocess.run(command, shell=True, check=True, 
                         capture_output=True, timeout=5)
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False
    
    def create_firewall_configs(self):
        """Create firewall integration configurations"""
        print("🔥 Creating firewall integration configurations...")
        
        # Palo Alto Networks Configuration
        palo_alto_config = {
            'enabled': True,
            'firewall_type': 'palo_alto',
            'connection': {
                'host': os.getenv('PALO_ALTO_HOST', '192.168.1.1'),
                'api_key': os.getenv('PALO_ALTO_API_KEY', ''),
                'port': 443,
                'verify_ssl': False
            },
            'polling': {
                'interval': 30,  # seconds
                'log_types': ['threat', 'traffic', 'url_filtering'],
                'max_events': 1000
            },
            'mapping': {
                'severity_mapping': {
                    'critical': 'critical',
                    'high': 'high', 
                    'medium': 'medium',
                    'low': 'low',
                    'informational': 'info'
                },
                'category_mapping': {
                    'virus': 'malware',
                    'spyware': 'malware',
                    'trojan': 'malware',
                    'phishing': 'phishing',
                    'brute-force': 'brute_force'
                }
            }
        }
        
        # Cisco ASA Configuration
        cisco_asa_config = {
            'enabled': False,
            'firewall_type': 'cisco_asa',
            'connection': {
                'host': os.getenv('CISCO_ASA_HOST', '192.168.1.254'),
                'username': os.getenv('CISCO_ASA_USER', 'admin'),
                'password': os.getenv('CISCO_ASA_PASSWORD', ''),
                'port': 22
            },
            'polling': {
                'interval': 60,  # seconds
                'commands': [
                    'show logging | include %ASA-',
                    'show access-list',
                    'show conn',
                    'show threat-detection'
                ]
            }
        }
        
        # Fortinet Configuration
        fortinet_config = {
            'enabled': False,
            'firewall_type': 'fortinet',
            'connection': {
                'host': os.getenv('FORTINET_HOST', '192.168.1.253'),
                'api_key': os.getenv('FORTINET_API_KEY', ''),
                'port': 443
            },
            'polling': {
                'interval': 45,  # seconds
                'log_types': ['traffic', 'virus', 'attack', 'webfilter']
            }
        }
        
        config = {
            'firewall_integrations': {
                'palo_alto': palo_alto_config,
                'cisco_asa': cisco_asa_config,
                'fortinet': fortinet_config
            },
            'global_settings': {
                'max_polling_threads': 10,
                'event_buffer_size': 5000,
                'connection_timeout': 30,
                'retry_attempts': 3,
                'retry_delay': 5
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ Firewall configurations created!")
    
    def create_integration_modules(self):
        """Create firewall integration modules"""
        print("🔧 Creating firewall integration modules...")
        
        # Create integrations directory
        Path(self.integration_dir).mkdir(exist_ok=True)
        
        # Palo Alto Integration Module
        palo_alto_module = '''"""
Palo Alto Networks Integration Module
Real-time threat log collection and analysis
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import time
import logging

logger = logging.getLogger(__name__)

class PaloAltoIntegration:
    def __init__(self, config):
        self.host = config['connection']['host']
        self.api_key = config['connection']['api_key']
        self.port = config['connection']['port']
        self.verify_ssl = config['connection']['verify_ssl']
        self.polling_interval = config['polling']['interval']
        self.log_types = config['polling']['log_types']
        self.severity_mapping = config['mapping']['severity_mapping']
        self.category_mapping = config['mapping']['category_mapping']
        
        self.base_url = f"https://{self.host}:{self.port}/api"
        self.headers = {'X-PAN-KEY': self.api_key}
        
    def get_threat_logs(self):
        """Get real-time threat logs from Palo Alto firewall"""
        try:
            url = f"{self.base_url}/?type=log&log-type=threat"
            response = requests.get(url, headers=self.headers, 
                                  verify=self.verify_ssl, timeout=30)
            
            if response.status_code == 200:
                return self.parse_threat_logs(response.text)
            else:
                logger.error(f"Failed to get threat logs: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting threat logs: {e}")
            return []
    
    def parse_threat_logs(self, xml_data):
        """Parse Palo Alto XML threat logs into alerts"""
        alerts = []
        
        try:
            root = ET.fromstring(xml_data)
            
            for log_entry in root.findall('.//log'):
                alert = {
                    'source_ip': self.get_xml_value(log_entry, 'src'),
                    'target_ip': self.get_xml_value(log_entry, 'dst'),
                    'source_port': self.get_xml_value(log_entry, 'sport'),
                    'target_port': self.get_xml_value(log_entry, 'dport'),
                    'protocol': self.get_xml_value(log_entry, 'protocol'),
                    'severity': self.map_severity(
                        self.get_xml_value(log_entry, 'severity')),
                    'threat_name': self.get_xml_value(log_entry, 'threatname'),
                    'category': self.map_category(
                        self.get_xml_value(log_entry, 'category')),
                    'action': self.get_xml_value(log_entry, 'action'),
                    'timestamp': self.get_xml_value(log_entry, 'receive_time'),
                    'user': self.get_xml_value(log_entry, 'user'),
                    'application': self.get_xml_value(log_entry, 'app'),
                    'source': 'palo_alto_firewall',
                    'raw_log': ET.tostring(log_entry)
                }
                alerts.append(alert)
                
        except ET.ParseError as e:
            logger.error(f"Error parsing XML logs: {e}")
            
        return alerts
    
    def get_xml_value(self, element, tag):
        """Extract value from XML element"""
        child = element.find(tag)
        return child.text if child is not None else 'unknown'
    
    def map_severity(self, fw_severity):
        """Map firewall severity to SOC severity"""
        return self.severity_mapping.get(fw_severity.lower(), 'medium')
    
    def map_category(self, fw_category):
        """Map firewall category to SOC category"""
        return self.category_mapping.get(fw_category.lower(), 'unknown')
    
    def start_continuous_polling(self):
        """Start continuous polling for threat logs"""
        logger.info(f"Starting continuous polling from {self.host}")
        
        while True:
            try:
                alerts = self.get_threat_logs()
                if alerts:
                    logger.info(f"Retrieved {len(alerts)} alerts from Palo Alto")
                    # Send alerts to SOC engine
                    self.send_alerts_to_soc(alerts)
                
                time.sleep(self.polling_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping Palo Alto polling")
                break
            except Exception as e:
                logger.error(f"Error in continuous polling: {e}")
                time.sleep(self.polling_interval)
    
    def send_alerts_to_soc(self, alerts):
        """Send alerts to SOC correlation engine"""
        try:
            soc_url = "http://localhost:8000/api/alerts/"
            
            for alert in alerts:
                response = requests.post(soc_url, json=alert, timeout=10)
                if response.status_code == 201:
                    logger.debug(f"Alert sent to SOC: {alert['threat_name']}")
                else:
                    logger.error(f"Failed to send alert to SOC: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending alerts to SOC: {e}")
    
    def test_connection(self):
        """Test connection to Palo Alto firewall"""
        try:
            url = f"{self.base_url}/?type=op&cmd=<show><system><info></info></system></show>"
            response = requests.get(url, headers=self.headers, 
                                  verify=self.verify_ssl, timeout=10)
            
            if response.status_code == 200:
                logger.info("Palo Alto connection successful")
                return True
            else:
                logger.error(f"Palo Alto connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Palo Alto connection error: {e}")
            return False
'''
        
        with open(f"{self.integration_dir}/palo_alto.py", 'w') as f:
            f.write(palo_alto_module)
        
        # Cisco ASA Integration Module
        cisco_asa_module = '''"""
Cisco ASA Integration Module
SSH-based log collection from Cisco ASA firewalls
"""

import paramiko
import re
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class CiscoASAIntegration:
    def __init__(self, config):
        self.host = config['connection']['host']
        self.username = config['connection']['username']
        self.password = config['connection']['password']
        self.port = config['connection']['port']
        self.polling_interval = config['polling']['interval']
        self.commands = config['polling']['commands']
        
        self.ssh_client = None
        
    def connect(self):
        """Establish SSH connection to Cisco ASA"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.host, 
                port=self.port,
                username=self.username, 
                password=self.password,
                timeout=10
            )
            logger.info(f"Connected to Cisco ASA at {self.host}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Cisco ASA: {e}")
            return False
    
    def disconnect(self):
        """Disconnect SSH connection"""
        if self.ssh_client:
            self.ssh_client.close()
            logger.info("Disconnected from Cisco ASA")
    
    def get_security_logs(self):
        """Get security logs from Cisco ASA"""
        if not self.ssh_client:
            return []
        
        alerts = []
        
        for command in self.commands:
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command(command)
                output = stdout.read()
                
                # Parse ASA log output
                parsed_alerts = self.parse_asa_logs(output)
                alerts.extend(parsed_alerts)
                
            except Exception as e:
                logger.error(f"Error executing command '{command}': {e}")
        
        return alerts
    
    def parse_asa_logs(self, log_data):
        """Parse ASA log output into alerts"""
        alerts = []
        lines = log_data.split('\\n')
        
        for line in lines:
            if '%ASA-' in line:
                alert = self.parse_asa_log_line(line)
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def parse_asa_log_line(self, line):
        """Parse individual ASA log line"""
        # ASA log format: %ASA-<level>-<message_id>: <message>
        # Example: %ASA-4-106023: Deny tcp src inside:10.0.0.1/53213 dst outside:192.168.1.100/80 by access-group "inside"
        
        try:
            # Extract basic information using regex
            pattern = r'%ASA-(\\d+)-(\\d+): (.+)'
            match = re.match(pattern, line)
            
            if match:
                severity_level = int(match.group(1))
                message = match.group(2)
                
                alert = {
                    'severity': self.map_asa_severity(severity_level),
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'cisco_asa',
                    'raw_log': line
                }
                
                # Extract IP addresses if present
                ip_pattern = r'(\\d+\\.\\d+\\.\\d+\\.\\d+)'
                ips = re.findall(ip_pattern, message)
                
                if len(ips) >= 2:
                    alert['source_ip'] = ips[0]
                    alert['target_ip'] = ips[1]
                
                return alert
                
        except Exception as e:
            logger.error(f"Error parsing ASA log line: {e}")
        
        return None
    
    def map_asa_severity(self, asa_level):
        """Map ASA severity levels to SOC severity"""
        if asa_level <= 2:
            return 'critical'
        elif asa_level <= 4:
            return 'high'
        elif asa_level <= 6:
            return 'medium'
        else:
            return 'low'
    
    def start_continuous_polling(self):
        """Start continuous polling for security logs"""
        logger.info(f"Starting continuous polling from {self.host}")
        
        if not self.connect():
            return
        
        try:
            while True:
                alerts = self.get_security_logs()
                if alerts:
                    logger.info(f"Retrieved {len(alerts)} alerts from Cisco ASA")
                    self.send_alerts_to_soc(alerts)
                
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping Cisco ASA polling")
        finally:
            self.disconnect()
    
    def send_alerts_to_soc(self, alerts):
        """Send alerts to SOC correlation engine"""
        try:
            import requests
            soc_url = "http://localhost:8000/api/alerts/"
            
            for alert in alerts:
                response = requests.post(soc_url, json=alert, timeout=10)
                if response.status_code == 201:
                    logger.debug(f"Alert sent to SOC: {alert['message']}")
                else:
                    logger.error(f"Failed to send alert to SOC: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending alerts to SOC: {e}")
    
    def test_connection(self):
        """Test connection to Cisco ASA"""
        if self.connect():
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command("show version")
                output = stdout.read()
                
                if "Cisco Adaptive Security Appliance" in output:
                    logger.info("Cisco ASA connection successful")
                    return True
                else:
                    logger.error("Device is not a Cisco ASA")
                    return False
                    
            except Exception as e:
                logger.error(f"Error testing Cisco ASA connection: {e}")
            finally:
                self.disconnect()
        
        return False
'''
        
        with open(f"{self.integration_dir}/cisco_asa.py", 'w') as f:
            f.write(cisco_asa_module)
        
        print("✅ Firewall integration modules created!")
    
    def create_docker_compose(self):
        """Create Docker Compose configuration for firewall integration"""
        print("🐳 Creating Docker Compose configuration with firewall integration...")
        
        docker_compose = {
            'version': '3.8',
            'services': {
                'soc-engine': {
                    'image': 'soc-correlation-engine:latest',
                    'ports': ['80:8000', '443:8443'],
                    'environment': [
                        'DATABASE_URL=mongodb://database:27017/soc_engine',
                        'REDIS_URL=redis://cache:6379',
                        'DEBUG=false',
                        'LOG_LEVEL=INFO',
                        'FIREWALL_INTEGRATION=true'
                    ],
                    'depends_on': ['database', 'cache'],
                    'networks': ['internal-network'],
                    'restart': 'unless-stopped',
                    'volumes': [
                        './logs:/app/logs',
                        './config/firewall_deployment.yml:/app/config/firewall.yml:ro',
                        './app/integrations:/app/integrations:ro'
                    ]
                },
                'database': {
                    'image': 'mongo:6.0',
                    'environment': [
                        'MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USER}',
                        'MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASS}',
                        'MONGO_INITDB_DATABASE=soc_engine'
                    ],
                    'volumes': [
                        'mongodb_data:/data/db',
                        './mongo-init.js:/docker-entrypoint-initdb.d/mongo-init.js:ro'
                    ],
                    'networks': ['internal-network'],
                    'restart': 'unless-stopped'
                },
                'cache': {
                    'image': 'redis:7-alpine',
                    'command': 'redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}',
                    'volumes': [
                        'redis_data:/data'
                    ],
                    'networks': ['internal-network'],
                    'restart': 'unless-stopped'
                },
                'firewall-collector': {
                    'image': 'python:3.9-slim',
                    'command': [
                        'python', '-m', 'pip', 'install', 'requests', 'paramiko', '&&',
                        'python', '/app/integrations/firewall_collector.py'
                    ],
                    'volumes': [
                        './config/firewall_deployment.yml:/app/config/firewall.yml:ro',
                        './app/integrations:/app/integrations:ro'
                    ],
                    'networks': ['host-network', 'internal-network'],
                    'restart': 'unless-stopped',
                    'depends_on': ['soc-engine']
                }
            },
            'volumes': {
                'mongodb_data': {},
                'redis_data': {}
            },
            'networks': {
                'internal-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '172.20.0.0/16'}]
                    }
                },
                'host-network': {
                    'driver': 'bridge'
                }
            }
        }
        
        with open(self.docker_compose_file, 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
        
        print("✅ Docker Compose configuration created!")
    
    def create_firewall_collector(self):
        """Create firewall collector service"""
        print("🔥 Creating firewall collector service...")
        
        collector_script = '''#!/usr/bin/env python3
"""
Firewall Collector Service
Collects logs from multiple firewall types and sends to SOC engine
"""

import yaml
import time
import logging
import sys
import os

# Add integrations to path
sys.path.append('/app/integrations')

from palo_alto import PaloAltoIntegration
from cisco_asa import CiscoASAIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirewallCollector:
    def __init__(self):
        self.config_file = '/app/config/firewall.yml'
        self.config = self.load_config()
        self.integrations = []
        self.setup_integrations()
    
    def load_config(self):
        """Load firewall configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def setup_integrations(self):
        """Setup enabled firewall integrations"""
        firewall_configs = self.config.get('firewall_integrations', {})
        
        if firewall_configs.get('palo_alto', {}).get('enabled', False):
            palo_alto = PaloAltoIntegration(firewall_configs['palo_alto'])
            if palo_alto.test_connection():
                self.integrations.append(palo_alto)
                logger.info("Palo Alto integration enabled")
        
        if firewall_configs.get('cisco_asa', {}).get('enabled', False):
            cisco_asa = CiscoASAIntegration(firewall_configs['cisco_asa'])
            if cisco_asa.test_connection():
                self.integrations.append(cisco_asa)
                logger.info("Cisco ASA integration enabled")
    
    def start_collection(self):
        """Start collecting logs from all enabled firewalls"""
        logger.info("Starting firewall log collection...")
        
        if not self.integrations:
            logger.warning("No firewall integrations enabled")
            return
        
        # Start all integrations
        import threading
        
        threads = []
        for integration in self.integrations:
            thread = threading.Thread(target=integration.start_continuous_polling)
            thread.daemon = True
            thread.start()
            threads.append(thread)
            logger.info(f"Started {integration.__class__.__name__}")
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(60)
                # Check thread health
                for i, thread in enumerate(threads):
                    if not thread.is_alive():
                        logger.warning(f"Integration thread {i} died, restarting...")
                        # Restart logic would go here
        
        except KeyboardInterrupt:
            logger.info("Stopping firewall collector...")
            # Cleanup would go here

if __name__ == "__main__":
    collector = FirewallCollector()
    collector.start_collection()
'''
        
        with open(f"{self.integration_dir}/firewall_collector.py", 'w') as f:
            f.write(collector_script)
        
        print("✅ Firewall collector service created!")
    
    def create_environment_file(self):
        """Create environment configuration for firewall deployment"""
        print("⚙️ Creating environment configuration...")
        
        env_config = """# Firewall Integration Deployment Configuration
# Database Configuration
DATABASE_URL=mongodb://admin:secure_password@database:27017/soc_engine
REDIS_URL=redis://redis:secure_password@cache:6379

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Firewall Integration
FIREWALL_INTEGRATION=true
PALO_ALTO_HOST=192.168.1.1
PALO_ALTO_API_KEY=your_palo_alto_api_key
CISCO_ASA_HOST=192.168.1.254
CISCO_ASA_USER=admin
CISCO_ASA_PASSWORD=your_cisco_asa_password
FORTINET_HOST=192.168.1.253
FORTINET_API_KEY=your_fortinet_api_key

# External API Keys
VIRUSTOTAL_API_KEY=your_virustotal_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
OTX_API_KEY=your_otx_api_key
SHODAN_API_KEY=your_shodan_api_key

# Performance Configuration
ALERT_BATCH_SIZE=500
CORRELATION_TIME_WINDOW=7200000
CRITICALITY_THRESHOLD=8.0

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/app/logs/soc_engine.log

# Network Configuration
DMZ_NETWORK=192.168.100.0/24
INTERNAL_NETWORK=172.20.0.0/16
"""
        
        with open('.env.firewall', 'w') as f:
            f.write(env_config)
        
        print("✅ Environment configuration created!")
    
    def deploy(self):
        """Main deployment method"""
        print("🔥 Starting Firewall Integration Deployment")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        self.check_prerequisites()
        
        # Step 2: Create configurations
        self.create_firewall_configs()
        self.create_integration_modules()
        self.create_firewall_collector()
        self.create_docker_compose()
        self.create_environment_file()
        
        # Step 3: Deploy services
        print("🚀 Deploying services with firewall integration...")
        
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "up", "-d"
            ], check=True, capture_output=True)
            
            print("✅ Firewall integration deployment completed!")
            print("🌐 Access your SOC Engine at: http://localhost:8000")
            print("🔍 Firewall logs are now being collected in real-time")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--firewall":
        deployment = FirewallDeployment()
        deployment.deploy()
    else:
        print("Usage: python deploy_firewall.py --firewall")
        print("This will deploy SOC Engine with firewall integration")
        sys.exit(1)
'''
        
        with open(f"{self.integration_dir}/firewall_collector.py", 'w') as f:
            f.write(collector_script)
        
        print("✅ Firewall collector service created!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--firewall":
        deployment = FirewallDeployment()
        deployment.deploy()
    else:
        print("Usage: python deploy_firewall.py --firewall")
        print("This will deploy SOC Engine with firewall integration")
        sys.exit(1)
