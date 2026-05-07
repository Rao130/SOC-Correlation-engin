# 🔐 SOC Correlation Engine - Production Security Implementation Guide

## Executive Summary

This guide covers all security features implemented in the SOC Correlation Engine v2.0.0, designed to meet enterprise security requirements and compliance standards (SOC 2, ISO 27001, HIPAA).

---

## 📋 Table of Contents

1. [Security Architecture](#security-architecture)
2. [Authentication & Authorization](#authentication--authorization)
3. [Encryption](#encryption)
4. [Rate Limiting & DDoS Protection](#rate-limiting--ddos-protection)
5. [Audit & Logging](#audit--logging)
6. [Deployment Security](#deployment-security)
7. [Compliance & Standards](#compliance--standards)
8. [Incident Response](#incident-response)

---

## Security Architecture

### Layers of Security

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│  - Business logic, alert processing, correlation engine     │
├─────────────────────────────────────────────────────────────┤
│                 SECURITY MIDDLEWARE LAYER                   │
│  - JWT Authentication                                       │
│  - Rate Limiting & Burst Protection                         │
│  - Request Logging & Audit Trail                            │
├─────────────────────────────────────────────────────────────┤
│               ENCRYPTION & CRYPTO LAYER                     │
│  - AES-256 Field Encryption                                 │
│  - Data at Rest Encryption                                  │
│  - TLS 1.3 for Transport Security                           │
├─────────────────────────────────────────────────────────────┤
│              DATABASE & STORAGE LAYER                        │
│  - MongoDB with native encryption                           │
│  - Redis with ACL                                           │
│  - Encrypted backups                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Authentication & Authorization

### 1. JWT Token Authentication

#### Features
- ✅ **15-minute access tokens** - Short-lived, frequent rotation
- ✅ **7-day refresh tokens** - Secure token refresh flow
- ✅ **Token rotation** - Prevents token reuse attacks
- ✅ **JTI (JWT ID)** - Unique token identifier for revocation
- ✅ **Secure claims** - User ID, role, permissions, IP address, user agent

#### Implementation

```python
from app.core.auth_enhanced import get_auth_provider

auth = get_auth_provider()

# Login
token_response = auth.authenticate_user(
    username="analyst@soc.local",
    password="SecurePassword123!",
    user_db=user_database,
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0..."
)

# Get tokens
access_token = token_response.access_token
refresh_token = token_response.refresh_token

# Verify token
payload = auth.verify_access_token(access_token)

# Refresh token
new_tokens = auth.refresh_token(refresh_token, user_data)

# Logout (revoke token)
auth.logout(access_token, user_id)
```

#### API Usage

**Login:**
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=analyst&password=SecurePassword123!
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 900,
  "expires_at": "2026-04-29T12:15:00Z"
}
```

**Use Token:**
```bash
GET /api/alerts
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 2. Role-Based Access Control (RBAC)

#### Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | read, write, admin | System administration |
| **Analyst** | read, write | Alert analysis, correlation review |
| **Viewer** | read | Dashboard viewing, read-only access |
| **Service** | service-specific | API-to-API authentication |

#### Implementation

```python
# Define user permissions
USER_DATA = {
    "analyst@soc.local": {
        "role": "analyst",
        "permissions": ["read", "write", "export"],
        "allowed_endpoints": ["/alerts", "/correlations", "/reports"]
    }
}

# Check permissions
if "write" not in user_permissions:
    raise HTTPException(status_code=403, detail="Permission denied")
```

### 3. Password Security

#### Requirements
- **Minimum 12 characters**
- **1 uppercase letter** (A-Z)
- **1 lowercase letter** (a-z)
- **1 digit** (0-9)
- **1 special character** (!@#$%^&*)

#### Implementation

```python
from app.core.auth_enhanced import PasswordManager

pm = PasswordManager()

# Hash password (use during registration)
hashed = pm.hash_password("SecurePassword123!")

# Verify password (use during login)
is_valid = pm.verify_password("SecurePassword123!", hashed)

# Validate password strength
is_strong, message = pm.validate_password_strength("MyPassword@2024")
```

---

## Encryption

### 1. Data at Rest (Database)

#### AES-256 Field-Level Encryption

**Sensitive Fields Encrypted:**
- Passwords
- API keys
- Tokens
- Credit card information
- Social security numbers
- Email addresses (configurable)

#### Implementation

```python
from app.core.encryption import get_encryption_services

encryption = get_encryption_services()
doc_encryptor = encryption["document_encryptor"]

# Encrypt sensitive fields
document = {
    "user_id": "user_123",
    "email": "analyst@soc.local",
    "api_key": "sk_live_abcd1234"
}

encrypted_doc = doc_encryptor.encrypt_document(document)
# Original sensitive fields set to null, encrypted versions stored

# Decrypt when needed
decrypted_doc = doc_encryptor.decrypt_document(encrypted_doc)
```

#### Key Rotation

```python
key_manager = encryption["key_manager"]

# Current key version
version = key_manager.get_key_version()

# Rotate to new key
new_key = key_manager.rotate_key()

# Old data automatically decrypted and re-encrypted with new key
```

### 2. Data in Transit (TLS 1.3)

#### Configuration

```ini
# .env
SSL_CERTFILE=/etc/ssl/certs/server.crt
SSL_KEYFILE=/etc/ssl/private/server.key
```

#### HTTPS Setup

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use with Uvicorn
uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

#### Strict Headers

All responses include security headers:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
```

---

## Rate Limiting & DDoS Protection

### 1. IP-Based Rate Limiting

**Limit:** 100 requests per 60 seconds per IP address

#### Response Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1714404900
```

#### Implementation

```python
from app.core.rate_limiting import IpBasedRateLimiter

limiter = IpBasedRateLimiter()

allowed, info = await limiter.check_ip_limit(
    ip_address="192.168.1.100",
    limit=100,
    window_seconds=60
)

if not allowed:
    raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

### 2. Burst Protection (DDoS Detection)

**Threshold:** 50 requests in 10 seconds triggers 5-minute cooldown

#### Implementation

```python
from app.core.rate_limiting import BurstProtector

burst_detector = BurstProtector()

is_safe, message = await burst_detector.check_burst(f"burst:{ip_address}")
if not is_safe:
    raise HTTPException(status_code=429, detail=message)
```

### 3. Brute Force Protection

**Security:**
- **Max 5 failed login attempts**
- **15-minute account lockout**
- **Audit logging of all attempts**
- **IP-based tracking**

#### Implementation

```python
from app.core.rate_limiting import LoginAttemptTracker

tracker = LoginAttemptTracker()

# Record failed attempt
info = await tracker.record_failed_attempt(
    username="analyst",
    ip_address="192.168.1.100"
)

if info["locked"]:
    raise HTTPException(status_code=429, detail="Account locked")

# Reset on successful login
await tracker.reset_attempts(username, ip_address)
```

---

## Audit & Logging

### 1. Comprehensive Audit Logging

#### Events Logged

| Event | Details | Severity |
|-------|---------|----------|
| LOGIN_ATTEMPT | Username, IP, success/failure, reason | INFO/WARN |
| TOKEN_REVOCATION | User ID, JTI, reason, timestamp | INFO |
| PERMISSION_CHANGE | User, old/new perms, changed by | WARN |
| DATA_ENCRYPTION | Field, key version, timestamp | INFO |
| RATE_LIMIT_EXCEEDED | IP, endpoint, limit exceeded | WARN |
| ERROR | Error type, endpoint, stack trace | ERROR |

#### Implementation

```python
from app.core.auth_enhanced import AuditLogger

audit = AuditLogger()

# Log login attempt
audit.log_login_attempt(
    username="analyst",
    success=True,
    ip_address="192.168.1.100"
)

# Log token revocation
audit.log_token_revocation(
    user_id="user_123",
    jti="abc123def456",
    reason="User logout"
)

# Log permission changes
audit.log_permission_change(
    user_id="user_456",
    old_permissions=["read"],
    new_permissions=["read", "write"],
    changed_by="admin"
)
```

### 2. Log Aggregation

#### Log Format

```json
{
  "timestamp": "2026-04-29T12:00:00Z",
  "level": "WARNING",
  "event_type": "RATE_LIMIT_EXCEEDED",
  "source": "RateLimiter",
  "ip_address": "192.168.1.100",
  "user_id": "user_123",
  "endpoint": "/api/alerts",
  "limit": 100,
  "current_count": 101,
  "message": "Rate limit exceeded"
}
```

#### Log Files

```
logs/
├── soc_engine.log           # All application logs
├── soc_engine.log.1         # Rotated logs
├── soc_engine.log.2
└── soc_engine.log.10        # 10 files max, 10MB each
```

### 3. Sensitive Data Masking

Prevents accidental exposure of secrets in logs:

```python
from app.core.encryption import SensitiveDataMasker

masker = SensitiveDataMasker()

# Mask individual strings
masked = masker.mask_string("sk_live_abcd1234")  # Returns: sk_l...d34

# Mask dictionary
data = {"api_key": "secret_value", "name": "John"}
masked = masker.mask_dict(data, ["api_key"])
```

---

## Deployment Security

### 1. Environment Configuration

#### Generate Secrets

```bash
# Generate SECRET_KEY (64+ characters)
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Generate ENCRYPTION_MASTER_SECRET
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

#### .env Setup

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Secure permissions
chmod 600 .env
```

### 2. Docker Deployment

#### Dockerfile Security

```dockerfile
FROM python:3.11-slim

# Don't run as root
RUN groupadd -r soc && useradd -r -g soc soc

# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app /app

# Use non-root user
USER soc

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

CMD ["python", "main.py"]
```

#### Docker Compose Security

```yaml
version: '3.9'

services:
  soc-engine:
    build: .
    ports:
      - "8001:8001"
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - ENCRYPTION_MASTER_SECRET=${ENCRYPTION_MASTER_SECRET}
      - MONGODB_URL=mongodb://mongo:27017
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - soc-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mongo:
    image: mongo:7.0
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_ROOT_USER}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_ROOT_PASSWORD}
    networks:
      - soc-network
    command: --auth

  redis:
    image: redis:7.0-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - soc-network

volumes:
  mongo_data:

networks:
  soc-network:
    driver: bridge
```

### 3. HTTPS Configuration

```bash
# Using Let's Encrypt (Certbot)
certbot certonly --standalone -d your-domain.com

# Point to certificates
export SSL_CERTFILE=/etc/letsencrypt/live/your-domain.com/fullchain.pem
export SSL_KEYFILE=/etc/letsencrypt/live/your-domain.com/privkey.pem
```

---

## Compliance & Standards

### SOC 2 Type II Checklist

- [x] Security: JWT auth, encryption, rate limiting
- [x] Availability: Health checks, monitoring, logging
- [x] Processing Integrity: Audit trails, error handling
- [x] Confidentiality: AES-256 encryption, TLS 1.3
- [x] Privacy: Sensitive data masking, audit logs

### ISO 27001 Alignment

- [x] Access Control: RBAC, authentication, authorization
- [x] Cryptography: AES-256, PBKDF2, TLS 1.3
- [x] Audit & Accountability: Comprehensive logging
- [x] Incident Management: Error handling, alerts

### HIPAA Compliance (Healthcare)

```python
# Additional HIPAA requirements
HIPAA_REQUIREMENTS = {
    "encryption_at_rest": "AES-256",
    "encryption_in_transit": "TLS 1.3",
    "access_control": "RBAC",
    "audit_logging": "All access logged",
    "data_retention": "Configurable",
    "breach_notification": "Automated alerts"
}
```

---

## Incident Response

### 1. Detecting Security Issues

#### Prometheus Alerts

```yaml
groups:
- name: security
  rules:
  - alert: RateLimitExceeded
    expr: rate(soc_rate_limit_exceeded_total[5m]) > 10
    annotations:
      summary: "High rate of rate limit violations"
  
  - alert: BruteForceDetected
    expr: rate(soc_login_failures_total[5m]) > 5
    annotations:
      summary: "Brute force attack detected"
  
  - alert: HighErrorRate
    expr: rate(soc_errors_total[5m]) > 0.1
    annotations:
      summary: "High application error rate"
```

### 2. Response Procedures

#### Rate Limit Violation
1. Check `/metrics` for source IP
2. Add to temporary blacklist
3. Review logs for pattern
4. Contact network team if DDoS suspected

#### Brute Force Attack
1. Automatically locks account (15 min)
2. Sends alert to security team
3. Reviews failed attempt patterns
4. May trigger IP block

#### Encryption Key Compromise
1. Immediately rotate keys: `key_manager.rotate_key()`
2. Re-encrypt all sensitive data
3. Audit data access logs
4. Notify users (HIPAA requirement)

### 3. Emergency Procedures

```bash
# Revoke all tokens in case of compromise
redis-cli FLUSHALL

# Rotate encryption keys
python -c "from app.core.encryption import KeyManager; km = KeyManager('secret'); km.rotate_key()"

# Check audit logs for suspicious activity
tail -f logs/soc_engine.log | grep "AUTHENTICATION\|AUTHORIZATION"

# Force restart application
supervisorctl restart soc_engine
```

---

## Testing Security

### Unit Tests

```python
# test_auth.py
def test_password_validation():
    from app.core.auth_enhanced import PasswordManager
    
    pm = PasswordManager()
    is_strong, msg = pm.validate_password_strength("weak")
    assert not is_strong

def test_token_expiration():
    auth = get_auth_provider()
    token, _ = auth.jwt_manager.create_token_pair(...)
    
    # Wait for expiration
    time.sleep(auth.jwt_manager.access_token_expire.total_seconds() + 1)
    
    payload = auth.verify_token(token)
    assert payload is None  # Expired
```

### Security Scanning

```bash
# OWASP dependency check
pip install safety
safety check

# Bandit security analysis
pip install bandit
bandit -r app/

# SAST scanning
pip install semgrep
semgrep --config=p/security-audit app/
```

---

## Support & Questions

For security vulnerabilities, please report to: **security@soc-engine.local**

For implementation help, contact: **support@soc-engine.local**

---

**Last Updated:** April 29, 2026
**Version:** 2.0.0
**Status:** Production-Ready ✅

