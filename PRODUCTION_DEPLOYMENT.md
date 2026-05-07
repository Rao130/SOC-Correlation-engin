# 🚀 SOC Correlation Engine - Quick Start & Deployment Guide

## Fast Deployment (Production Ready)

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (recommended)
- MongoDB 7.0+
- Redis 7.0+
- 4GB RAM, 2 CPU cores minimum

---

## Option 1: Docker Compose (Recommended - 5 minutes)

### Step 1: Clone & Configure
```bash
git clone https://github.com/Rao130/SOC-Correlation-engine.git
cd SOC-Correlation-engine

# Copy configuration template
cp .env.example .env

# Generate secure keys
python3 << 'EOF'
import secrets
secret = secrets.token_urlsafe(64)
encryption = secrets.token_urlsafe(64)
print(f"SECRET_KEY={secret}")
print(f"ENCRYPTION_MASTER_SECRET={encryption}")
EOF

# Update .env with generated keys
nano .env
```

### Step 2: Start Services
```bash
docker-compose up -d

# Verify all services running
docker-compose ps

# Check logs
docker-compose logs -f soc-engine
```

### Step 3: Verify Installation
```bash
# Health check
curl http://localhost:8001/health

# API documentation
open http://localhost:8001/api/docs
```

### Expected Output
```json
{
  "status": "healthy",
  "timestamp": "2026-04-29T12:00:00Z",
  "version": "2.0.0",
  "uptime_seconds": 45
}
```

---

## Option 2: Manual Installation (Development)

### Step 1: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download ML models
python -m spacy download en_core_web_sm
```

### Step 2: Start MongoDB & Redis
```bash
# MongoDB (Terminal 1)
mongod --dbpath ./data/mongodb --auth

# Redis (Terminal 2)
redis-server

# Setup MongoDB
mongo admin --eval 'db.createUser({user:"root",pwd:"password",roles:["root"]})'
```

### Step 3: Configure Application
```bash
cp .env.example .env
# Edit .env with your MongoDB and Redis credentials
```

### Step 4: Start Application
```bash
# Terminal 3
python main.py
```

---

## API Quick Reference

### Authentication

#### Login
```bash
curl -X POST "http://localhost:8001/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SecurePassword123!"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "expires_at": "2026-04-29T12:15:00Z"
}
```

#### Refresh Token
```bash
curl -X POST "http://localhost:8001/auth/refresh" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "refresh_token=<your-refresh-token>"
```

#### Logout
```bash
curl -X POST "http://localhost:8001/auth/logout" \
  -H "Authorization: Bearer <your-access-token>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=<your-access-token>"
```

### System Endpoints

#### Health Check
```bash
curl http://localhost:8001/health
```

#### System Status
```bash
curl -X GET "http://localhost:8001/api/status" \
  -H "Authorization: Bearer <token>"
```

#### Metrics (Prometheus)
```bash
curl http://localhost:8001/metrics
```

#### API Documentation
```
Browser: http://localhost:8001/api/docs
```

---

## Monitoring & Maintenance

### View Logs
```bash
# Docker
docker-compose logs -f soc-engine

# File-based
tail -f logs/soc_engine.log
```

### Prometheus Metrics

#### Key Metrics to Monitor
```bash
# Request rate
soc_http_requests_total{method="POST",endpoint="/alerts",status="success"}

# Error rate
soc_errors_total{error_type="http_error"}

# Rate limit violations
rate(soc_rate_limit_exceeded_total[5m])

# Request latency
histogram_quantile(0.95, soc_http_request_duration_seconds)
```

#### Setup Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'soc-engine'
    static_configs:
      - targets: ['localhost:8001']
```

```bash
# Run Prometheus
prometheus --config.file=prometheus.yml
```

### Database Maintenance

#### MongoDB Backup
```bash
# Backup
mongodump --uri="mongodb://root:password@localhost:27017/soc_correlation_engine" \
  --out=./backups/soc_$(date +%Y%m%d)

# Restore
mongorestore --uri="mongodb://root:password@localhost:27017" \
  ./backups/soc_20260429
```

#### Redis Persistence
```bash
# Redis persistence is automatically enabled
# Check backup file
ls -lh /var/lib/redis/dump.rdb

# Manual backup
redis-cli BGSAVE
```

