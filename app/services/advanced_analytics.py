"""
Advanced Analytics and Reporting for SOC Correlation Engine
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class ReportType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"

class MetricType(Enum):
    SECURITY_POSTURE = "security_posture"
    THREAT_LANDSCAPE = "threat_landscape"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    TREND_ANALYSIS = "trend_analysis"
    PREDICTIVE_ANALYTICS = "predictive_analytics"

@dataclass
class AnalyticsMetric:
    """Analytics metric definition"""
    name: str
    type: MetricType
    description: str
    calculation_method: str
    threshold: Optional[float] = None
    unit: Optional[str] = None

class AdvancedAnalyticsEngine:
    """Advanced analytics and reporting engine"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.metrics_cache = {}
        self.report_templates = {}
        self.prediction_models = {}
        
    async def initialize_analytics(self):
        """Initialize analytics engine"""
        await self._setup_metrics()
        await self._setup_report_templates()
        await self._setup_prediction_models()
        logger.info("Advanced analytics engine initialized")
    
    async def _setup_metrics(self):
        """Setup analytics metrics"""
        self.metrics = {
            MetricType.SECURITY_POSTURE: [
                AnalyticsMetric(
                    name="security_score",
                    type=MetricType.SECURITY_POSTURE,
                    description="Overall security posture score",
                    calculation_method="weighted_average",
                    threshold=80.0,
                    unit="score"
                ),
                AnalyticsMetric(
                    name="risk_exposure",
                    type=MetricType.SECURITY_POSTURE,
                    description="Total risk exposure",
                    calculation_method="sum_risk_scores",
                    threshold=1000.0,
                    unit="points"
                ),
                AnalyticsMetric(
                    name="vulnerability_density",
                    type=MetricType.SECURITY_POSTURE,
                    description="Vulnerabilities per asset",
                    calculation_method="vulnerability_ratio",
                    threshold=0.1,
                    unit="ratio"
                )
            ],
            MetricType.THREAT_LANDSCAPE: [
                AnalyticsMetric(
                    name="threat_diversity",
                    type=MetricType.THREAT_LANDSCAPE,
                    description="Number of unique threat types",
                    calculation_method="unique_categories",
                    threshold=10,
                    unit="count"
                ),
                AnalyticsMetric(
                    name="attack_frequency",
                    type=MetricType.THREAT_LANDSCAPE,
                    description="Attacks per day",
                    calculation_method="daily_average",
                    threshold=50,
                    unit="attacks/day"
                ),
                AnalyticsMetric(
                    name="threat_sophistication",
                    type=MetricType.THREAT_LANDSCAPE,
                    description="Average threat sophistication level",
                    calculation_method="severity_weighted_average",
                    threshold=5.0,
                    unit="level"
                )
            ],
            MetricType.COMPLIANCE: [
                AnalyticsMetric(
                    name="compliance_score",
                    type=MetricType.COMPLIANCE,
                    description="Regulatory compliance percentage",
                    calculation_method="compliance_percentage",
                    threshold=95.0,
                    unit="percent"
                ),
                AnalyticsMetric(
                    name="policy_violations",
                    type=MetricType.COMPLIANCE,
                    description="Security policy violations per week",
                    calculation_method="weekly_count",
                    threshold=5,
                    unit="violations/week"
                )
            ],
            MetricType.PERFORMANCE: [
                AnalyticsMetric(
                    name="detection_time",
                    type=MetricType.PERFORMANCE,
                    description="Average threat detection time",
                    calculation_method="mean_time_to_detect",
                    threshold=300,
                    unit="seconds"
                ),
                AnalyticsMetric(
                    name="response_time",
                    type=MetricType.PERFORMANCE,
                    description="Average incident response time",
                    calculation_method="mean_time_to_respond",
                    threshold=900,
                    unit="seconds"
                ),
                AnalyticsMetric(
                    name="system_throughput",
                    type=MetricType.PERFORMANCE,
                    description="Alerts processed per minute",
                    calculation_method="alerts_per_minute",
                    threshold=100,
                    unit="alerts/min"
                )
            ]
        }
    
    async def _setup_report_templates(self):
        """Setup report templates"""
        self.report_templates = {
            "executive_dashboard": {
                "name": "Executive Security Dashboard",
                "description": "High-level security overview for executives",
                "metrics": [
                    "security_score",
                    "risk_exposure",
                    "threat_diversity",
                    "compliance_score",
                    "detection_time",
                    "response_time"
                ],
                "visualization": ["gauge", "trend", "heatmap", "summary"]
            },
            "security_operations": {
                "name": "Security Operations Report",
                "description": "Detailed security operations metrics",
                "metrics": [
                    "attack_frequency",
                    "threat_sophistication",
                    "vulnerability_density",
                    "policy_violations",
                    "system_throughput"
                ],
                "visualization": ["timeseries", "bar", "pie", "table"]
            },
            "threat_intelligence": {
                "name": "Threat Intelligence Report",
                "description": "Threat landscape and trends analysis",
                "metrics": [
                    "threat_diversity",
                    "attack_frequency",
                    "threat_sophistication"
                ],
                "visualization": ["heatmap", "network", "timeline", "geographic"]
            },
            "compliance_audit": {
                "name": "Compliance Audit Report",
                "description": "Regulatory compliance status",
                "metrics": [
                    "compliance_score",
                    "policy_violations"
                ],
                "visualization": ["scorecard", "trend", "gap_analysis"]
            }
        }
    
    async def _setup_prediction_models(self):
        """Setup prediction models"""
        self.prediction_models = {
            "threat_prediction": {
                "name": "Threat Prediction Model",
                "description": "Predict future threat activity",
                "features": ["historical_alerts", "seasonal_patterns", "threat_intelligence"],
                "algorithm": "lstm_neural_network",
                "prediction_horizon": "7_days",
                "accuracy_target": 0.85
            },
            "risk_assessment": {
                "name": "Risk Assessment Model",
                "description": "Assess and predict risk levels",
                "features": ["vulnerability_data", "asset_value", "threat_landscape"],
                "algorithm": "random_forest",
                "prediction_horizon": "30_days",
                "accuracy_target": 0.90
            },
            "capacity_planning": {
                "name": "Capacity Planning Model",
                "description": "Predict system resource needs",
                "features": ["alert_volume_trend", "correlation_complexity", "storage_growth"],
                "algorithm": "linear_regression",
                "prediction_horizon": "90_days",
                "accuracy_target": 0.80
            }
        }
    
    async def generate_comprehensive_report(self, report_type: str, time_period: str = "7d") -> Dict:
        """Generate comprehensive analytics report"""
        try:
            # Parse time period
            end_time = datetime.utcnow()
            if time_period.endswith('d'):
                days = int(time_period[:-1])
                start_time = end_time - timedelta(days=days)
            elif time_period.endswith('h'):
                hours = int(time_period[:-1])
                start_time = end_time - timedelta(hours=hours)
            else:
                start_time = end_time - timedelta(days=7)
            
            # Generate metrics
            metrics_data = await self._calculate_all_metrics(start_time, end_time)
            
            # Generate insights
            insights = await self._generate_insights(metrics_data, start_time, end_time)
            
            # Generate predictions
            predictions = await self._generate_predictions(metrics_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(metrics_data, insights)
            
            report = {
                "report_metadata": {
                    "type": report_type,
                    "period": time_period,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                    "generated_at": datetime.utcnow().isoformat(),
                    "version": "2.0"
                },
                "executive_summary": await self._generate_executive_summary(metrics_data, insights),
                "metrics": metrics_data,
                "insights": insights,
                "predictions": predictions,
                "recommendations": recommendations,
                "visualizations": await self._prepare_visualizations(metrics_data),
                "appendix": await self._generate_appendix(metrics_data)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def _calculate_all_metrics(self, start_time: datetime, end_time: datetime) -> Dict:
        """Calculate all analytics metrics"""
        metrics_data = {}
        
        # Get alerts from database
        alerts_collection = self.db.get_collection("alerts")
        alerts = await alerts_collection.find({
            "timestamp": {"$gte": start_time.isoformat(), "$lte": end_time.isoformat()}
        }).to_list()
        
        # Get correlations
        correlations_collection = self.db.get_collection("correlation_groups")
        correlations = await correlations_collection.find({
            "created_at": {"$gte": start_time.isoformat(), "$lte": end_time.isoformat()}
        }).to_list()
        
        for metric_type, metric_list in self.metrics.items():
            metrics_data[metric_type.value] = {}
            
            for metric in metric_list:
                try:
                    value = await self._calculate_metric_value(metric, alerts, correlations, start_time, end_time)
                    metrics_data[metric_type.value][metric.name] = {
                        "value": value,
                        "unit": metric.unit,
                        "threshold": metric.threshold,
                        "status": "good" if metric.threshold and value <= metric.threshold else "warning",
                        "trend": await self._calculate_trend(metric.name, value, start_time, end_time)
                    }
                except Exception as e:
                    logger.error(f"Error calculating metric {metric.name}: {e}")
                    metrics_data[metric_type.value][metric.name] = {
                        "value": None,
                        "error": str(e),
                        "status": "error"
                    }
        
        return metrics_data
    
    async def _calculate_metric_value(self, metric: AnalyticsMetric, alerts: List[Dict], 
                                 correlations: List[Dict], start_time: datetime, end_time: datetime) -> float:
        """Calculate specific metric value"""
        if metric.calculation_method == "weighted_average":
            return await self._calculate_weighted_average(alerts, metric.name)
        elif metric.calculation_method == "sum_risk_scores":
            return await self._sum_risk_scores(alerts)
        elif metric.calculation_method == "vulnerability_ratio":
            return await self._calculate_vulnerability_ratio(alerts)
        elif metric.calculation_method == "unique_categories":
            return await self._count_unique_categories(alerts)
        elif metric.calculation_method == "daily_average":
            return await self._calculate_daily_average(alerts, start_time, end_time)
        elif metric.calculation_method == "severity_weighted_average":
            return await self._calculate_severity_weighted_average(alerts)
        elif metric.calculation_method == "compliance_percentage":
            return await self._calculate_compliance_percentage(alerts)
        elif metric.calculation_method == "weekly_count":
            return await self._calculate_weekly_count(alerts, start_time, end_time)
        elif metric.calculation_method == "mean_time_to_detect":
            return await self._calculate_mean_time_to_detect(alerts)
        elif metric.calculation_method == "mean_time_to_respond":
            return await self._calculate_mean_time_to_respond(alerts)
        elif metric.calculation_method == "alerts_per_minute":
            return await self._calculate_alerts_per_minute(alerts, start_time, end_time)
        else:
            return 0.0
    
    async def _calculate_weighted_average(self, alerts: List[Dict], metric_name: str) -> float:
        """Calculate weighted average metric"""
        if not alerts:
            return 0.0
        
        weights = {
            "security_score": {
                "critical": 0.4, "high": 0.3, "medium": 0.2, "low": 0.1
            },
            "risk_exposure": {
                "critical": 10, "high": 7.5, "medium": 5, "low": 2.5
            }
        }
        
        if metric_name in weights:
            weight_map = weights[metric_name]
            total_weighted = 0.0
            total_weight = 0.0
            
            for alert in alerts:
                severity = alert.get("severity", "medium")
                risk_score = alert.get("risk_score", 5.0)
                weight = weight_map.get(severity, 0.25)
                total_weighted += risk_score * weight
                total_weight += weight
            
            return total_weighted / total_weight if total_weight > 0 else 0.0
        
        return sum(alert.get("risk_score", 5.0) for alert in alerts) / len(alerts)
    
    async def _sum_risk_scores(self, alerts: List[Dict]) -> float:
        """Sum all risk scores"""
        return sum(alert.get("risk_score", 0.0) for alert in alerts)
    
    async def _calculate_vulnerability_ratio(self, alerts: List[Dict]) -> float:
        """Calculate vulnerability density"""
        if not alerts:
            return 0.0
        
        vulnerability_alerts = [a for a in alerts if a.get("category") in ["vulnerability", "patch_management"]]
        total_assets = len(set(alert.get("raw_data", {}).get("target_asset", "unknown") for alert in alerts))
        
        return len(vulnerability_alerts) / total_assets if total_assets > 0 else 0.0
    
    async def _count_unique_categories(self, alerts: List[Dict]) -> int:
        """Count unique threat categories"""
        return len(set(alert.get("category", "unknown") for alert in alerts))
    
    async def _calculate_daily_average(self, alerts: List[Dict], start_time: datetime, end_time: datetime) -> float:
        """Calculate daily average of alerts"""
        days = (end_time - start_time).days + 1
        return len(alerts) / days if days > 0 else 0.0
    
    async def _calculate_severity_weighted_average(self, alerts: List[Dict]) -> float:
        """Calculate severity-weighted average sophistication"""
        severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        if not alerts:
            return 0.0
        
        total_weighted = sum(severity_weights.get(alert.get("severity", "medium"), 2) for alert in alerts)
        return total_weighted / len(alerts)
    
    async def _calculate_compliance_percentage(self, alerts: List[Dict]) -> float:
        """Calculate compliance percentage"""
        if not alerts:
            return 100.0
        
        compliant_alerts = [a for a in alerts if a.get("compliance_status", "unknown") == "compliant"]
        return (len(compliant_alerts) / len(alerts)) * 100
    
    async def _calculate_weekly_count(self, alerts: List[Dict], start_time: datetime, end_time: datetime) -> float:
        """Calculate weekly count of policy violations"""
        weeks = (end_time - start_time).days / 7 + 1
        violation_alerts = [a for a in alerts if a.get("category") in ["policy_violation", "compliance_breach"]]
        return len(violation_alerts) / weeks if weeks > 0 else 0.0
    
    async def _calculate_mean_time_to_detect(self, alerts: List[Dict]) -> float:
        """Calculate mean time to detect threats"""
        detection_times = []
        
        for alert in alerts:
            if "detection_time" in alert.get("raw_data", {}):
                detection_time = alert["raw_data"]["detection_time"]
                alert_time = datetime.fromisoformat(alert.get("timestamp"))
                detection_datetime = datetime.fromisoformat(detection_time)
                detection_times.append((alert_time - detection_datetime).total_seconds())
        
        return sum(detection_times) / len(detection_times) if detection_times else 0.0
    
    async def _calculate_mean_time_to_respond(self, alerts: List[Dict]) -> float:
        """Calculate mean time to respond to threats"""
        response_times = []
        
        for alert in alerts:
            if "response_time" in alert.get("raw_data", {}):
                response_time = alert["raw_data"]["response_time"]
                alert_time = datetime.fromisoformat(alert.get("timestamp"))
                response_datetime = datetime.fromisoformat(response_time)
                response_times.append((response_datetime - alert_time).total_seconds())
        
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    async def _calculate_alerts_per_minute(self, alerts: List[Dict], start_time: datetime, end_time: datetime) -> float:
        """Calculate alerts processed per minute"""
        minutes = (end_time - start_time).total_seconds() / 60
        return len(alerts) / minutes if minutes > 0 else 0.0
    
    async def _calculate_trend(self, metric_name: str, current_value: float, 
                            start_time: datetime, end_time: datetime) -> str:
        """Calculate trend for metric"""
        # Get historical data for trend calculation
        previous_period_start = start_time - timedelta(days=7)
        previous_period_end = start_time
        
        alerts_collection = self.db.get_collection("alerts")
        previous_alerts = await alerts_collection.find({
            "timestamp": {"$gte": previous_period_start.isoformat(), "$lte": previous_period_end.isoformat()}
        }).to_list()
        
        previous_value = await self._calculate_metric_value(
            next(m for m in self.metrics[MetricType.SECURITY_POSTURE] if m.name == metric_name),
            previous_alerts, [], previous_period_start, previous_period_end
        )
        
        if previous_value == 0:
            return "stable"
        
        change_percent = ((current_value - previous_value) / previous_value) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    async def _generate_insights(self, metrics_data: Dict, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Generate insights from metrics data"""
        insights = []
        
        # Security posture insights
        security_metrics = metrics_data.get("security_posture", {})
        if "security_score" in security_metrics:
            score = security_metrics["security_score"]["value"]
            if score < 70:
                insights.append({
                    "type": "critical",
                    "category": "security_posture",
                    "title": "Low Security Score Detected",
                    "description": f"Security posture score is {score:.1f}, below acceptable threshold",
                    "recommendation": "Implement immediate security improvements and conduct risk assessment"
                })
            elif score < 85:
                insights.append({
                    "type": "warning",
                    "category": "security_posture",
                    "title": "Security Score Needs Improvement",
                    "description": f"Security posture score is {score:.1f}, room for improvement",
                    "recommendation": "Review security controls and implement best practices"
                })
        
        # Threat landscape insights
        threat_metrics = metrics_data.get("threat_landscape", {})
        if "attack_frequency" in threat_metrics:
            frequency = threat_metrics["attack_frequency"]["value"]
            if frequency > 100:
                insights.append({
                    "type": "critical",
                    "category": "threat_landscape",
                    "title": "High Attack Frequency",
                    "description": f"Attack frequency is {frequency:.1f} attacks per day, significantly elevated",
                    "recommendation": "Enhance monitoring and consider implementing additional security controls"
                })
        
        # Performance insights
        performance_metrics = metrics_data.get("performance", {})
        if "detection_time" in performance_metrics:
            detection_time = performance_metrics["detection_time"]["value"]
            if detection_time > 600:  # 10 minutes
                insights.append({
                    "type": "warning",
                    "category": "performance",
                    "title": "Slow Threat Detection",
                    "description": f"Average detection time is {detection_time:.1f} seconds, above optimal",
                    "recommendation": "Optimize detection algorithms and monitoring processes"
                })
        
        return insights
    
    async def _generate_predictions(self, metrics_data: Dict) -> List[Dict]:
        """Generate predictions based on current metrics"""
        predictions = []
        
        # Threat prediction
        threat_metrics = metrics_data.get("threat_landscape", {})
        if "attack_frequency" in threat_metrics:
            current_frequency = threat_metrics["attack_frequency"]["value"]
            trend = threat_metrics["attack_frequency"]["trend"]
            
            predicted_frequency = current_frequency * 1.2 if trend == "increasing" else current_frequency * 1.05
            
            predictions.append({
                "type": "threat_prediction",
                "metric": "attack_frequency",
                "current_value": current_frequency,
                "predicted_value": predicted_frequency,
                "prediction_horizon": "7_days",
                "confidence": 0.85,
                "description": f"Predicted attack frequency in 7 days: {predicted_frequency:.1f} attacks/day"
            })
        
        # Risk prediction
        security_metrics = metrics_data.get("security_posture", {})
        if "risk_exposure" in security_metrics:
            current_risk = security_metrics["risk_exposure"]["value"]
            trend = security_metrics["risk_exposure"]["trend"]
            
            predicted_risk = current_risk * 1.3 if trend == "increasing" else current_risk * 1.1
            
            predictions.append({
                "type": "risk_prediction",
                "metric": "risk_exposure",
                "current_value": current_risk,
                "predicted_value": predicted_risk,
                "prediction_horizon": "30_days",
                "confidence": 0.80,
                "description": f"Predicted risk exposure in 30 days: {predicted_risk:.1f} points"
            })
        
        return predictions
    
    async def _generate_recommendations(self, metrics_data: Dict, insights: List[Dict]) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Analyze critical insights
        critical_insights = [i for i in insights if i["type"] == "critical"]
        
        if critical_insights:
            recommendations.append({
                "priority": "high",
                "category": "immediate_action",
                "title": "Address Critical Security Issues",
                "description": f"Found {len(critical_insights)} critical issues requiring immediate attention",
                "actions": [
                    "Conduct emergency security assessment",
                    "Implement additional monitoring",
                    "Review and update security policies",
                    "Consider temporary security measures"
                ],
                "estimated_effort": "2-3 days",
                "impact": "high"
            })
        
        # Performance recommendations
        performance_metrics = metrics_data.get("performance", {})
        if "system_throughput" in performance_metrics:
            throughput = performance_metrics["system_throughput"]["value"]
            if throughput < 50:
                recommendations.append({
                    "priority": "medium",
                    "category": "performance_optimization",
                    "title": "Optimize System Throughput",
                    "description": f"System throughput is {throughput:.1f} alerts/min, below optimal",
                    "actions": [
                        "Scale processing resources",
                        "Optimize correlation algorithms",
                        "Implement parallel processing",
                        "Review system bottlenecks"
                    ],
                    "estimated_effort": "1-2 weeks",
                    "impact": "medium"
                })
        
        return recommendations
    
    async def _generate_executive_summary(self, metrics_data: Dict, insights: List[Dict]) -> Dict:
        """Generate executive summary"""
        security_score = metrics_data.get("security_posture", {}).get("security_score", {}).get("value", 0)
        risk_level = "Low" if security_score > 85 else "Medium" if security_score > 70 else "High"
        
        critical_insights = len([i for i in insights if i["type"] == "critical"])
        warning_insights = len([i for i in insights if i["type"] == "warning"])
        
        return {
            "overall_status": risk_level,
            "security_score": security_score,
            "key_metrics": {
                "total_alerts": len([a for metric_group in metrics_data.values() 
                                   for m in metric_group.values() if isinstance(m, dict)]),
                "critical_issues": critical_insights,
                "warning_issues": warning_insights,
                "system_health": "healthy" if critical_insights == 0 else "degraded"
            },
            "summary": f"Security posture is {risk_level} with a score of {security_score:.1f}. "
                      f"{'No critical issues detected.' if critical_insights == 0 else f'{critical_insights} critical issues require immediate attention.'}",
            "recommendations_priority": "Address critical issues immediately" if critical_insights > 0 else "Continue monitoring and optimization"
        }
    
    async def _prepare_visualizations(self, metrics_data: Dict) -> List[Dict]:
        """Prepare visualization data"""
        visualizations = []
        
        # Security score gauge
        if "security_posture" in metrics_data and "security_score" in metrics_data["security_posture"]:
            visualizations.append({
                "type": "gauge",
                "title": "Security Score",
                "data": {
                    "value": metrics_data["security_posture"]["security_score"]["value"],
                    "min": 0,
                    "max": 100,
                    "thresholds": [70, 85]
                }
            })
        
        # Threat landscape pie chart
        if "threat_landscape" in metrics_data:
            threat_data = metrics_data["threat_landscape"]
            if "threat_diversity" in threat_data:
                visualizations.append({
                    "type": "pie",
                    "title": "Threat Categories",
                    "data": await self._get_threat_category_distribution()
                })
        
        # Performance trend
        if "performance" in metrics_data:
            visualizations.append({
                "type": "timeseries",
                "title": "System Performance",
                "data": await self._get_performance_trend()
            })
        
        return visualizations
    
    async def _get_threat_category_distribution(self) -> List[Dict]:
        """Get threat category distribution for visualization"""
        alerts_collection = self.db.get_collection("alerts")
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        categories = await alerts_collection.aggregate(pipeline).to_list()
        
        return [{"category": cat["_id"], "count": cat["count"]} for cat in categories]
    
    async def _get_performance_trend(self) -> Dict:
        """Get performance trend data"""
        # Mock trend data - in production, query historical performance
        return {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            "datasets": [
                {
                    "label": "Alerts Processed",
                    "data": [120, 135, 125, 140, 130, 110, 100]
                },
                {
                    "label": "Detection Time (s)",
                    "data": [45, 42, 48, 40, 43, 50, 55]
                }
            ]
        }
    
    async def _generate_appendix(self, metrics_data: Dict) -> Dict:
        """Generate appendix with detailed data"""
        return {
            "methodology": "Advanced analytics using machine learning and statistical analysis",
            "data_sources": ["SIEM", "Firewall", "IDS/IPS", "Windows Logs", "Threat Intelligence"],
            "calculation_methods": {
                "security_score": "Weighted average based on severity and risk scores",
                "risk_exposure": "Sum of all risk scores with severity weighting",
                "threat_diversity": "Count of unique threat categories",
                "compliance_score": "Percentage of compliant security events"
            },
            "assumptions": [
                "All data sources are active and reporting correctly",
                "Risk scores are calculated using standardized methodology",
                "Time periods are based on UTC timestamps"
            ]
        }
