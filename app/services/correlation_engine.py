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
        """Process alert correlations - disabled for demo"""
        try:
            logger.info("Correlation processing disabled for demo")
            return []
        except Exception as e:
            logger.error(f"Error processing correlations: {e}")
            return []
    
    async def _find_correlations(self, alerts: List[Dict]) -> List[Dict]:
        """Find correlations between alerts using multiple methods"""
        correlation_groups = []
        
        # Entity-based correlation
        entity_groups = await self._entity_based_correlation(alerts)
        correlation_groups.extend(entity_groups)
        
        # Temporal correlation
        temporal_groups = await self._temporal_correlation(alerts)
        correlation_groups.extend(temporal_groups)
        
        # Semantic correlation
        if self.nlp:
            semantic_groups = await self._semantic_correlation(alerts)
            correlation_groups.extend(semantic_groups)
        
        # Geographic correlation
        geographic_groups = await self._geographic_correlation(alerts)
        correlation_groups.extend(geographic_groups)
        
        # Behavioral correlation
        behavioral_groups = await self._behavioral_correlation(alerts)
        correlation_groups.extend(behavioral_groups)
        
        # Remove duplicates and merge similar groups
        correlation_groups = self._merge_correlation_groups(correlation_groups)
        
        return correlation_groups
    
    async def _entity_based_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts based on shared entities"""
        entity_map = defaultdict(list)
        
        # Build entity to alerts mapping
        for alert in alerts:
            for entity in alert.get('entities', []):
                entity_key = f"{entity['type']}:{entity['value']}"
                entity_map[entity_key].append(alert)
        
        correlation_groups = []
        
        # Find groups with multiple alerts
        for entity_key, entity_alerts in entity_map.items():
            if len(entity_alerts) >= 2:
                # Calculate correlation score based on entity importance
                entity_type = entity_key.split(':')[0]
                entity_importance = self._get_entity_importance(entity_type)
                
                correlation_score = min(100, len(entity_alerts) * entity_importance * 20)
                
                correlation_groups.append({
                    'type': 'entity_based',
                    'alerts': entity_alerts,
                    'score': correlation_score,
                    'entity': entity_key,
                    'confidence': min(100, len(entity_alerts) * 25)
                })
        
        return correlation_groups
    
    async def _temporal_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts based on temporal proximity"""
        correlation_groups = []
        
        # Sort alerts by timestamp
        sorted_alerts = sorted(alerts, key=lambda x: x['timestamp'])
        
        # Find temporal clusters
        for i, alert1 in enumerate(sorted_alerts):
            temporal_cluster = [alert1]
            
            for alert2 in sorted_alerts[i+1:]:
                time_diff = (alert2['timestamp'] - alert1['timestamp']).total_seconds()
                
                if time_diff <= self.temporal_threshold:
                    # Check for other similarities
                    similarity = await self._calculate_alert_similarity(alert1, alert2)
                    if similarity >= 0.3:
                        temporal_cluster.append(alert2)
                else:
                    break
            
            if len(temporal_cluster) >= 2:
                correlation_score = min(100, len(temporal_cluster) * 15)
                
                correlation_groups.append({
                    'type': 'temporal',
                    'alerts': temporal_cluster,
                    'score': correlation_score,
                    'time_window': max(1, int((temporal_cluster[-1]['timestamp'] - temporal_cluster[0]['timestamp']).total_seconds() / 60)),
                    'confidence': min(100, len(temporal_cluster) * 20)
                })
        
        return correlation_groups
    
    async def _semantic_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts based on semantic similarity"""
        # Simplified version without ML libraries for demo
        correlation_groups = []
        
        # Simple text similarity based on common words
        for i, alert1 in enumerate(alerts):
            for alert2 in alerts[i+1:]:
                # Simple keyword matching for demo
                text1 = f"{alert1.get('title', '')} {alert1.get('description', '')}".lower()
                text2 = f"{alert2.get('title', '')} {alert2.get('description', '')}".lower()
                
                # Calculate simple similarity
                words1 = set(text1.split())
                words2 = set(text2.split())
                
                if words1 and words2:
                    similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                    
                    if similarity >= 0.3:  # Lower threshold for simple matching
                        correlation_groups.append({
                            'type': 'semantic',
                            'alerts': [alert1, alert2],
                            'score': similarity * 100,
                            'cluster_id': i,
                            'confidence': min(100, similarity * 100)
                        })
        
        return correlation_groups
    
    async def _geographic_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts based on geographic proximity"""
        correlation_groups = []
        
        # Filter alerts with location data
        geo_alerts = [alert for alert in alerts if alert.get('location') and 
                      alert['location'].get('latitude') and alert['location'].get('longitude')]
        
        if len(geo_alerts) < 2:
            return correlation_groups
        
        # Group by geographic proximity
        for i, alert1 in enumerate(geo_alerts):
            geo_cluster = [alert1]
            loc1 = alert1['location']
            
            for alert2 in geo_alerts[i+1:]:
                loc2 = alert2['location']
                
                # Calculate distance
                distance = self._calculate_distance(
                    loc1['latitude'], loc1['longitude'],
                    loc2['latitude'], loc2['longitude']
                )
                
                if distance <= self.geographic_threshold:
                    geo_cluster.append(alert2)
            
            if len(geo_cluster) >= 2:
                correlation_score = min(100, len(geo_cluster) * 12)
                
                correlation_groups.append({
                    'type': 'geographic',
                    'alerts': geo_cluster,
                    'score': correlation_score,
                    'geographic_radius': max(1, int(self._calculate_cluster_radius(geo_cluster))),
                    'confidence': min(100, len(geo_cluster) * 18)
                })
        
        return correlation_groups
    
    async def _behavioral_correlation(self, alerts: List[Dict]) -> List[Dict]:
        """Correlate alerts based on behavioral patterns"""
        correlation_groups = []
        
        # Group alerts by category and source
        behavior_map = defaultdict(list)
        
        for alert in alerts:
            behavior_key = f"{alert.get('category')}:{alert.get('source')}"
            behavior_map[behavior_key].append(alert)
        
        # Find behavioral patterns
        for behavior_key, behavior_alerts in behavior_map.items():
            if len(behavior_alerts) >= 3:  # Need at least 3 alerts for pattern
                # Analyze pattern characteristics
                pattern_score = await self._analyze_behavioral_pattern(behavior_alerts)
                
                if pattern_score >= 30:  # Minimum pattern score threshold
                    correlation_groups.append({
                        'type': 'behavioral',
                        'alerts': behavior_alerts,
                        'score': pattern_score,
                        'pattern': behavior_key,
                        'confidence': min(100, len(behavior_alerts) * 15)
                    })
        
        return correlation_groups
    
    async def _calculate_alert_similarity(self, alert1: Dict, alert2: Dict) -> float:
        """Calculate similarity between two alerts"""
        similarity = 0.0
        
        # Entity similarity
        entities1 = {f"{e['type']}:{e['value']}" for e in alert1.get('entities', [])}
        entities2 = {f"{e['type']}:{e['value']}" for e in alert2.get('entities', [])}
        
        if entities1 and entities2:
            entity_similarity = len(entities1.intersection(entities2)) / len(entities1.union(entities2))
            similarity += entity_similarity * 0.4
        
        # Category similarity
        if alert1.get('category') == alert2.get('category'):
            similarity += 0.3
        
        # Severity similarity
        severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        sev1 = severity_weights.get(alert1.get('severity'), 0)
        sev2 = severity_weights.get(alert2.get('severity'), 0)
        
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
