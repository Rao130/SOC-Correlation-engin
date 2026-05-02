"""
Advanced Monitoring and Alerting for SOC Correlation Engine
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import time
import psutil
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MonitoringType(Enum):
    SYSTEM_HEALTH = "system_health"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    COMPLIANCE = "compliance"

class NotificationChannel(Enum):
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

@dataclass
class MonitoringMetric:
    """Monitoring metric definition"""
    name: str
    type: MonitoringType
    description: str
    calculation_method: str
    thresholds: Dict[str, float] = field(default_factory=dict)
    unit: Optional[str] = None
    collection_interval: int = 60  # seconds

@dataclass
class AlertRule:
    """Alert rule definition"""
    name: str
    description: str
    metric: str
    condition: str  # gt, lt, eq, rate
    threshold: float
    severity: AlertSeverity
    channels: List[NotificationChannel]
    cooldown: int = 300  # seconds
    enabled: bool = True

class AdvancedMonitoringEngine:
    """Advanced monitoring and alerting engine"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.metrics = {}
        self.alert_rules = {}
        self.notification_channels = {}
        self.metric_history = defaultdict(lambda: deque(maxlen=1000))
        self.alert_history = deque(maxlen=10000)
        self.active_alerts = {}
        self.system_start_time = time.time()
        
    async def initialize_monitoring(self):
        """Initialize monitoring engine"""
        await self._setup_metrics()
        await self._setup_alert_rules()
        await self._setup_notification_channels()
        logger.info("Advanced monitoring engine initialized")
    
    async def _setup_metrics(self):
        """Setup monitoring metrics"""
        self.metrics = {
            MonitoringType.SYSTEM_HEALTH: [
                MonitoringMetric(
                    name="cpu_usage",
                    type=MonitoringType.SYSTEM_HEALTH,
                    description="CPU utilization percentage",
                    calculation_method="psutil_cpu_percent",
                    thresholds={"warning": 70, "critical": 90},
                    unit="percent",
                    collection_interval=30
                ),
                MonitoringMetric(
                    name="memory_usage",
                    type=MonitoringType.SYSTEM_HEALTH,
                    description="Memory utilization percentage",
                    calculation_method="psutil_memory_percent",
                    thresholds={"warning": 80, "critical": 95},
                    unit="percent",
                    collection_interval=30
                ),
                MonitoringMetric(
                    name="disk_usage",
                    type=MonitoringType.SYSTEM_HEALTH,
                    description="Disk utilization percentage",
                    calculation_method="psutil_disk_percent",
                    thresholds={"warning": 80, "critical": 95},
                    unit="percent",
                    collection_interval=60
                ),
                MonitoringMetric(
                    name="gpu_usage",
                    type=MonitoringType.SYSTEM_HEALTH,
                    description="GPU utilization percentage",
                    calculation_method="psutil_gpu_percent",
                    thresholds={"warning": 70, "critical": 90},
                    unit="percent",
                    collection_interval=30
                )
            ],
            MonitoringType.PERFORMANCE: [
                MonitoringMetric(
                    name="api_response_time",
                    type=MonitoringType.PERFORMANCE,
                    description="API response time in milliseconds",
                    calculation_method="api_metrics",
                    thresholds={"warning": 500, "critical": 2000},
                    unit="ms",
                    collection_interval=60
                ),
                MonitoringMetric(
                    name="throughput",
                    type=MonitoringType.PERFORMANCE,
                    description="Alerts processed per second",
                    calculation_method="alert_processing_metrics",
                    thresholds={"warning": 10, "critical": 5},
                    unit="alerts/sec",
                    collection_interval=60
                ),
                MonitoringMetric(
                    name="error_rate",
                    type=MonitoringType.PERFORMANCE,
                    description="Error rate percentage",
                    calculation_method="error_rate_calculation",
                    thresholds={"warning": 5, "critical": 15},
                    unit="percent",
                    collection_interval=60
                )
            ],
            MonitoringType.SECURITY: [
                MonitoringMetric(
                    name="failed_logins",
                    type=MonitoringType.SECURITY,
                    description="Number of failed login attempts",
                    calculation_method="security_event_count",
                    thresholds={"warning": 10, "critical": 50},
                    unit="count",
                    collection_interval=60
                ),
                MonitoringMetric(
                    name="suspicious_activities",
                    type=MonitoringType.SECURITY,
                    description="Suspicious security activities",
                    calculation_method="threat_detection_metrics",
                    thresholds={"warning": 5, "critical": 20},
                    unit="count",
                    collection_interval=60
                ),
                MonitoringMetric(
                    name="data_exfiltration_attempts",
                    type=MonitoringType.SECURITY,
                    description="Data exfiltration attempts",
                    calculation_method="data_loss_metrics",
                    thresholds={"warning": 1, "critical": 5},
                    unit="count",
                    collection_interval=30
                )
            ],
            MonitoringType.BUSINESS: [
                MonitoringMetric(
                    name="active_users",
                    type=MonitoringType.BUSINESS,
                    description="Number of active users",
                    calculation_method="user_activity_metrics",
                    thresholds={"warning": 1, "critical": 0},
                    unit="count",
                    collection_interval=300
                ),
                MonitoringMetric(
                    name="system_uptime",
                    type=MonitoringType.BUSINESS,
                    description="System uptime percentage",
                    calculation_method="uptime_calculation",
                    thresholds={"warning": 99, "critical": 95},
                    unit="percent",
                    collection_interval=60
                )
            ]
        }
    
    async def _setup_alert_rules(self):
        """Setup alert rules"""
        self.alert_rules = {
            "high_cpu_usage": AlertRule(
                name="High CPU Usage",
                description="CPU usage exceeds threshold",
                metric="cpu_usage",
                condition="gt",
                threshold=80,
                severity=AlertSeverity.WARNING,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown=300
            ),
            "critical_cpu_usage": AlertRule(
                name="Critical CPU Usage",
                description="CPU usage exceeds critical threshold",
                metric="cpu_usage",
                condition="gt",
                threshold=95,
                severity=AlertSeverity.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
                cooldown=60
            ),
            "high_memory_usage": AlertRule(
                name="High Memory Usage",
                description="Memory usage exceeds threshold",
                metric="memory_usage",
                condition="gt",
                threshold=85,
                severity=AlertSeverity.WARNING,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown=300
            ),
            "api_response_slow": AlertRule(
                name="Slow API Response",
                description="API response time exceeds threshold",
                metric="api_response_time",
                condition="gt",
                threshold=1000,
                severity=AlertSeverity.WARNING,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD],
                cooldown=300
            ),
            "high_error_rate": AlertRule(
                name="High Error Rate",
                description="Error rate exceeds threshold",
                metric="error_rate",
                condition="gt",
                threshold=10,
                severity=AlertSeverity.ERROR,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK],
                cooldown=180
            ),
            "security_breach": AlertRule(
                name="Security Breach Detected",
                description="Security breach or compromise detected",
                metric="suspicious_activities",
                condition="gt",
                threshold=10,
                severity=AlertSeverity.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                cooldown=60
            ),
            "system_down": AlertRule(
                name="System Down",
                description="System is not responding",
                metric="system_uptime",
                condition="lt",
                threshold=90,
                severity=AlertSeverity.CRITICAL,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.SLACK],
                cooldown=30
            )
        }
    
    async def _setup_notification_channels(self):
        """Setup notification channels"""
        self.notification_channels = {
            NotificationChannel.EMAIL: {
                "enabled": True,
                "config": {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "alerts@yourcompany.com",
                    "password": "your_app_password",
                    "recipients": ["admin@yourcompany.com", "security-team@yourcompany.com"]
                }
            },
            NotificationChannel.SMS: {
                "enabled": True,
                "config": {
                    "provider": "twilio",
                    "account_sid": "your_account_sid",
                    "auth_token": "your_auth_token",
                    "from_number": "+1234567890",
                    "recipients": ["+1234567890", "+0987654321"]
                }
            },
            NotificationChannel.SLACK: {
                "enabled": True,
                "config": {
                    "webhook_url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                    "channel": "#security-alerts",
                    "username": "SOC Bot"
                }
            },
            NotificationChannel.WEBHOOK: {
                "enabled": True,
                "config": {
                    "url": "https://your-siemsystem.com/webhooks/alerts",
                    "headers": {"Authorization": "Bearer your_token"},
                    "timeout": 30
                }
            }
        }
    
    async def start_monitoring_loop(self):
        """Start the main monitoring loop"""
        logger.info("Starting advanced monitoring loop")
        
        while True:
            try:
                # Collect all metrics
                await self._collect_all_metrics()
                
                # Evaluate alert rules
                await self._evaluate_alert_rules()
                
                # Update dashboards
                await self._update_dashboards()
                
                # Cleanup old data
                await self._cleanup_old_data()
                
                # Wait for next collection interval
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_all_metrics(self):
        """Collect all monitoring metrics"""
        timestamp = datetime.utcnow()
        
        for metric_type, metric_list in self.metrics.items():
            for metric in metric_list:
                try:
                    value = await self._collect_metric_value(metric)
                    if value is not None:
                        # Store metric value
                        metric_data = {
                            "timestamp": timestamp.isoformat(),
                            "metric_name": metric.name,
                            "metric_type": metric.type.value,
                            "value": value,
                            "unit": metric.unit,
                            "thresholds": metric.thresholds
                        }
                        
                        # Store in history
                        self.metric_history[metric.name].append(metric_data)
                        
                        # Store in database
                        await self._store_metric_in_db(metric_data)
                        
                except Exception as e:
                    logger.error(f"Error collecting metric {metric.name}: {e}")
    
    async def _collect_metric_value(self, metric: MonitoringMetric) -> Optional[float]:
        """Collect value for a specific metric"""
        if metric.calculation_method == "psutil_cpu_percent":
            return psutil.cpu_percent(interval=1)
        elif metric.calculation_method == "psutil_memory_percent":
            return psutil.virtual_memory().percent
        elif metric.calculation_method == "psutil_disk_percent":
            return psutil.disk_usage('/').percent
        elif metric.calculation_method == "psutil_gpu_percent":
            try:
                # Use psutil for GPU monitoring (fallback to CPU if no GPU)
                if hasattr(psutil, 'gpu'):
                    gpus = psutil.gpu()
                    if gpus:
                        return sum(gpu.load * 100 for gpu in gpus) / len(gpus)
                else:
                    # Fallback to CPU if GPU monitoring not available
                    return psutil.cpu_percent(interval=1)
            except:
                return None
        elif metric.calculation_method == "api_metrics":
            return await self._get_api_response_time()
        elif metric.calculation_method == "alert_processing_metrics":
            return await self._get_alert_throughput()
        elif metric.calculation_method == "error_rate_calculation":
            return await self._calculate_error_rate()
        elif metric.calculation_method == "security_event_count":
            return await self._count_security_events("failed_login")
        elif metric.calculation_method == "threat_detection_metrics":
            return await self._count_threat_events()
        elif metric.calculation_method == "data_loss_metrics":
            return await self._count_data_exfiltration_attempts()
        elif metric.calculation_method == "user_activity_metrics":
            return await self._count_active_users()
        elif metric.calculation_method == "uptime_calculation":
            return await self._calculate_uptime()
        else:
            return None
    
    async def _get_api_response_time(self) -> float:
        """Get API response time"""
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/health", timeout=10)
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
        except:
            return 5000  # High value indicating failure
    
    async def _get_alert_throughput(self) -> float:
        """Get alert processing throughput"""
        try:
            # Get recent alerts from database
            alerts_collection = self.db.get_collection("alerts")
            one_minute_ago = datetime.utcnow() - timedelta(minutes=1)
            recent_alerts = await alerts_collection.count_documents({
                "timestamp": {"$gte": one_minute_ago.isoformat()}
            })
            return recent_alerts / 60.0  # Per second
        except:
            return 0.0
    
    async def _calculate_error_rate(self) -> float:
        """Calculate error rate"""
        try:
            # Mock calculation - in production, use actual error logs
            total_requests = 1000
            error_requests = 50
            return (error_requests / total_requests) * 100
        except:
            return 0.0
    
    async def _count_security_events(self, event_type: str) -> int:
        """Count security events of specific type"""
        try:
            alerts_collection = self.db.get_collection("alerts")
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            count = await alerts_collection.count_documents({
                "category": event_type,
                "timestamp": {"$gte": one_hour_ago.isoformat()}
            })
            return count
        except:
            return 0
    
    async def _count_threat_events(self) -> int:
        """Count threat events"""
        try:
            alerts_collection = self.db.get_collection("alerts")
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            count = await alerts_collection.count_documents({
                "severity": {"$in": ["high", "critical"]},
                "timestamp": {"$gte": one_hour_ago.isoformat()}
            })
            return count
        except:
            return 0
    
    async def _count_data_exfiltration_attempts(self) -> int:
        """Count data exfiltration attempts"""
        try:
            alerts_collection = self.db.get_collection("alerts")
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            count = await alerts_collection.count_documents({
                "category": {"$in": ["data_exfiltration", "data_breach"]},
                "timestamp": {"$gte": one_hour_ago.isoformat()}
            })
            return count
        except:
            return 0
    
    async def _count_active_users(self) -> int:
        """Count active users"""
        try:
            # Mock implementation - in production, use actual user tracking
            return 25
        except:
            return 0
    
    async def _calculate_uptime(self) -> float:
        """Calculate system uptime"""
        try:
            uptime_seconds = time.time() - self.system_start_time
            total_seconds = 24 * 60 * 60  # 24 hours in seconds
            return (uptime_seconds / total_seconds) * 100
        except:
            return 0.0
    
    async def _store_metric_in_db(self, metric_data: Dict):
        """Store metric data in database"""
        try:
            metrics_collection = self.db.get_collection("monitoring_metrics")
            await metrics_collection.insert_one(metric_data)
        except Exception as e:
            logger.error(f"Error storing metric in database: {e}")
    
    async def _evaluate_alert_rules(self):
        """Evaluate all alert rules"""
        timestamp = datetime.utcnow()
        
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            try:
                # Check cooldown
                if rule_name in self.active_alerts:
                    last_alert_time = self.active_alerts[rule_name]["timestamp"]
                    if (timestamp - last_alert_time).total_seconds() < rule.cooldown:
                        continue
                
                # Get current metric value
                current_value = await self._get_current_metric_value(rule.metric)
                if current_value is None:
                    continue
                
                # Evaluate rule condition
                should_alert = await self._evaluate_condition(
                    current_value, rule.condition, rule.threshold
                )
                
                if should_alert:
                    # Create alert
                    alert = {
                        "rule_name": rule_name,
                        "metric": rule.metric,
                        "current_value": current_value,
                        "threshold": rule.threshold,
                        "condition": rule.condition,
                        "severity": rule.severity.value,
                        "description": rule.description,
                        "timestamp": timestamp.isoformat(),
                        "channels": [channel.value for channel in rule.channels]
                    }
                    
                    # Send notifications
                    await self._send_notifications(alert, rule.channels)
                    
                    # Store alert
                    self.alert_history.append(alert)
                    self.active_alerts[rule_name] = alert
                    
                    logger.warning(f"Alert triggered: {rule_name} - {rule.description}")
                
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_name}: {e}")
    
    async def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a metric"""
        if metric_name in self.metric_history and self.metric_history[metric_name]:
            return self.metric_history[metric_name][-1]["value"]
        return None
    
    async def _evaluate_condition(self, current_value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == "gt":
            return current_value > threshold
        elif condition == "lt":
            return current_value < threshold
        elif condition == "eq":
            return current_value == threshold
        elif condition == "rate":
            # Rate-based condition (e.g., rate of change)
            return False  # Implement rate logic as needed
        return False
    
    async def _send_notifications(self, alert: Dict, channels: List[NotificationChannel]):
        """Send notifications through specified channels"""
        for channel in channels:
            try:
                if channel == NotificationChannel.EMAIL:
                    await self._send_email_notification(alert)
                elif channel == NotificationChannel.SMS:
                    await self._send_sms_notification(alert)
                elif channel == NotificationChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == NotificationChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                elif channel == NotificationChannel.DASHBOARD:
                    await self._update_dashboard_alert(alert)
            except Exception as e:
                logger.error(f"Error sending notification via {channel.value}: {e}")
    
    async def _send_email_notification(self, alert: Dict):
        """Send email notification"""
        config = self.notification_channels[NotificationChannel.EMAIL]["config"]
        
        subject = f"[{alert['severity'].upper()}] SOC Alert: {alert['rule_name']}"
        body = f"""