---

## Production Deployment

### 1. Security Hardening

```bash
# Generate strong secrets
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(64))"
python3 -c "import secrets; print('ENCRYPTION_MASTER_SECRET=' + secrets.token_urlsafe(64))"

# Update .env with secure values
# DO NOT commit .env to git
echo ".env" >> .gitignore
```

### 2. SSL/TLS Setup

```bash
# Using Let's Encrypt
certbot certonly --standalone -d your-domain.com

# Update .env
SSL_CERTFILE=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEYFILE=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

### 3. Firewall Configuration

```bash
# Allow only necessary ports
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow 22/tcp

# Allow HTTPS (8001)
ufw allow 8001/tcp

# Allow HTTP (for redirect)
ufw allow 80/tcp

# Enable firewall
ufw enable
```

### 4. Database Security

```bash
# MongoDB authentication
db.createUser({
  user: "soc_app",
  pwd: "StrongPassword123!@#",
  roles: ["readWrite", "dbAdmin"]
})

# Redis password
requirepass StrongPassword123!@#
```

### 5. Reverse Proxy (Nginx)

```nginx
upstream soc_backend {
    server localhost:8001;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=100r/m;
    limit_req zone=general burst=50 nodelay;

    location / {
        proxy_pass http://soc_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Deny access to sensitive endpoints from outside
    location /api/admin {
        allow 10.0.0.0/8;  # Internal network only
        deny all;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 6. Process Management (systemd)

```ini
# /etc/systemd/system/soc-engine.service
[Unit]
Description=SOC Correlation Engine
After=network.target

[Service]
Type=simple
User=soc
WorkingDirectory=/home/soc/soc-correlation-engine
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/soc/soc-correlation-engine/.env
ExecStart=/home/soc/soc-correlation-engine/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable soc-engine
sudo systemctl start soc-engine

# Check status
sudo systemctl status soc-engine
```

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs soc-engine

# Verify environment variables
env | grep SECRET_KEY

# Test database connection
python3 -c "from pymongo import MongoClient; print(MongoClient('mongodb://localhost:27017'))"

# Test Redis connection
redis-cli ping
```

### High Memory Usage

```bash
# Check process
docker stats soc-engine

# Limit memory in docker-compose
services:
  soc-engine:
    mem_limit: 2g
    memswap_limit: 2g
```

### Rate Limiting Issues

```bash
# Reset rate limit counter
redis-cli FLUSHDB

# Check Redis memory
redis-cli INFO memory
```

---

## Performance Tuning

### Recommended Settings for Production

| Setting | Value | Notes |
|---------|-------|-------|
| Worker Processes | 4-8 | Based on CPU cores |
| Max Connections | 100 | Database connections |
| Request Timeout | 30s | API timeout |
| Cache TTL | 1 hour | Query caching |
| Log Level | INFO | Reduce verbosity |
| Batch Size | 100 | Alert processing |

### Load Testing

```bash
# Install load testing tool
pip install locust

# Create locustfile.py
from locust import HttpUser, task

class SOCUser(HttpUser):
    @task
    def health_check(self):
        self.client.get("/health")

# Run test
locust -f locustfile.py --host=http://localhost:8001
```

---

## Support & Maintenance

### Update Application
```bash
git pull origin main
pip install -r requirements.txt
docker-compose restart soc-engine
```

### Database Upgrade
```bash
# Backup first
mongodump --out=./backup_pre_upgrade

# Run migrations
alembic upgrade head
```

### Emergency Restart
```bash
docker-compose down
docker-compose up -d
```

---

## Checklist Before Production

- [ ] `.env` configured with strong secrets
- [ ] SSL/TLS certificates installed
- [ ] MongoDB authentication enabled
- [ ] Redis password configured
- [ ] Firewall rules configured
- [ ] Backups tested and working
- [ ] Monitoring/Prometheus running
- [ ] Audit logging enabled
- [ ] Rate limiting tested
- [ ] Documentation reviewed
- [ ] Security scan passed (bandit)
- [ ] Load test completed

---

**Last Updated:** April 29, 2026
**Version:** 2.0.0

