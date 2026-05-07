# 🐳 Docker Guide for SOC Correlation Engine

## 📋 Overview

This guide helps you deploy the SOC Correlation Engine using Docker Compose with all necessary services.

## ✅ Fixed Issues

The docker-compose.yml has been completely rewritten to fix:
- ❌ **Duplicate services** (mongo/mongodb, redis)
- ❌ **Syntax errors** and malformed YAML
- ❌ **Port conflicts** between services
- ❌ **Missing service dependencies**
- ❌ **Inconsistent naming** and configurations

## 🚀 Quick Start

### 1. Prerequisites
```bash
# Install Docker Desktop (Windows/Mac) or Docker Engine (Linux)
# Verify installation
docker --version
docker-compose --version  # or docker compose version
```

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values (optional for development)
nano .env
```

### 3. Start Services
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access Services
- **Main Application**: http://localhost:8000
- **Grafana Dashboard**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Kibana**: http://localhost:5601
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)
- **Consul UI**: http://localhost:8500
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379

## 📊 Services Architecture

### Core Services
| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **soc-engine** | 8000 | Main application | ✅ HTTP health |
| **mongodb** | 27017 | Primary database | ✅ MongoDB ping |
| **redis** | 6379 | Cache & sessions | ✅ Redis ping |

### Monitoring Services
| Service | Port | Purpose |
|---------|------|---------|
| **prometheus** | 9090 | Metrics collection |
| **grafana** | 3001 | Visualization dashboard |
| **elasticsearch** | N/A | Log storage |
| **kibana** | 5601 | Log visualization |

### Infrastructure Services
| Service | Port | Purpose |
|---------|------|---------|
| **rabbitmq** | 5672,15672 | Message broker |
| **consul** | 8500 | Service discovery |
| **nginx** | 80,443 | Load balancer |

## 🔧 Configuration

### Environment Variables
Key variables in `.env`:
```bash
# Application
APP_NAME="SOC Correlation Engine"
DEBUG=False
PORT=8000

# Security (IMPORTANT: Change in production!)
SECRET_KEY="your-super-secret-key-change-in-production"
ENCRYPTION_MASTER_SECRET="your-encryption-master-secret-change-in-production"

# Database
MONGO_PASSWORD="admin123"
REDIS_PASSWORD="admin123"

# Services
GRAFANA_PASSWORD="admin123"
RABBITMQ_USER="admin"
RABBITMQ_PASSWORD="admin123"
```

### Custom Configuration
```bash
# Build custom image
docker-compose build soc-engine

# Rebuild without cache
docker-compose build --no-cache soc-engine

# Scale services
docker-compose up -d --scale soc-engine=2
```

## 🛠️ Management Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart soc-engine

# View logs for specific service
docker-compose logs -f soc-engine
```

### Development Workflow
```bash
# Start with live code mounting
docker-compose up -d soc-engine

# View real-time logs
docker-compose logs -f soc-engine

# Rebuild after code changes
docker-compose up -d --build soc-engine

# Access container shell
docker-compose exec soc-engine bash
```

### Database Operations
```bash
# Access MongoDB
docker-compose exec mongodb mongosh -u admin -p admin123

# Access Redis
docker-compose exec redis redis-cli -a admin123

# Backup MongoDB
docker-compose exec mongodb mongodump --out /backup

# Restore MongoDB
docker-compose exec mongodb mongorestore /backup
```

## 🔍 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
netstat -tulpn | grep :8000

# Change ports in docker-compose.yml
ports:
  - "8001:8000"  # Use different host port
```

#### Service Won't Start
```bash
# Check logs
docker-compose logs service-name

# Check health status
docker-compose ps

# Force rebuild
docker-compose up -d --build --force-recreate service-name
```

#### Memory Issues
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### Network Issues
```bash
# Check network connectivity
docker-compose exec soc-engine ping mongodb

# Reset network
docker-compose down
docker network prune
docker-compose up -d
```

### Health Checks
```bash
# Check all service health
docker-compose ps

# Test main application
curl http://localhost:8000/health

# Test MongoDB connection
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Test Redis connection
docker-compose exec redis redis-cli -a admin123 ping
```

## 📈 Monitoring

### Prometheus Metrics
Access: http://localhost:9090
- Target: `soc-engine:8000/metrics`
- Custom SOC metrics included

### Grafana Dashboards
Access: http://localhost:3001
- Pre-configured dashboards
- Data source: Prometheus
- Login: admin/admin123

### Log Management
- **Elasticsearch**: Centralized log storage
- **Kibana**: Log visualization and search
- **File logging**: Also available in container logs

## 🔒 Security Considerations

### Production Deployment
```bash
# 1. Update all passwords in .env
# 2. Generate strong secrets
python -c "import secrets; print(secrets.token_urlsafe(64))"

# 3. Use HTTPS (configure SSL certificates)
# 4. Enable authentication
# 5. Configure firewall rules
# 6. Regular security updates
```

### Network Security
```bash
# Use custom network
networks:
  soc-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    internal: true  # Isolate from external
```

## 📝 Development Tips

### Hot Reloading
```yaml
# In docker-compose.yml
volumes:
  - ./app:/app/app  # Mount code for live updates
```

### Debug Mode
```bash
# Enable debug logging
echo "DEBUG=True" >> .env
docker-compose restart soc-engine
```

### Testing
```bash
# Run tests in container
docker-compose exec soc-engine python -m pytest

# Access development shell
docker-compose exec soc-engine bash
```

## 🚀 Production Deployment

### Performance Optimization
```yaml
# Resource limits
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

### High Availability
```bash
# Scale services
docker-compose up -d --scale soc-engine=3

# Use external database
# Update MONGODB_URL to external instance
```

### Backup Strategy
```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mongodb mongodump --out /backup_$DATE
docker-compose exec redis redis-cli --rdb /redis_backup_$DATE.rdb
```

## 🆘 Support

### Getting Help
```bash
# Check Docker version compatibility
docker --version
docker-compose version

# Validate configuration
python validate_docker_compose.py

# System diagnostics
docker-compose config
docker system info
```

### Common Debugging Commands
```bash
# Container inspection
docker-compose exec soc-engine env
docker-compose exec soc-engine ps aux

# Network inspection
docker network ls
docker network inspect soc_correlation_engine_soc-network

# Volume inspection
docker volume ls
docker volume inspect soc_correlation_engine_mongodb_data
```

---

**🎉 Your SOC Correlation Engine is now ready for Docker deployment!**

The docker-compose.yml has been completely fixed and validated. All services are properly configured with no conflicts or syntax errors.
