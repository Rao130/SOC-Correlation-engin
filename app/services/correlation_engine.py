import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json
import numpy as np

# from sklearn.cluster import DBSCAN
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# import spacy

from app.core.database import get_db
from app.core.config import settings
from app.utils.logger import setup_logging

logger = setup_logging()

class CorrelationEngine:
    """Advanced alert correlation engine for SOC operations"""
    
    def __init__(self, db_manager=None):
        self.db = db_manager or get_db()  # Use passed db_manager or get default
        self.running = False
        self.correlation_task = None
        self.nlp = None
        self.vectorizer = None  # Disabled for demo
        
        # Correlation thresholds
        self.entity_threshold = 0.7
        self.temporal_threshold = 3600  # 1 hour in seconds
        self.semantic_threshold = 0.6
        self.geographic_threshold = 500  # 500 km
        
        # Load NLP model
        self._load_nlp_model()
    
    def _load_nlp_model(self):
        """Load NLP model for semantic analysis"""
        # Simplified version without spacy for demo
        self.nlp = None
        logger.info("NLP model disabled for demo")
    
    async def start(self):
        """Start the correlation engine"""
        if self.running:
            return
        
        self.running = True
        self.correlation_task = asyncio.create_task(self._correlation_loop())
        logger.info("Correlation engine started")
    
    async def stop(self):
        """Stop the correlation engine"""
        self.running = False
        if self.correlation_task:
            self.correlation_task.cancel()
            try:
                await self.correlation_task
            except asyncio.CancelledError:
                pass
        logger.info("Correlation engine stopped")
    
    def is_running(self) -> bool:
        """Check if correlation engine is running"""
        return self.running
    
    async def _correlation_loop(self):
        """Main correlation processing loop"""
        while self.running:
            try:
                await self._process_correlations()
                await asyncio.sleep(settings.BACKGROUND_TASK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in correlation loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _process_correlations(self):
        """Process alert correlations"""
        try:
            # Get recent alerts for correlation
            alerts = await self._get_recent_alerts()
            
            if not alerts:
                logger.info("No alerts found for correlation")
                return []
            
            logger.info(f"Processing correlations for {len(alerts)} alerts")
            
            # Find correlations between alerts
            correlation_groups = await self._find_correlations(alerts)
            
            # Store correlations in database
            for correlation in correlation_groups:
                await self._store_correlation(correlation)
            
            logger.info(f"Found {len(correlation_groups)} correlation groups")
            return correlation_groups
            
        except Exception as e:
            logger.error(f"Error processing correlations: {e}")
            return []
    
    async def _get_recent_alerts(self) -> List[Dict]:
        """Get recent alerts for correlation analysis"""
        try:
            # In a real implementation, this would query the database
            # For now, return mock data
            return [
                {
                    "id": 1,
                    "title": "SQL Injection Attack",
                    "source_ip": "192.168.1.105",
                    "timestamp": "2024-04-05 14:32:15",
                    "severity": "critical",
                    "category": "injection"
                },
                {
                    "id": 2,
                    "title": "Brute Force Attempt",
                    "source_ip": "10.0.0.15",
                    "timestamp": "2024-04-05 14:31:42",
                    "severity": "high",
                    "category": "authentication"
                },
                {
                    "id": 3,
                    "title": "Suspicious File Upload",
                    "source_ip": "172.16.0.45",
                    "timestamp": "2024-04-05 14:30:28",
                    "severity": "medium",
                    "category": "filesystem"
                }
            ]
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []

    async def _store_correlation(self, correlation: Dict):
        """Store correlation in database"""
        try:
            # In a real implementation, this would store in database
            logger.info(f"Storing correlation: {correlation.get('name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Error storing correlation: {e}")
            return False

    async def _find_correlations(self, alerts: List[Dict]) -> List[Dict]:
        """Find correlations between alerts using multiple methods"""
        correlation_groups = []
        
        # Entity-based correlation
        entity_groups = await self._entity_based_correlation(alerts)
        correlation_groups.extend(entity_groups)
        
        # Temporal correlation
        temporal_groups = await self._temporal_correlation(alerts)
        correlation_groups.extend(temporal_groups)
        
        # Pattern-based correlation
        pattern_groups = await self._pattern_based_correlation(alerts)
        correlation_groups.extend(pattern_groups)
        
        return correlation_groups

    async def _entity_based_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Group alerts by common entities (IP, user, etc.)"""
        correlations = []
        correlation_id = 1
        
        # Group by source IP
        ip_groups = {}
        for alert in alerts:
            ip = alert.get('source_ip', 'unknown')
            if ip not in ip_groups:
                ip_groups[ip] = []
            ip_groups[ip].append(alert)
        
        # Create correlation groups for IPs with multiple alerts
        for ip, ip_alerts in ip_groups.items():
            if len(ip_alerts) > 1:
                correlations.append({
                    'id': correlation_id,
                    'name': f'Multiple Alerts from {ip}',
                    'description': f'{len(ip_alerts)} alerts detected from same source IP',
                    'correlation_score': min(90, len(ip_alerts) * 20),
                    'confidence': 85,
                    'type': 'entity_based',
                    'alerts': ip_alerts,
                    'timestamp': datetime.now().isoformat()
                })
                correlation_id += 1
        
        return correlations

    async def _temporal_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Group alerts by time proximity"""
        correlations = []
        correlation_id = 1
        
        # Sort alerts by timestamp
        sorted_alerts = sorted(alerts, key=lambda x: x.get('timestamp', ''))
        
        # Find alerts within 5 minutes of each other
        time_window = 300  # 5 minutes in seconds
        
        for i, alert in enumerate(sorted_alerts):
            nearby_alerts = [alert]
            alert_time = datetime.fromisoformat(alert.get('timestamp', '').replace('Z', '+00:00'))
            
            for j in range(i + 1, len(sorted_alerts)):
                other_alert = sorted_alerts[j]
                other_time = datetime.fromisoformat(other_alert.get('timestamp', '').replace('Z', '+00:00'))
                
                if abs((alert_time - other_time).total_seconds()) <= time_window:
                    nearby_alerts.append(other_alert)
                else:
                    break
            
            if len(nearby_alerts) > 1:
                correlations.append({
                    'id': correlation_id,
                    'name': f'Temporal Cluster',
                    'description': f'{len(nearby_alerts)} alerts within {time_window//60} minutes',
                    'correlation_score': min(80, len(nearby_alerts) * 15),
                    'confidence': 75,
                    'type': 'temporal',
                    'alerts': nearby_alerts,
                    'timestamp': datetime.now().isoformat()
                })
                correlation_id += 1
        
        return correlations

    async def _pattern_based_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Group alerts by attack patterns"""
        correlations = []
        correlation_id = 1
        
        # Group by category
        category_groups = {}
        for alert in alerts:
            category = alert.get('category', 'unknown')
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(alert)
        
        # Create correlation groups for categories with multiple alerts
        for category, cat_alerts in category_groups.items():
            if len(cat_alerts) > 1:
                correlations.append({
                    'id': correlation_id,
                    'name': f'{category.title()} Attack Pattern',
                    'description': f'{len(cat_alerts)} {category} attacks detected',
                    'correlation_score': min(70, len(cat_alerts) * 10),
                    'confidence': 70,
                    'type': 'pattern_based',
                    'alerts': cat_alerts,
                    'timestamp': datetime.now().isoformat()
                })
                correlation_id += 1
        
        return correlations

    def _get_priority_from_score(self, score: int) -> str:
        """Calculate priority from correlation score"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'

    async def get_total_correlations(self) -> int:
        """Get total number of correlation groups"""
        try:
            correlation_collection = self.db.get_database().correlation_groups
            return await correlation_collection.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total correlations: {e}")
            return 0

    async def get_active_correlations(self) -> int:
        """Get number of active correlation groups"""
        try:
            correlation_collection = self.db.get_database().correlation_groups
            return await correlation_collection.count_documents({'status': 'active'})
        except Exception as e:
            logger.error(f"Error getting active correlations: {e}")
            return 0
        
        if sev1 > 0 and sev2 > 0:
            severity_similarity = 1 - abs(sev1 - sev2) / 4
            similarity += severity_similarity * 0.2
        
        # Source similarity
        if alert1.get('source') == alert2.get('source'):
            similarity += 0.1
        
        return min(1.0, similarity)
    
    def _get_entity_importance(self, entity_type: str) -> float:
        """Get importance weight for entity type"""
        importance_weights = {
            'ip': 0.8,
            'domain': 0.7,
            'url': 0.6,
            'hash': 0.9,
            'email': 0.5,
            'user': 0.4,
            'file': 0.3
        }
        return importance_weights.get(entity_type, 0.5)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        from math import radians, cos, sin, asin, sqrt
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Earth's radius in kilometers
        r = 6371
        
        return c * r
    
    def _calculate_cluster_radius(self, alerts: List[Dict]) -> float:
        """Calculate the radius of a geographic cluster"""
        if len(alerts) < 2:
            return 0
        
        locations = [(alert['location']['latitude'], alert['location']['longitude']) 
                    for alert in alerts if alert.get('location')]
        
        if len(locations) < 2:
            return 0
        
        # Calculate maximum distance between any two points
        max_distance = 0
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                distance = self._calculate_distance(
                    locations[i][0], locations[i][1],
                    locations[j][0], locations[j][1]
                )
                max_distance = max(max_distance, distance)
        
        return max_distance
    
    async def _analyze_behavioral_pattern(self, alerts: List[Dict]) -> float:
        """Analyze behavioral pattern and return pattern score"""
        score = 0.0
        
        # Time-based pattern
        timestamps = [alert['timestamp'] for alert in alerts]
        if len(timestamps) >= 3:
            # Check for regular intervals
            intervals = []
            for i in range(1, len(timestamps)):
                interval = (timestamps[i] - timestamps[i-1]).total_seconds()
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                
                # Lower variance = more regular pattern
                pattern_consistency = max(0, 1 - variance / (avg_interval ** 2))
                score += pattern_consistency * 30
        
        # Severity progression
        severities = [alert.get('severity') for alert in alerts]
        severity_counts = {sev: severities.count(sev) for sev in set(severities)}
        
        # Check for escalating severity
        if 'critical' in severity_counts or 'high' in severity_counts:
            score += 20
        
        # Entity diversity
        all_entities = set()
        for alert in alerts:
            for entity in alert.get('entities', []):
                all_entities.add(f"{entity['type']}:{entity['value']}")
        
        entity_diversity = len(all_entities) / len(alerts) if alerts else 0
        score += min(20, entity_diversity * 10)
        
        # Source consistency
        sources = [alert.get('source') for alert in alerts]
        unique_sources = len(set(sources))
        source_consistency = 1 - (unique_sources - 1) / len(sources) if sources else 0
        score += source_consistency * 15
        
        return min(100, score)
    
    def _merge_correlation_groups(self, groups: List[Dict]) -> List[Dict]:
        """Merge overlapping correlation groups"""
        if not groups:
            return []
        
        merged_groups = []
        used_alerts = set()
        
        # Sort groups by score (highest first)
        groups.sort(key=lambda x: x['score'], reverse=True)
        
        for group in groups:
            group_alert_ids = {alert.get('alert_id') for alert in group['alerts']}
            
            # Skip if most alerts are already used
            overlap = len(group_alert_ids.intersection(used_alerts))
            if overlap > len(group_alert_ids) * 0.5:
                continue
            
            merged_groups.append(group)
            used_alerts.update(group_alert_ids)
        
        return merged_groups
    
    async def _save_correlation_groups(self, correlation_groups: List[Dict]):
        """Save correlation groups to database"""
        if not correlation_groups:
            return
        
        correlation_collection = self.db.get_database().correlation_groups
        
        for group in correlation_groups:
            correlation_doc = {
                'groupId': f"corr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(group['alerts'])}",
                'name': f"{group['type'].replace('_', ' ').title()} Correlation",
                'description': f"Correlation group with {len(group['alerts'])} alerts",
                'correlationType': group['type'],
                'correlationScore': group['score'],
                'confidence': group['confidence'],
                'alerts': [
                    {
                        'alertId': alert.get('alert_id'),
                        'severity': alert.get('severity'),
                        'timestamp': alert.get('timestamp'),
                        'contributionScore': 1.0
                    }
                    for alert in group['alerts']
                ],
                'timeWindow': {
                    'start': min(alert['timestamp'] for alert in group['alerts']),
                    'end': max(alert['timestamp'] for alert in group['alerts']),
                    'duration': int((max(alert['timestamp'] for alert in group['alerts']) - 
                                   min(alert['timestamp'] for alert in group['alerts'])).total_seconds() * 1000)
                },
                'status': 'active',
                'priority': self._calculate_priority_from_score(group['score']),
                'metrics': {
                    'alertCount': len(group['alerts']),
                    'uniqueEntities': len(set(
                        f"{entity['type']}:{entity['value']}"
                        for alert in group['alerts']
                        for entity in alert.get('entities', [])
                    )),
                    'severityScore': sum(
                        {'low': 1, 'medium': 3, 'high': 7, 'critical': 10}.get(alert.get('severity'), 1)
                        for alert in group['alerts']
                    ) / len(group['alerts'])
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await correlation_collection.insert_one(correlation_doc)
    
    async def _update_alert_correlations(self, correlation_groups: List[Dict]):
        """Update alerts with correlation information"""
        alerts_collection = self.db.get_database().alerts
        
        for group in correlation_groups:
            group_id = f"corr_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(group['alerts'])}"
            
            for alert in group['alerts']:
                await alerts_collection.update_one(
                    {'alertId': alert.get('alert_id')},
                    {
                        '$addToSet': {
                            'correlationGroups': group_id
                        },
                        '$set': {
                            'processing.correlation_processed': True,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
    
    def _calculate_priority_from_score(self, score: float) -> str:
        """Calculate priority from correlation score"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    async def get_total_correlations(self) -> int:
        """Get total number of correlation groups"""
        try:
            correlation_collection = self.db.get_database().correlation_groups
            return await correlation_collection.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total correlations: {e}")
            return 0
    
    async def get_active_correlations(self) -> int:
        """Get number of active correlation groups"""
        try:
            correlation_collection = self.db.get_database().correlation_groups
            return await correlation_collection.count_documents({'status': 'active'})
        except Exception as e:
            logger.error(f"Error getting active correlations: {e}")
            return 0