SOC Correlation Engine Alert

Alert Details:
- Rule: {alert['rule_name']}
- Description: {alert['description']}
- Metric: {alert['metric']}
- Current Value: {alert['current_value']}
- Threshold: {alert['threshold']}
- Condition: {alert['condition']}
- Severity: {alert['severity']}
- Time: {alert['timestamp']}

Please investigate this alert immediately.

Best regards,
SOC Team
"""
        
        try:
            msg = MIMEMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for {alert['rule_name']}")
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
    
    async def _send_sms_notification(self, alert: Dict):
        """Send SMS notification"""
        config = self.notification_channels[NotificationChannel.SMS]["config"]
        
        message = f"SOC Alert: {alert['rule_name']} - {alert['description']}"
        
        try:
            # Mock SMS implementation - integrate with actual SMS provider
            logger.info(f"SMS notification sent: {message}")
        except Exception as e:
            logger.error(f"Error sending SMS notification: {e}")
    
    async def _send_slack_notification(self, alert: Dict):
        """Send Slack notification"""
        config = self.notification_channels[NotificationChannel.SLACK]["config"]
        
        payload = {
            "channel": config['channel'],
            "username": config['username'],
            "text": f"🚨 *{alert['severity'].upper()}* SOC Alert: {alert['rule_name']}",
            "attachments": [
                {
                    "color": "danger" if alert['severity'] == 'critical' else "warning",
                    "fields": [
                        {"title": "Description", "value": alert['description'], "short": False},
                        {"title": "Metric", "value": alert['metric'], "short": True},
                        {"title": "Current Value", "value": str(alert['current_value']), "short": True},
                        {"title": "Threshold", "value": str(alert['threshold']), "short": True}
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(config['webhook_url'], json=payload, timeout=10)
            if response.status_code == 200:
                logger.info(f"Slack notification sent for {alert['rule_name']}")
            else:
                logger.error(f"Slack notification failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
    
    async def _send_webhook_notification(self, alert: Dict):
        """Send webhook notification"""
        config = self.notification_channels[NotificationChannel.WEBHOOK]["config"]
        
        payload = {
            "alert_type": "soc_correlation_engine",
            "alert": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            response = requests.post(
                config['url'],
                json=payload,
                headers=config['headers'],
                timeout=config['timeout']
            )
            if response.status_code == 200:
                logger.info(f"Webhook notification sent for {alert['rule_name']}")
            else:
                logger.error(f"Webhook notification failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending webhook notification: {e}")
    
    async def _update_dashboard_alert(self, alert: Dict):
        """Update dashboard with alert"""
        try:
            # Store alert for dashboard display
            dashboard_collection = self.db.get_collection("dashboard_alerts")
            await dashboard_collection.insert_one(alert)
            logger.info(f"Dashboard alert updated for {alert['rule_name']}")
        except Exception as e:
            logger.error(f"Error updating dashboard alert: {e}")
    
    async def _update_dashboards(self):
        """Update monitoring dashboards"""
        try:
            # Prepare dashboard data
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_health": await self._get_system_health_summary(),
                "performance_metrics": await self._get_performance_summary(),
                "security_metrics": await self._get_security_summary(),
                "active_alerts": list(self.active_alerts.values()),
                "recent_alerts": list(self.alert_history)[-10:]
            }
            
            # Store dashboard data
            dashboard_collection = self.db.get_collection("dashboard_data")
            await dashboard_collection.insert_one(dashboard_data)
            
        except Exception as e:
            logger.error(f"Error updating dashboards: {e}")
    
    async def _get_system_health_summary(self) -> Dict:
        """Get system health summary"""
        health_metrics = {}
        
        for metric_name in ["cpu_usage", "memory_usage", "disk_usage"]:
            if metric_name in self.metric_history and self.metric_history[metric_name]:
                latest = self.metric_history[metric_name][-1]
                health_metrics[metric_name] = {
                    "value": latest["value"],
                    "status": "healthy" if latest["value"] < 80 else "warning" if latest["value"] < 95 else "critical",
                    "unit": latest["unit"]
                }
        
        return health_metrics
    
    async def _get_performance_summary(self) -> Dict:
        """Get performance summary"""
        performance_metrics = {}
        
        for metric_name in ["api_response_time", "throughput", "error_rate"]:
            if metric_name in self.metric_history and self.metric_history[metric_name]:
                latest = self.metric_history[metric_name][-1]
                performance_metrics[metric_name] = {
                    "value": latest["value"],
                    "status": "good" if latest["value"] < latest["thresholds"].get("warning", 100) else "degraded",
                    "unit": latest["unit"]
                }
        
        return performance_metrics
    
    async def _get_security_summary(self) -> Dict:
        """Get security summary"""
        security_metrics = {}
        
        for metric_name in ["failed_logins", "suspicious_activities", "data_exfiltration_attempts"]:
            if metric_name in self.metric_history and self.metric_history[metric_name]:
                latest = self.metric_history[metric_name][-1]
                security_metrics[metric_name] = {
                    "value": latest["value"],
                    "status": "normal" if latest["value"] < latest["thresholds"].get("warning", 10) else "elevated",
                    "unit": latest["unit"]
                }
        
        return security_metrics
    
    async def _cleanup_old_data(self):
        """Cleanup old monitoring data"""
        try:
            # Cleanup old metric data (keep last 7 days)
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            metrics_collection = self.db.get_collection("monitoring_metrics")
            result = await metrics_collection.delete_many({
                "timestamp": {"$lt": cutoff_time.isoformat()}
            })
            
            if result.deleted_count > 0:
                logger.info(f"Cleaned up {result.deleted_count} old metric records")
            
            # Cleanup old alert data (keep last 30 days)
            alert_cutoff_time = datetime.utcnow() - timedelta(days=30)
            dashboard_collection = self.db.get_collection("dashboard_alerts")
            alert_result = await dashboard_collection.delete_many({
                "timestamp": {"$lt": alert_cutoff_time.isoformat()}
            })
            
            if alert_result.deleted_count > 0:
                logger.info(f"Cleaned up {alert_result.deleted_count} old alert records")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def get_monitoring_dashboard_data(self) -> Dict:
        """Get comprehensive monitoring dashboard data"""
        return {
            "system_status": await self._get_system_health_summary(),
            "performance": await self._get_performance_summary(),
            "security": await self._get_security_summary(),
            "active_alerts": list(self.active_alerts.values()),
            "alert_history": list(self.alert_history)[-50:],
            "metrics_history": {
                metric_name: list(history)[-100:] 
                for metric_name, history in self.metric_history.items()
            },
            "summary": {
                "total_alerts_24h": len([a for a in self.alert_history 
                                         if datetime.fromisoformat(a["timestamp"]) > datetime.utcnow() - timedelta(hours=24)]),
                "critical_alerts": len([a for a in self.active_alerts.values() if a["severity"] == "critical"]),
                "warning_alerts": len([a for a in self.active_alerts.values() if a["severity"] == "warning"]),
                "system_uptime": await self._calculate_uptime()
            }
        }
