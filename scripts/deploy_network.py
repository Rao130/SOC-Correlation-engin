#!/usr/bin/env python3
"""
Network Deployment Script for World-Class SOC Correlation Engine
Automated deployment for on-premises network infrastructure
"""

import os
import sys
import subprocess
import yaml
import json
import time
from pathlib import Path

class NetworkDeployment:
    def __init__(self):
        self.config_file = "config/network_deployment.yml"
        self.docker_compose_file = "docker-compose.production.yml"
        self.nginx_config_file = "config/nginx.conf"
        self.backup_dir = "/backups"
        
    def check_prerequisites(self):
        """Check system prerequisites"""
        print("🔍 Checking system prerequisites...")
        
        prerequisites = {
            "docker": self.check_command("docker --version"),
            "docker-compose": self.check_command("docker-compose --version"),
            "git": self.check_command("git --version"),
            "python3": self.check_command("python3 --version"),
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
    
    def create_directories(self):
        """Create necessary directories"""
        print("📁 Creating directory structure...")
        
        directories = [
            "config",
            "logs",
            "data",
            "backups",
            "ssl",
            "monitoring"
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            print(f"✅ Created {directory}/ directory")
    
    def generate_ssl_certificates(self):
        """Generate self-signed SSL certificates for testing"""
        print("🔐 Generating SSL certificates...")
        
        ssl_dir = Path("ssl")
        ssl_dir.mkdir(exist_ok=True)
        
        # Generate private key
        subprocess.run([
            "openssl", "genrsa", "-out", "ssl/key.pem", "2048"
        ], check=True)
        
        # Generate certificate
        subprocess.run([
            "openssl", "req", "-new", "-x509", "-key", "ssl/key.pem",
            "-out", "ssl/cert.pem", "-days", "365",
            "-subj", "/C=IN/ST=State/L=City/O=Organization/CN=localhost"
        ], check=True)
        
        print("✅ SSL certificates generated successfully!")
    
    def create_nginx_config(self):
        """Create Nginx configuration"""
        print("🌐 Creating Nginx configuration...")
        
        nginx_config = f"""events {{
    worker_connections 1024;
}}

http {{
    upstream soc_engine {{
        server soc-engine:8000;
    }}

    # HTTP to HTTPS redirect
    server {{
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }}

    # HTTPS configuration
    server {{
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # WebSocket support
        location /ws {{
            proxy_pass http://soc_engine;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # API endpoints
        location /api/ {{
            proxy_pass http://soc_engine;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }}

        # Static files
        location /static/ {{
            proxy_pass http://soc_engine;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}

        # Main application
        location / {{
            proxy_pass http://soc_engine;
            proxy_set_header Host $host;
        }}
    }}
}}"""
        
        with open(self.nginx_config_file, 'w') as f:
            f.write(nginx_config)
        
        print("✅ Nginx configuration created!")
    
    def create_docker_compose(self):
        """Create Docker Compose configuration"""
        print("🐳 Creating Docker Compose configuration...")
        
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
                        'LOG_LEVEL=INFO'
                    ],
                    'depends_on': ['database', 'cache'],
                    'networks': ['dmz-network'],
                    'restart': 'unless-stopped',
                    'volumes': [
                        './logs:/app/logs',
                        './data:/app/data'
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
                    'volumes': ['redis_data:/data'],
                    'networks': ['internal-network'],
                    'restart': 'unless-stopped'
                },
                'nginx': {
                    'image': 'nginx:alpine',
                    'ports': ['80:80', '443:443'],
                    'volumes': [
                        f'{self.nginx_config_file}:/etc/nginx/nginx.conf:ro',
                        './ssl:/etc/nginx/ssl:ro'
                    ],
                    'depends_on': ['soc-engine'],
                    'networks': ['dmz-network'],
                    'restart': 'unless-stopped'
                }
            },
            'volumes': {
                'mongodb_data': {},
                'redis_data': {}
            },
            'networks': {
                'dmz-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '192.168.100.0/24'}]
                    }
                },
                'internal-network': {
                    'driver': 'bridge',
                    'ipam': {
                        'config': [{'subnet': '192.168.2.0/24'}]
                    }
                }
            }
        }
        
        with open(self.docker_compose_file, 'w') as f:
            yaml.dump(docker_compose, f, default_flow_style=False)
        
        print("✅ Docker Compose configuration created!")
    
    def create_environment_file(self):
        """Create environment configuration file"""
        print("⚙️ Creating environment configuration...")
        
        env_config = """# Network Deployment Configuration
# Database Configuration
DATABASE_URL=mongodb://admin:secure_password@database:27017/soc_engine
REDIS_URL=redis://redis:secure_password@cache:6379

# Security Configuration
SECRET_KEY=your-super-secure-secret-key-change-in-production-$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External API Keys (Set your actual keys)
VIRUSTOTAL_API_KEY=your_virustotal_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
OTX_API_KEY=your_otx_api_key
SHODAN_API_KEY=your_shodan_api_key

# Performance Configuration
ALERT_BATCH_SIZE=500
CORRELATION_TIME_WINDOW=7200000
CRITICALITY_THRESHOLD=8.0

# Background Tasks
BACKGROUND_TASK_INTERVAL=30
ML_MODEL_UPDATE_INTERVAL=43200

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/soc_engine.log

# Rate Limiting
RATE_LIMIT_WINDOW_MS=600000
RATE_LIMIT_MAX_REQUESTS=1000

# MongoDB Root User
MONGO_ROOT_USER=admin
MONGO_ROOT_PASS=secure_password_change_this_in_production

# Redis Password
REDIS_PASSWORD=secure_password_change_this_in_production
"""
        
        with open('.env.production', 'w') as f:
            f.write(env_config)
        
        print("✅ Environment configuration created!")
    
    def create_mongo_init_script(self):
        """Create MongoDB initialization script"""
        print("📊 Creating MongoDB initialization script...")
        
        mongo_init = """// MongoDB initialization script
db = db.getSiblingDB('soc_engine');

// Create collections with indexes
db.alerts.createIndex({"timestamp": -1});
db.alerts.createIndex({"severity": 1});
db.alerts.createIndex({"source_ip": 1});
db.alerts.createIndex({"target_ip": 1});

db.correlation_groups.createIndex({"created_at": -1});
db.correlation_groups.createIndex({"correlation_score": -1});
db.correlation_groups.createIndex({"status": 1});

db.analyst_feedback.createIndex({"correlation_id": 1});
db.analyst_feedback.createIndex({"timestamp": -1});

db.reputation_data.createIndex({"entity_value": 1});
db.reputation_data.createIndex({"entity_type": 1});

print("MongoDB initialization completed successfully");
"""
        
        with open('mongo-init.js', 'w') as f:
            f.write(mongo_init)
        
        print("✅ MongoDB initialization script created!")
    
    def build_docker_image(self):
        """Build Docker image"""
        print("🐳 Building Docker image...")
        
        try:
            subprocess.run([
                "docker", "build", "-t", "soc-correlation-engine:latest", "."
            ], check=True, capture_output=True)
            print("✅ Docker image built successfully!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker build failed: {e}")
            sys.exit(1)
    
    def deploy_services(self):
        """Deploy services using Docker Compose"""
        print("🚀 Deploying services...")
        
        try:
            # Stop existing services
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "down"
            ], capture_output=True)
            
            # Start services
            subprocess.run([
                "docker-compose", "-f", self.docker_compose_file, "up", "-d"
            ], check=True, capture_output=True)
            
            print("✅ Services deployed successfully!")
            
            # Wait for services to be ready
            print("⏳ Waiting for services to be ready...")
            time.sleep(30)
            
            # Check service health
            self.check_service_health()
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e}")
            sys.exit(1)
    
    def check_service_health(self):
        """Check health of deployed services"""
        print("🏥 Checking service health...")
        
        # Check SOC Engine
        try:
            import requests
            response = requests.get("http://localhost/health", timeout=10)
            if response.status_code == 200:
                print("✅ SOC Engine: Healthy")
            else:
                print(f"⚠️ SOC Engine: Status {response.status_code}")
        except Exception as e:
            print(f"❌ SOC Engine: Unreachable - {e}")
        
        # Check Database
        try:
            result = subprocess.run([
                "docker", "exec", "database", "mongo", "--eval", "db.adminCommand('ismaster')"
            ], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ MongoDB: Healthy")
            else:
                print("❌ MongoDB: Unhealthy")
        except Exception as e:
            print(f"❌ MongoDB: Unreachable - {e}")
        
        # Check Redis
        try:
            result = subprocess.run([
                "docker", "exec", "cache", "redis-cli", "ping"
            ], capture_output=True, text=True)
            if "PONG" in result.stdout:
                print("✅ Redis: Healthy")
            else:
                print("❌ Redis: Unhealthy")
        except Exception as e:
            print(f"❌ Redis: Unreachable - {e}")
    
    def setup_backup_cron(self):
        """Setup automated backup cron job"""
        print("💾 Setting up automated backup...")
        
        cron_job = f"""# SOC Engine Backup Script
# Run daily at 2 AM
0 2 * * * /usr/bin/python3 {os.getcwd()}/scripts/backup.py >> {self.backup_dir}/backup.log 2>&1

# Run weekly cleanup on Sunday at 3 AM
0 3 * * 0 /usr/bin/python3 {os.getcwd()}/scripts/cleanup.py >> {self.backup_dir}/cleanup.log 2>&1
"""
        
        with open('soc-engine.cron', 'w') as f:
            f.write(cron_job)
        
        # Install cron job
        subprocess.run([
            "crontab", "soc-engine.cron"
        ], check=True)
        
        print("✅ Backup cron job configured!")
    
    def create_deployment_summary(self):
        """Create deployment summary"""
        print("📋 Creating deployment summary...")
        
        summary = {
            "deployment_type": "Network-Based",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "services": {
                "soc_engine": {
                    "url": "https://localhost",
                    "status": "deployed"
                },
                "database": {
                    "type": "MongoDB",
                    "status": "deployed"
                },
                "cache": {
                    "type": "Redis",
                    "status": "deployed"
                },
                "proxy": {
                    "type": "Nginx",
                    "status": "deployed"
                }
            },
            "networks": {
                "dmz": "192.168.100.0/24",
                "internal": "192.168.2.0/24"
            },
            "next_steps": [
                "Access dashboard at https://localhost",
                "Configure firewall rules",
                "Set up monitoring",
                "Test with sample data"
            ]
        }
        
        with open('deployment_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("✅ Deployment summary created!")
        print("\n🎉 Network Deployment Summary:")
        print(json.dumps(summary, indent=2))
    
    def deploy(self):
        """Main deployment method"""
        print("🚀 Starting Network Deployment for World-Class SOC Correlation Engine")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        self.check_prerequisites()
        
        # Step 2: Create directory structure
        self.create_directories()
        
        # Step 3: Generate SSL certificates
        self.generate_ssl_certificates()
        
        # Step 4: Create configurations
        self.create_nginx_config()
        self.create_docker_compose()
        self.create_environment_file()
        self.create_mongo_init_script()
        
        # Step 5: Build Docker image
        self.build_docker_image()
        
        # Step 6: Deploy services
        self.deploy_services()
        
        # Step 7: Setup backup
        self.setup_backup_cron()
        
        # Step 8: Create summary
        self.create_deployment_summary()
        
        print("\n🎯 Deployment completed successfully!")
        print("🌐 Access your World-Class SOC Engine at: https://localhost")
        print("📊 Dashboard available at: https://localhost/dashboard")
        print("🔍 Health check at: https://localhost/health")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--network":
        deployment = NetworkDeployment()
        deployment.deploy()
    else:
        print("Usage: python deploy_network.py --network")
        print("This will deploy the SOC Engine in network mode")
        sys.exit(1)
