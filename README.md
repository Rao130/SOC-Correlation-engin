# SOC Correlation Engine

An industry-ready Security Operations Center (SOC) alert fatigue reduction system with advanced correlation, context analysis, reputation database, and criticality scoring.

## 🚀 Features

### Core Capabilities
- **Alert Fatigue Reduction**: Advanced algorithms to reduce alert fatigue and improve analyst efficiency
- **Multi-dimensional Correlation**: Entity-based, temporal, semantic, geographic, and behavioral correlation
- **Reputation Database**: Comprehensive entity reputation tracking with multiple threat intelligence sources
- **Criticality Scoring**: ML-powered criticality assessment for prioritized threat response
- **Real-time Dashboard**: Interactive web dashboard with live updates and geographic visualization
- **Context Analysis**: MITRE ATT&CK mapping and threat intelligence integration

### Technical Features
- **Python Backend**: FastAPI with async support for high-performance alert processing
- **Modern Frontend**: HTML/CSS/JavaScript with real-time WebSocket updates
- **Geospatial Analysis**: Interactive threat maps with geographic clustering
- **Machine Learning**: Anomaly detection and pattern recognition
- **Background Processing**: Async task processing for correlation and reputation checks
- **RESTful API**: Complete API for integration with existing security tools

## 📋 System Requirements

- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- Node.js (for development tools)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SOC_correlation_engine
```

### 2. Set Up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Databases
```bash
# Install MongoDB
# Install Redis
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Download GeoIP Database
```bash
# Download GeoLite2-City.mmdb from MaxMind
# Place in data/ directory
```

### 6. Install spaCy Model
```bash
python -m spacy download en_core_web_sm
```

## 🚀 Quick Start

### 1. Start the Backend
```bash
python main.py
```

### 2. Access the Dashboard
Open your browser and navigate to: `http://localhost:8000`

### 3. Create Sample Alerts
Use the API to create sample alerts:
```bash
curl -X POST "http://localhost:8000/api/alerts/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Suspicious Login Activity",
    "description": "Multiple failed login attempts detected",
    "severity": "high",
    "source": "authentication_system",
    "category": "intrusion",
    "confidence": 85,
    "entities": [
      {"type": "ip", "value": "192.168.1.100"},
      {"type": "user", "value": "admin"}
    ]
  }'
```

## 📊 Dashboard Features

### Main Dashboard
- **Real-time KPIs**: Active alerts, correlations, threat level
- **Alert Timeline**: Hour-by-hour alert trends
- **Threat Distribution**: Severity breakdown
- **Recent Alerts**: Latest security alerts with quick actions

### Alert Management
- **Advanced Filtering**: Search, severity, status, category filters
- **Alert Details**: Comprehensive alert information with entity analysis
- **Bulk Operations**: Mass status updates and assignments
- **Notes & Assignments**: Analyst collaboration tools

### Correlation Analysis
- **Correlation Groups**: Automatically grouped related alerts
- **Correlation Types**: Entity, temporal, semantic, geographic, behavioral
- **Confidence Scoring**: Reliability assessment for correlations
- **Interactive Investigation**: Deep dive into correlation details

### Reputation Database
- **Entity Tracking**: IP, domain, URL, hash, email reputation
- **Threat Intelligence**: Integration with VirusTotal, AbuseIPDB, OTX
- **Risk Scoring**: Aggregated reputation scores
- **Historical Analysis**: Entity behavior over time

### Geographic Visualization
- **Threat Maps**: Real-time geographic threat distribution
- **Cluster Analysis**: Geographic threat clustering
- **Location Intelligence**: Country, city, ASN analysis
- **Interactive Exploration**: Click-to-investigate map features

### Analytics & Insights
- **Fatigue Metrics**: Alert fatigue reduction statistics
- **Response Time Analysis**: Analyst performance metrics
- **Threat Evolution**: Trend analysis over time
- **Top Threat Actors**: Most active threat sources

## 🔧 Configuration

### Environment Variables
Key configuration options in `.env`:

```env
# Database
DATABASE_URL=mongodb://localhost:27017/soc_correlation_engine
REDIS_URL=redis://localhost:6379

# API Keys
VIRUSTOTAL_API_KEY=your_virustotal_api_key
ABUSEIPDB_API_KEY=your_abuseipdb_api_key
OTX_API_KEY=your_otx_api_key
SHODAN_API_KEY=your_shodan_api_key

# Alert Processing
ALERT_BATCH_SIZE=100
CORRELATION_TIME_WINDOW=3600000
CRITICALITY_THRESHOLD=7.5

# Background Tasks
BACKGROUND_TASK_INTERVAL=60
```

