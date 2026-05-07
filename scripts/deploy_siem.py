#!/usr/bin/env python3
"""
SIEM Integration Deployment Script
Deploy SOC Correlation Engine with SIEM platform integration
"""

import os
import sys
import subprocess
import yaml
import json
import time
from pathlib import Path

class SIEMDeployment:
    def __init__(self):
        self.config_file = "config/siem_deployment.yml"
        self.docker_compose_file = "docker-compose.siem.yml"
        self.integration_dir = "app/integrations"
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking SIEM integration prerequisites...")
        
        prerequisites = {
            "docker": self.check_command("docker --version"),
            "docker-compose": self.check_command("docker-compose --version"),
            "python3": self.check_command("python3 --version"),
            "curl": self.check_command("curl --version"),
            "pip": self.check_command("pip --version")
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
    
    def create_siem_configs(self):
        """Create SIEM integration configurations"""
        print("🛡️ Creating SIEM integration configurations...")
        
        # Splunk Integration Configuration
        splunk_config = {
            'enabled': True,
            'siem_type': 'splunk',
            'connection': {
                'host': os.getenv('SPLUNK_HOST', 'localhost'),
                'port': int(os.getenv('SPLUNK_PORT', '8089')),
                'scheme': 'https',
                'verify_ssl': False
            },
            'authentication': {
                'username': os.getenv('SPLUNK_USERNAME', 'admin'),
                'password': os.getenv('SPLUNK_PASSWORD', 'changeme'),
                'token': os.getenv('SPLUNK_TOKEN', '')
            },
            'indexing': {
                'index': 'security_alerts',
                'source_type': 'soc_correlation',
                'sourcetype': 'json'
            },
            'querying': {
                'search_query': 'index=security sourcetype=* | head 1000',
                'real_time_query': 'index=security sourcetype=* | rt',
                'time_range': '-24h@h',
                'max_results': 10000
            },
            'correlation_export': {
                'enabled': True,
                'export_format': 'json',
                'export_interval': 300,  # 5 minutes
                'correlation_index': 'correlations'
            }
        }
        
        # IBM QRadar Integration Configuration
        qradar_config = {
            'enabled': False,
            'siem_type': 'qradar',
            'connection': {
                'host': os.getenv('QRADAR_HOST', '192.168.1.100'),
                'port': int(os.getenv('QRADAR_PORT', '443')),
                'api_version': '12.0',
                'verify_ssl': False
            },
            'authentication': {
                'username': os.getenv('QRADAR_USERNAME', 'admin'),
                'password': os.getenv('QRADAR_PASSWORD', 'changeme'),
                'token': os.getenv('QRADAR_TOKEN', '')
            },
            'offense_management': {
                'auto_create': True,
                'correlation_reference': True,
                'severity_mapping': {
                    'critical': 10,
                    'high': 8,
                    'medium': 6,
                    'low': 4
                }
            },
            'api_endpoints': {
                'offenses': '/api/siem/offenses',
                'reference_data': '/api/reference_data/sets',
                'ariel_query': '/api/ariel/search'
            }
        }
        
        # Microsoft Sentinel Integration Configuration
        sentinel_config = {
            'enabled': False,
            'siem_type': 'microsoft_sentinel',
            'connection': {
                'workspace_id': os.getenv('SENTINEL_WORKSPACE_ID', ''),
                'tenant_id': os.getenv('SENTINEL_TENANT_ID', ''),
                'client_id': os.getenv('SENTINEL_CLIENT_ID', ''),
                'client_secret': os.getenv('SENTINEL_CLIENT_SECRET', ''),
                'api_version': '2021-03-01'
            },
            'authentication': {
                'method': 'client_secret',  # or 'certificate'
                'certificate_path': os.getenv('SENTINEL_CERT_PATH', ''),
                'certificate_key_path': os.getenv('SENTINEL_CERT_KEY_PATH', '')
            },
            'log_analytics': {
                'workspace': 'default',
                'table': 'SecurityAlert',
                'time_field': 'TimeGenerated',
                'query_template': 'SecurityAlert | where TimeGenerated > ago({time_range}s)'
            },
            'correlation_export': {
                'enabled': True,
                'export_table': 'SOC_Correlations',
                'export_frequency': '5m'
            }
        }
        
        # Elastic SIEM Integration Configuration
        elastic_config = {
            'enabled': False,
            'siem_type': 'elastic_siem',
            'connection': {
                'hosts': os.getenv('ELASTIC_HOSTS', 'localhost:9200'),
                'username': os.getenv('ELASTIC_USERNAME', 'elastic'),
                'password': os.getenv('ELASTIC_PASSWORD', 'changeme'),
                'verify_ssl': False
            },
            'indexing': {
                'alerts_index': 'soc-alerts',
                'correlations_index': 'soc-correlations',
                'template': 'soc-alert-template'
            },
            'querying': {
                'alerts_query': {
                    'query': {
                        'bool': {
                            'must': [
                                {'range': {'timestamp': {'gte': 'now-24h'}}}
                            ]
                        }
                    },
                    'sort': [{'timestamp': {'order': 'desc'}}]
                }
            }
        }
        
        config = {
            'siem_integrations': {
                'splunk': splunk_config,
                'qradar': qradar_config,
                'microsoft_sentinel': sentinel_config,
                'elastic_siem': elastic_config
            },
            'global_settings': {
                'max_concurrent_connections': 10,
                'retry_attempts': 3,
                'retry_delay': 5,
                'timeout': 30,
                'batch_size': 100,
                'buffer_size': 1000
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print("✅ SIEM configurations created!")
    
    def create_integration_modules(self):
        """Create SIEM integration modules"""
        print("🔧 Creating SIEM integration modules...")
        
        # Create integrations directory
        Path(self.integration_dir).mkdir(exist_ok=True)
        
        # Splunk Integration Module
        splunk_module = '''"""
Splunk Integration Module
Real-time bidirectional integration with Splunk SIEM
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from splunklib import client as splunk_client

logger = logging.getLogger(__name__)

class SplunkIntegration:
    def __init__(self, config):
        self.host = config['connection']['host']
        self.port = config['connection']['port']
        self.scheme = config['connection']['scheme']
        self.verify_ssl = config['connection']['verify_ssl']
        
        if config['authentication'].get('token'):
            self.token = config['authentication']['token']
            self.service = None
        else:
            self.username = config['authentication']['username']
            self.password = config['authentication']['password']
            self.service = splunk_client.Service(
                scheme=self.scheme,
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                verify=self.verify_ssl
            )
            self.token = None
        
        self.index = config['indexing']['index']
        self.source_type = config['indexing']['source_type']
        self.sourcetype = config['indexing']['sourcetype']
        
        self.search_query = config['querying']['search_query']
        self.real_time_query = config['querying']['real_time_query']
        self.time_range = config['querying']['time_range']
        self.max_results = config['querying']['max_results']
        
        self.correlation_export = config['correlation_export']
        self.export_format = self.correlation_export['export_format']
        self.export_interval = self.correlation_export['export_interval']
        self.correlation_index = self.correlation_export['correlation_index']
        
    def connect(self):
        """Establish connection to Splunk"""
        try:
            if self.service:
                self.service.login()
                logger.info(f"Connected to Splunk at {self.host}:{self.port}")
                return True
            elif self.token:
                # Test token-based connection
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(f"{self.scheme}://{self.host}:{self.port}/services/auth/login", 
                                      headers=headers, verify=self.verify_ssl)
                if response.status_code == 200:
                    logger.info(f"Connected to Splunk via token at {self.host}:{self.port}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Splunk: {e}")
            return False
    
    def get_security_alerts(self):
        """Get security alerts from Splunk"""
        try:
            if self.service:
                results = self.service.query(
                    self.search_query,
                    count=self.max_results,
                    earliest_time=datetime.utcnow() - timedelta(hours=24)
                )
                
                alerts = []
                for result in results:
                    alert = {
                        'id': result.get('_serial', ''),
                        'timestamp': result.get('_time', ''),
                        'source_ip': result.get('src_ip', ''),
                        'target_ip': result.get('dest_ip', ''),
                        'severity': self.map_severity(result.get('severity', 'medium')),
                        'threat_name': result.get('threat_name', ''),
                        'category': result.get('category', 'unknown'),
                        'description': result.get('description', ''),
                        'source': 'splunk',
                        'raw_data': result
                    }
                    alerts.append(alert)
                
                return alerts
            else:
                # Use REST API with token
                headers = {'Authorization': f'Bearer {self.token}'}
                url = f"{self.scheme}://{self.host}:{self.port}/services/search/jobs/export"
                
                params = {
                    'search': self.search_query,
                    'output_mode': 'json',
                    'earliest_time': (datetime.utcnow() - timedelta(hours=24)).isoformat(),
                    'latest_time': datetime.utcnow().isoformat(),
                    'max_count': self.max_results
                }
                
                response = requests.post(url, headers=headers, params=params, verify=self.verify_ssl)
                if response.status_code == 200:
                    return self.parse_splunk_results(response.json())
                else:
                    logger.error(f"Failed to get alerts from Splunk: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting alerts from Splunk: {e}")
            return []
    
    def send_correlation_results(self, correlations):
        """Send correlation results to Splunk"""
        try:
            if not self.correlation_export['enabled']:
                return
            
            for correlation in correlations:
                event = {
                    'time': datetime.utcnow().isoformat(),
                    'index': self.correlation_index,
                    'source': 'soc_correlation_engine',
                    'sourcetype': self.sourcetype,
                    'event': {
                        'correlation_id': correlation['id'],
                        'correlation_score': correlation['risk_score'],
                        'confidence': correlation['confidence'],
                        'risk_level': correlation['risk_level'],
                        'alert_count': correlation['alert_count'],
                        'patterns': correlation.get('patterns', []),
                        'recommendations': correlation.get('recommendations', []),
                        'created_at': correlation['created_at']
                    }
                }
                
                if self.service:
                    # Use Splunk SDK
                    self.service.index(event, index=self.correlation_index)
                else:
                    # Use REST API
                    headers = {'Authorization': f'Bearer {self.token}'}
                    url = f"{self.scheme}://{self.host}:{self.port}/services/receiver/simple"
                    
                    response = requests.post(url, headers=headers, json=event, verify=self.verify_ssl)
                    if response.status_code == 200:
                        logger.info(f"Correlation {correlation['id']} sent to Splunk")
                    else:
                        logger.error(f"Failed to send correlation to Splunk: {response.status_code}")
                        
        except Exception as e:
            logger.error(f"Error sending correlation to Splunk: {e}")
    
    def start_real_time_collection(self):
        """Start real-time alert collection from Splunk"""
        logger.info("Starting real-time collection from Splunk")
        
        if not self.connect():
            return
        
        try:
            while True:
                alerts = self.get_security_alerts()
                if alerts:
                    logger.info(f"Retrieved {len(alerts)} alerts from Splunk")
                    # Send alerts to SOC engine
                    self.send_alerts_to_soc(alerts)
                
                time.sleep(60)  # Poll every minute
                
        except KeyboardInterrupt:
            logger.info("Stopping Splunk collection")
        except Exception as e:
            logger.error(f"Error in real-time collection: {e}")
    
    def send_alerts_to_soc(self, alerts):
        """Send alerts to SOC correlation engine"""
        try:
            soc_url = "http://localhost:8000/api/alerts/"
            
            for alert in alerts:
                response = requests.post(soc_url, json=alert, timeout=10)
                if response.status_code == 201:
                    logger.debug(f"Alert sent to SOC: {alert.get('threat_name', 'unknown')}")
                else:
                    logger.error(f"Failed to send alert to SOC: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending alerts to SOC: {e}")
    
    def map_severity(self, splunk_severity):
        """Map Splunk severity to SOC severity"""
        mapping = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'informational': 'info'
        }
        return mapping.get(splunk_severity.lower(), 'medium')
    
    def parse_splunk_results(self, results):
        """Parse Splunk REST API results"""
        alerts = []
        
        if 'results' in results:
            for result in results['results']:
                alert = {
                    'id': result.get('_serial', ''),
                    'timestamp': result.get('_time', ''),
                    'source_ip': result.get('src_ip', ''),
                    'target_ip': result.get('dest_ip', ''),
                    'severity': self.map_severity(result.get('severity', 'medium')),
                    'threat_name': result.get('threat_name', ''),
                    'category': result.get('category', 'unknown'),
                    'description': result.get('description', ''),
                    'source': 'splunk',
                    'raw_data': result
                }
                alerts.append(alert)
        
        return alerts
    
    def test_connection(self):
        """Test connection to Splunk"""
        logger.info("Testing Splunk connection...")
        return self.connect()
'''
        
        with open(f"{self.integration_dir}/splunk.py", 'w') as f:
            f.write(splunk_module)
        
        # QRadar Integration Module
        qradar_module = '''"""
IBM QRadar Integration Module
Integration with IBM QRadar SIEM for bidirectional data exchange
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

class QRadarIntegration:
    def __init__(self, config):
        self.host = config['connection']['host']
        self.port = config['connection']['port']
        self.api_version = config['connection']['api_version']
        self.verify_ssl = config['connection']['verify_ssl']
        
        self.auth = HTTPBasicAuth(
            config['authentication']['username'],
            config['authentication']['password']
        )
        
        if config['authentication'].get('token'):
            self.token = config['authentication']['token']
            self.auth = None
        else:
            self.token = None
        
        self.offense_endpoint = f"https://{self.host}:{self.port}{config['api_endpoints']['offenses']}"
        self.reference_endpoint = f"https://{self.host}:{self.port}{config['api_endpoints']['reference_data']}"
        self.ariel_endpoint = f"https://{self.host}:{self.port}{config['api_endpoints']['ariel_query']}"
        
        self.correlation_reference = config['offense_management']['correlation_reference']
        self.severity_mapping = config['offense_management']['severity_mapping']
        self.auto_create_offense = config['offense_management']['auto_create']
    
    def get_offenses(self, time_range=3600):
        """Get offenses from QRadar"""
        try:
            params = {
                'filter': f"start_time >= {int(time.time() - time_range)}"
            }
            
            if self.token:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(self.offense_endpoint, headers=headers, 
                                      params=params, verify=self.verify_ssl)
            else:
                response = requests.get(self.offense_endpoint, auth=self.auth, 
                                      params=params, verify=self.verify_ssl)
            
            if response.status_code == 200:
                return self.parse_qradar_offenses(response.json())
            else:
                logger.error(f"Failed to get offenses: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting offenses from QRadar: {e}")
            return []
    
    def create_correlation_reference(self, correlation):
        """Create reference in QRadar for correlation"""
        try:
            if not self.correlation_reference:
                return True
            
            data = {
                'name': f"SOC_Correlation_{correlation['id']}",
                'value': correlation['risk_score'],
                'description': correlation.get('description', ''),
                'reference_type': 'correlation_score'
            }
            
            if self.token:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.post(self.reference_endpoint, headers=headers, 
                                      json=data, verify=self.verify_ssl)
            else:
                response = requests.post(self.reference_endpoint, auth=self.auth, 
                                      json=data, verify=self.verify_ssl)
            
            return response.status_code == 201
            
        except Exception as e:
            logger.error(f"Error creating correlation reference: {e}")
            return False
    
    def parse_qradar_offenses(self, offenses_data):
        """Parse QRadar offenses into alerts"""
        alerts = []
        
        if offenses_data and len(offenses_data) > 0:
            for offense in offenses_data:
                alert = {
                    'id': str(offense.get('id', '')),
                    'timestamp': offense.get('start_time', ''),
                    'severity': self.map_qradar_severity(offense.get('severity', 3)),
                    'threat_name': offense.get('offense_type', ''),
                    'category': offense.get('offense_source', 'unknown'),
                    'description': offense.get('description', ''),
                    'source_ip': self.extract_ip_from_description(offense.get('description', '')),
                    'target_ip': '',  # QRadar may not always provide target
                    'source': 'qradar',
                    'raw_data': offense
                }
                alerts.append(alert)
        
        return alerts
    
    def map_qradar_severity(self, qradar_severity):
        """Map QRadar severity (1-10) to SOC severity"""
        if qradar_severity >= 8:
            return 'critical'
        elif qradar_severity >= 6:
            return 'high'
        elif qradar_severity >= 4:
            return 'medium'
        elif qradar_severity >= 2:
            return 'low'
        else:
            return 'info'
    
    def extract_ip_from_description(self, description):
        """Extract IP address from QRadar description"""
        import re
        ip_pattern = r'\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b'
        match = re.search(ip_pattern, description)
        return match.group() if match else None
    
    def start_real_time_collection(self):
        """Start real-time offense collection from QRadar"""
        logger.info("Starting real-time collection from QRadar")
        
        try:
            while True:
                offenses = self.get_offenses()
                if offenses:
                    logger.info(f"Retrieved {len(offenses)} offenses from QRadar")
                    # Send alerts to SOC engine
                    self.send_alerts_to_soc(offenses)
                
                time.sleep(120)  # Poll every 2 minutes
                
        except KeyboardInterrupt:
            logger.info("Stopping QRadar collection")
        except Exception as e:
            logger.error(f"Error in real-time collection: {e}")
    
    def send_alerts_to_soc(self, offenses):
        """Send offenses as alerts to SOC correlation engine"""
        try:
            soc_url = "http://localhost:8000/api/alerts/"
            
            for offense in offenses:
                alert = {
                    'id': str(offense.get('id', '')),
                    'timestamp': offense.get('start_time', ''),
                    'severity': offense.get('severity', 'medium'),
                    'threat_name': offense.get('offense_type', ''),
                    'category': offense.get('offense_source', 'unknown'),
                    'description': offense.get('description', ''),
                    'source_ip': self.extract_ip_from_description(offense.get('description', '')),
                    'source': 'qradar',
                    'raw_data': offense
                }
                
                response = requests.post(soc_url, json=alert, timeout=10)
                if response.status_code == 201:
                    logger.debug(f"Offense sent to SOC: {offense.get('offense_type', 'unknown')}")
                else:
                    logger.error(f"Failed to send offense to SOC: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error sending offenses to SOC: {e}")
    
    def test_connection(self):
        """Test connection to QRadar"""
        logger.info("Testing QRadar connection...")
        
        try:
            if self.token:
                headers = {'Authorization': f'Bearer {self.token}'}
                response = requests.get(f"https://{self.host}:{self.port}/api/about", 
                                      headers=headers, verify=self.verify_ssl)
            else:
                response = requests.get(f"https://{self.host}:{self.port}/api/about", 
                                      auth=self.auth, verify=self.verify_ssl)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"QRadar connection test failed: {e}")
            return False
'''
        
        with open(f"{self.integration_dir}/qradar.py", 'w') as f:
            f.write(qradar_module)
        
        print("✅ SIEM integration modules created!")
    
    def create_docker_compose(self):
        """Create Docker Compose configuration for SIEM integration"""
        print("🐳 Creating Docker Compose configuration for SIEM integration...")
        
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
                        'SIEM_INTEGRATION=true'
                    ],
                    'depends_on': ['database', 'cache'],
                    'networks': ['internal-network'],
                    'restart': 'unless-stopped',
                    'volumes': [
                        './logs:/app/logs',
                        './data:/app/data',
                        './config/siem_deployment.yml:/app/config/siem.yml:ro',
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
                'siem-collector': {
                    'image': 'python:3.9-slim',
                    'command': [
                        'python', '-m', 'pip', 'install', 'splunk-sdk', 'requests', '&&',
                        'python', '/app/integrations/siem_collector.py'
                    ],
                    'volumes': [
                        './config/siem_deployment.yml:/app/config/siem.yml:ro',
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
    
    def create_siem_collector(self):
        """Create SIEM collector service"""
        print("🔧 Creating SIEM collector service...")
        
        collector_script = '''#!/usr/bin/env python3
"""
SIEM Collector Service
Collects alerts from multiple SIEM platforms and sends to SOC engine
"""

import yaml
import time
import logging
import sys
import os

# Add integrations to path
sys.path.append('/app/integrations')

from splunk import SplunkIntegration
from qradar import QRadarIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SIEMCollector:
    def __init__(self):
        self.config_file = '/app/config/siem.yml'
        self.config = self.load_config()
        self.integrations = []
        self.setup_integrations()
    
    def load_config(self):
        """Load SIEM configuration"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def setup_integrations(self):
        """Setup enabled SIEM integrations"""
        siem_configs = self.config.get('siem_integrations', {})
        
        if siem_configs.get('splunk', {}).get('enabled', False):
            splunk = SplunkIntegration(siem_configs['splunk'])
            if splunk.test_connection():
                self.integrations.append(splunk)
                logger.info("Splunk integration enabled")
        
        if siem_configs.get('qradar', {}).get('enabled', False):
            qradar = QRadarIntegration(siem_configs['qradar'])
            if qradar.test_connection():
                self.integrations.append(qradar)
                logger.info("QRadar integration enabled")
    
    def start_collection(self):
        """Start collecting from all enabled SIEMs"""
        logger.info("Starting SIEM log collection...")
        
        if not self.integrations:
            logger.warning("No SIEM integrations enabled")
            return
        
        import threading
        
        threads = []
        for integration in self.integrations:
            thread = threading.Thread(target=integration.start_real_time_collection)
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
                        logger.warning(f"SIEM integration thread {i} died, restarting...")
                        # Restart logic would go here
        
        except KeyboardInterrupt:
            logger.info("Stopping SIEM collector...")
            # Cleanup would go here

if __name__ == "__main__":
    collector = SIEMCollector()
    collector.start_collection()
'''
        
        with open(f"{self.integration_dir}/siem_collector.py", 'w') as f:
            f.write(collector_script)
        
        print("✅ SIEM collector service created!")
    
    def create_environment_file(self):
        """Create environment configuration for SIEM deployment"""
        print("⚙️ Creating environment configuration...")
        
        env_config = """# SIEM Integration Deployment Configuration
# Database Configuration
DATABASE_URL=mongodb://admin:secure_password@database:27017/soc_engine
REDIS_URL=redis://redis:secure_password@cache:6379

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SIEM Integration
SIEM_INTEGRATION=true
SPLUNK_HOST=localhost
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=changeme
SPLUNK_TOKEN=

QRADAR_HOST=192.168.1.100
QRADAR_PORT=443
QRADAR_USERNAME=admin
QRADAR_PASSWORD=changeme
QRADAR_TOKEN=

# Microsoft Sentinel
SENTINEL_WORKSPACE_ID=
SENTINEL_TENANT_ID=
SENTINEL_CLIENT_ID=
SENTINEL_CLIENT_SECRET=

# Elastic SIEM
ELASTIC_HOSTS=localhost:9200
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=changeme

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
SIEM_NETWORK=host-network
INTERNAL_NETWORK=172.20.0.0/16
"""
        
        with open('.env.siem', 'w') as f:
            f.write(env_config)
        
        print("✅ Environment configuration created!")
    
    def deploy(self):
        """Main deployment method"""
        print("🛡️ Starting SIEM Integration Deployment")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        self.check_prerequisites()
        
        # Step 2: Create configurations
        self.create_siem_configs()
        self.create_integration_modules()
        self.create_siem_collector()
        self.create_docker_compose()
        self.create_environment_file()
        
        # Step 3: Deploy services
        print("🚀 Deploying services with SIEM integration...")
        
        try:
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "up", "-d"
            ], check=True, capture_output=True)
            
            print("✅ SIEM integration deployment completed!")
            print("🌐 Access your SOC Engine at: http://localhost:8000")
            print("📊 SIEM logs are now being collected in real-time")
            print("🔍 Check SIEM integration status at: http://localhost:8000/api/dashboard/siem-status")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--siem":
        deployment = SIEMDeployment()
        deployment.deploy()
    else:
        print("Usage: python deploy_siem.py --siem")
        print("This will deploy SOC Engine with SIEM integration")
        sys.exit(1)
'''
        
        with open(f"{self.integration_dir}/siem_collector.py", 'w') as f:
            f.write(collector_script)
        
        print("✅ SIEM collector service created!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--siem":
        deployment = SIEMDeployment()
        deployment.deploy()
    else:
        print("Usage: python deploy_siem.py --siem")
        print("This will deploy SOC Engine with SIEM integration")
        sys.exit(1)