### Correlation Thresholds
Adjust correlation sensitivity in `app/services/correlation_engine.py`:

```python
self.entity_threshold = 0.7
self.temporal_threshold = 3600  # 1 hour
self.semantic_threshold = 0.6
self.geographic_threshold = 500  # 500 km
```

## 📡 API Documentation

### Alert Endpoints
- `POST /api/alerts/` - Create new alert
- `GET /api/alerts/` - Get alerts with filtering
- `GET /api/alerts/{id}` - Get specific alert
- `PATCH /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert

### Correlation Endpoints
- `GET /api/correlation/` - Get correlation groups
- `POST /api/correlation/analyze` - Run correlation analysis
- `GET /api/correlation/{id}` - Get correlation details

### Reputation Endpoints
- `GET /api/reputation/` - Get reputation data
- `POST /api/reputation/check` - Check entity reputation
- `GET /api/reputation/{entity}` - Get entity details

### Dashboard Endpoints
- `GET /api/stats` - System statistics
- `GET /api/dashboard/metrics` - Dashboard metrics
- `GET /api/api/maps/threats` - Geographic threat data

## 🔍 Advanced Features

### Alert Fatigue Reduction
- **Duplicate Detection**: Automatic identification of duplicate alerts
- **Suppression Rules**: Configurable alert suppression policies
- **Auto-resolution**: Machine learning-powered automatic resolution
- **Analyst Behavior Tracking**: Learn from analyst actions

### Machine Learning Integration
- **Anomaly Detection**: Unsupervised learning for pattern detection
- **Behavioral Analysis**: User and entity behavior modeling
- **Predictive Scoring**: Risk prediction based on historical data
- **Adaptive Thresholds**: Dynamic threshold adjustment

### Threat Intelligence Integration
- **VirusTotal**: Malware and URL reputation
- **AbuseIPDB**: IP address reputation
- **OTX (AlienVault)**: Open threat intelligence
- **Shodan**: Asset and service discovery

## 🧪 Testing

### Run Tests
```bash
pytest tests/
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Get system stats
curl http://localhost:8000/api/stats

# Create test alert
curl -X POST "http://localhost:8000/api/alerts/" \
  -H "Content-Type: application/json" \
  -d @test_alert.json
```

## 📈 Performance

### Optimization Features
- **Async Processing**: Non-blocking alert processing
- **Database Indexing**: Optimized queries for performance
- **Caching**: Redis caching for frequent queries
- **Batch Processing**: Efficient bulk operations

### Scaling Considerations
- **Horizontal Scaling**: Multiple worker processes
- **Database Sharding**: MongoDB sharding support
- **Load Balancing**: Application-level load balancing
- **Monitoring**: Performance metrics and health checks

## 🔒 Security

### Security Features
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: API rate limiting protection

### Security Best Practices
- **Environment Variables**: Secure configuration management
- **Database Security**: Encrypted connections and access control
- **API Security**: HTTPS enforcement and CORS configuration
- **Logging**: Comprehensive security event logging

## 🚀 Deployment

### Docker Deployment
```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

### Production Considerations
- **Reverse Proxy**: Nginx or Apache configuration
- **SSL/TLS**: HTTPS certificate setup
- **Monitoring**: Application and infrastructure monitoring
- **Backup**: Database backup and recovery procedures

## 📚 Documentation

### Code Structure
```
SOC_correlation_engine/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── core/               # Core configuration
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── static/                 # Frontend assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and icons
├── data/                   # Data files
├── logs/                   # Log files
├── tests/                  # Test files
└── main.py                 # Application entry point
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 🤝 Support

### Getting Help
- **Documentation**: Check this README and inline documentation
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join our security community discussions

### Troubleshooting
- **Database Connection**: Check MongoDB and Redis status
- **API Keys**: Verify external API key configuration
- **Logs**: Check application logs for error details
- **Performance**: Monitor system resources and database performance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database for alert storage
- **Redis**: In-memory data structure store
- **spaCy**: Natural language processing
- **scikit-learn**: Machine learning library
- **Leaflet**: Interactive maps
- **Chart.js**: Data visualization

---

**Built with ❤️ for the Security Community**
#   S O C - C o r r e l a t i o n - e n g i n  
 