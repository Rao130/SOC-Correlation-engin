"""
Real-time Correlation Engine for SOC Correlation Engine
Processes correlations in real-time as alerts are ingested
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, deque
from app.core.logging import logger
from app.core.database import get_db
from app.models.alert import AlertDocument

class RealTimeCorrelationEngine:
    """Real-time correlation processing engine"""
    
    def __init__(self):
        self.active = False
        self.correlation_task = None
        self.processing_interval = 10  # seconds
        self.correlation_window = 300  # 5 minutes window for correlations
        
        # Real-time correlation buffers
        self.alert_buffer = deque(maxlen=1000)
        self.entity_buffer = defaultdict(deque)
        self.temporal_buffer = defaultdict(deque)
        self.source_buffer = defaultdict(deque)
        self.category_buffer = defaultdict(deque)
        
        # Correlation thresholds
        self.entity_threshold = 2  # Minimum alerts for entity correlation
        self.temporal_threshold = 3  # Minimum alerts for temporal correlation
        self.source_threshold = 2  # Minimum alerts for source correlation
        self.category_threshold = 3  # Minimum alerts for category correlation
        
    async def start_correlation_processing(self):
        """Start real-time correlation processing"""
        if self.active:
            logger.warning("Correlation processing already active")
            return
            
        self.active = True
        self.correlation_task = asyncio.create_task(self._correlation_loop())
        logger.info("🚀 Real-time correlation processing started")
        
    async def stop_correlation_processing(self):
        """Stop correlation processing"""
        self.active = False
        if self.correlation_task:
            self.correlation_task.cancel()
        logger.info("🛑 Real-time correlation processing stopped")
        
    async def add_alert_for_correlation(self, alert: Dict[str, Any]):
        """Add new alert to correlation buffers"""
        try:
            self.alert_buffer.append(alert)
            
            # Add to specific correlation buffers
            await self._add_to_entity_buffer(alert)
            await self._add_to_temporal_buffer(alert)
            await self._add_to_source_buffer(alert)
            await self._add_to_category_buffer(alert)
            
            logger.debug(f"Added alert to correlation buffers: {alert.get('id', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error adding alert to correlation buffers: {e}")
            
    async def _add_to_entity_buffer(self, alert: Dict[str, Any]):
        """Add alert to entity-based correlation buffer"""
        try:
            entities = alert.get('entities', [])
            for entity in entities:
                entity_key = f"{entity.get('type')}:{entity.get('value')}"
                self.entity_buffer[entity_key].append(alert)
                
                # Keep only recent alerts within correlation window
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.correlation_window)
                self.entity_buffer[entity_key] = deque(
                    [a for a in self.entity_buffer[entity_key] 
                     if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                    maxlen=100
                )
        except Exception as e:
            logger.warning(f"Error adding alert to entity buffer: {e}")
            
    async def _add_to_temporal_buffer(self, alert: Dict[str, Any]):
        """Add alert to temporal correlation buffer"""
        try:
            timestamp = alert.get('timestamp')
            if timestamp:
                # Round to nearest minute for temporal grouping
                dt = self._parse_timestamp(timestamp)
                time_key = dt.strftime("%Y%m%d_%H%M")
                
                self.temporal_buffer[time_key].append(alert)
            
            # Keep only recent time windows
            cutoff_time = datetime.utcnow() - timedelta(seconds=self.correlation_window)
            cutoff_key = cutoff_time.strftime("%Y%m%d_%H%M")
            
            # Remove old time windows
            keys_to_remove = [k for k in self.temporal_buffer.keys() if k < cutoff_key]
            for key in keys_to_remove:
                del self.temporal_buffer[key]
        except Exception as e:
            logger.warning(f"Error adding alert to temporal buffer: {e}")
                
    async def _add_to_source_buffer(self, alert: Dict[str, Any]):
        """Add alert to source-based correlation buffer"""
        try:
            raw_data = alert.get('raw_data', {})
            source_ip = raw_data.get('source_ip')
            
            if source_ip:
                self.source_buffer[source_ip].append(alert)
                
                # Keep only recent alerts
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.correlation_window)
                self.source_buffer[source_ip] = deque(
                    [a for a in self.source_buffer[source_ip]
                     if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                    maxlen=50
                )
        except Exception as e:
            logger.warning(f"Error adding alert to source buffer: {e}")
            
    async def _add_to_category_buffer(self, alert: Dict[str, Any]):
        """Add alert to category-based correlation buffer"""
        try:
            category = alert.get('category')
            if category:
                self.category_buffer[category].append(alert)
                
                # Keep only recent alerts
                cutoff_time = datetime.utcnow() - timedelta(seconds=self.correlation_window)
                self.category_buffer[category] = deque(
                    [a for a in self.category_buffer[category]
                     if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                    maxlen=100
                )
        except Exception as e:
            logger.warning(f"Error adding alert to category buffer: {e}")
            
    async def _correlation_loop(self):
        """Main correlation processing loop"""
        while self.active:
            try:
                # Process all correlation types
                await self._process_entity_correlations()
                await self._process_temporal_correlations()
                await self._process_source_correlations()
                await self._process_category_correlations()
                
                # Clean old data from buffers
                await self._cleanup_old_data()
                
                # Wait for next processing cycle
                await asyncio.sleep(self.processing_interval)
                
            except asyncio.CancelledError:
                logger.info("Correlation processing loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in correlation processing loop: {e}")
                await asyncio.sleep(self.processing_interval)
                
    async def _process_entity_correlations(self):
        """Process entity-based correlations"""
        correlations = []
        
        for entity_key, alerts in self.entity_buffer.items():
            if len(alerts) >= self.entity_threshold:
                correlation = await self._create_entity_correlation(entity_key, list(alerts))
                if correlation:
                    correlations.append(correlation)
                    
        if correlations:
            await self._save_correlations(correlations)
            logger.info(f"Processed {len(correlations)} entity correlations")
            
    async def _process_temporal_correlations(self):
        """Process temporal correlations"""
        correlations = []
        
        for time_key, alerts in self.temporal_buffer.items():
            if len(alerts) >= self.temporal_threshold:
                correlation = await self._create_temporal_correlation(time_key, list(alerts))
                if correlation:
                    correlations.append(correlation)
                    
        if correlations:
            await self._save_correlations(correlations)
            logger.info(f"Processed {len(correlations)} temporal correlations")
            
    async def _process_source_correlations(self):
        """Process source-based correlations"""
        correlations = []
        
        for source_ip, alerts in self.source_buffer.items():
            if len(alerts) >= self.source_threshold:
                correlation = await self._create_source_correlation(source_ip, list(alerts))
                if correlation:
                    correlations.append(correlation)
                    
        if correlations:
            await self._save_correlations(correlations)
            logger.info(f"Processed {len(correlations)} source correlations")
            
    async def _process_category_correlations(self):
        """Process category-based correlations"""
        correlations = []
        
        for category, alerts in self.category_buffer.items():
            if len(alerts) >= self.category_threshold:
                correlation = await self._create_category_correlation(category, list(alerts))
                if correlation:
                    correlations.append(correlation)
                    
        if correlations:
            await self._save_correlations(correlations)
            logger.info(f"Processed {len(correlations)} category correlations")
            
    async def _create_entity_correlation(self, entity_key: str, alerts: List[Dict]) -> Optional[Dict]:
        """Create entity-based correlation"""
        try:
            entity_type, entity_value = entity_key.split(':', 1)
            
            # Calculate correlation score based on alert characteristics
            severity_scores = [self._get_severity_score(alert.get('severity', 'medium')) for alert in alerts]
            avg_severity = sum(severity_scores) / len(severity_scores)
            
            # Calculate confidence based on entity consistency and alert count
            confidence = min(95, 60 + (len(alerts) * 5) + (avg_severity * 2))
            
            # Determine status based on score
            correlation_score = min(95, 50 + (len(alerts) * 3) + avg_severity)
            status = self._get_status_from_score(correlation_score)
            
            correlation = {
                '_id': f"entity_corr_{int(time.time())}_{hash(entity_key) % 10000}",
                'name': f"Entity Correlation: {entity_type}:{entity_value} - {datetime.utcnow().strftime('%H:%M:%S')}",
                'description': f"Real-time correlation of {len(alerts)} alerts involving {entity_type} {entity_value}",
                'correlation_type': 'entity_based',
                'alert_ids': [alert.get('_id', alert.get('id', '')) for alert in alerts],
                'entities': [{'type': entity_type, 'value': entity_value}],
                'correlation_score': float(correlation_score),
                'confidence': int(confidence),
                'status': status,
                'alert_count': len(alerts),
                'entity_count': 1,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'time_window': self.correlation_window,
                'processing_type': 'real_time'
            }
            
            return correlation
            
        except Exception as e:
            logger.error(f"Error creating entity correlation: {e}")
            return None
            
    async def _create_temporal_correlation(self, time_key: str, alerts: List[Dict]) -> Optional[Dict]:
        """Create temporal correlation"""
        try:
            # Parse time key to get time window
            year, month, day, hour, minute = map(int, [time_key[:4], time_key[4:6], time_key[6:8], time_key[8:10], time_key[10:12]])
            time_window = datetime(year, month, day, hour, minute)
            
            # Calculate correlation score based on temporal density
            severity_scores = [self._get_severity_score(alert.get('severity', 'medium')) for alert in alerts]
            avg_severity = sum(severity_scores) / len(severity_scores)
            
            correlation_score = min(90, 45 + (len(alerts) * 2) + avg_severity)
            confidence = min(90, 55 + (len(alerts) * 3))
            status = self._get_status_from_score(correlation_score)
            
            correlation = {
                '_id': f"temporal_corr_{int(time.time())}_{hash(time_key) % 10000}",
                'name': f"Temporal Correlation: {time_window.strftime('%H:%M')} - {datetime.utcnow().strftime('%H:%M:%S')}",
                'description': f"Real-time cluster of {len(alerts)} alerts within 1-minute window",
                'correlation_type': 'temporal',
                'alert_ids': [alert.get('_id', alert.get('id', '')) for alert in alerts],
                'entities': [{'type': 'time_window', 'value': time_window.isoformat()}],
                'correlation_score': float(correlation_score),
                'confidence': int(confidence),
                'status': status,
                'alert_count': len(alerts),
                'entity_count': 1,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'time_window': self.correlation_window,
                'processing_type': 'real_time'
            }
            
            return correlation
            
        except Exception as e:
            logger.error(f"Error creating temporal correlation: {e}")
            return None
            
    async def _create_source_correlation(self, source_ip: str, alerts: List[Dict]) -> Optional[Dict]:
        """Create source-based correlation"""
        try:
            # Calculate correlation score based on source activity
            severity_scores = [self._get_severity_score(alert.get('severity', 'medium')) for alert in alerts]
            avg_severity = sum(severity_scores) / len(severity_scores)
            
            correlation_score = min(92, 55 + (len(alerts) * 4) + avg_severity)
            confidence = min(92, 65 + (len(alerts) * 3))
            status = self._get_status_from_score(correlation_score)
            
            correlation = {
                '_id': f"source_corr_{int(time.time())}_{hash(source_ip) % 10000}",
                'name': f"Source Correlation: {source_ip} - {datetime.utcnow().strftime('%H:%M:%S')}",
                'description': f"Real-time correlation of {len(alerts)} alerts from source {source_ip}",
                'correlation_type': 'source_based',
                'alert_ids': [alert.get('_id', alert.get('id', '')) for alert in alerts],
                'entities': [{'type': 'source_ip', 'value': source_ip}],
                'correlation_score': float(correlation_score),
                'confidence': int(confidence),
                'status': status,
                'alert_count': len(alerts),
                'entity_count': 1,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'time_window': self.correlation_window,
                'processing_type': 'real_time'
            }
            
            return correlation
            
        except Exception as e:
            logger.error(f"Error creating source correlation: {e}")
            return None
            
    async def _create_category_correlation(self, category: str, alerts: List[Dict]) -> Optional[Dict]:
        """Create category-based correlation"""
        try:
            # Calculate correlation score based on category clustering
            severity_scores = [self._get_severity_score(alert.get('severity', 'medium')) for alert in alerts]
            avg_severity = sum(severity_scores) / len(severity_scores)
            
            correlation_score = min(88, 40 + (len(alerts) * 2) + avg_severity)
            confidence = min(88, 50 + (len(alerts) * 2))
            status = self._get_status_from_score(correlation_score)
            
            correlation = {
                '_id': f"category_corr_{int(time.time())}_{hash(category) % 10000}",
                'name': f"Category Correlation: {category} - {datetime.utcnow().strftime('%H:%M:%S')}",
                'description': f"Real-time pattern of {len(alerts)} {category} attacks detected",
                'correlation_type': 'category_based',
                'alert_ids': [alert.get('_id', alert.get('id', '')) for alert in alerts],
                'entities': [{'type': 'category', 'value': category}],
                'correlation_score': float(correlation_score),
                'confidence': int(confidence),
                'status': status,
                'alert_count': len(alerts),
                'entity_count': 1,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'time_window': self.correlation_window,
                'processing_type': 'real_time'
            }
            
            return correlation
            
        except Exception as e:
            logger.error(f"Error creating category correlation: {e}")
            return None
            
    async def _save_correlations(self, correlations: List[Dict]):
        """Save correlations to database"""
        try:
            # Get database connection
            db = await get_db()
            if not db:
                logger.error("Database not available for correlation saving")
                return
                
            correlation_collection = db.get_collection("correlation_groups")
            
            # Insert correlations in batch
            if correlations:
                await correlation_collection.insert_many(correlations)
                logger.debug(f"Saved {len(correlations)} correlations to database")
                
        except Exception as e:
            logger.error(f"Error saving correlations: {e}")
            
    async def _cleanup_old_data(self):
        """Clean up old data from correlation buffers"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(seconds=self.correlation_window)
            
            # Clean entity buffer
            for entity_key in list(self.entity_buffer.keys()):
                try:
                    self.entity_buffer[entity_key] = deque(
                        [a for a in self.entity_buffer[entity_key]
                         if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                        maxlen=100
                    )
                    if not self.entity_buffer[entity_key]:
                        del self.entity_buffer[entity_key]
                except Exception as inner_e:
                    logger.warning(f"Error cleaning entity buffer for {entity_key}: {inner_e}")
                    continue
                    
            # Clean temporal buffer
            for time_key in list(self.temporal_buffer.keys()):
                try:
                    self.temporal_buffer[time_key] = deque(
                        [a for a in self.temporal_buffer[time_key]
                         if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                        maxlen=50
                    )
                    if not self.temporal_buffer[time_key]:
                        del self.temporal_buffer[time_key]
                except Exception as inner_e:
                    logger.warning(f"Error cleaning temporal buffer for {time_key}: {inner_e}")
                    continue
                    
            # Clean source buffer
            for source_ip in list(self.source_buffer.keys()):
                try:
                    self.source_buffer[source_ip] = deque(
                        [a for a in self.source_buffer[source_ip]
                         if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                        maxlen=50
                    )
                    if not self.source_buffer[source_ip]:
                        del self.source_buffer[source_ip]
                except Exception as inner_e:
                    logger.warning(f"Error cleaning source buffer for {source_ip}: {inner_e}")
                    continue
                    
            # Clean category buffer
            for category in list(self.category_buffer.keys()):
                try:
                    self.category_buffer[category] = deque(
                        [a for a in self.category_buffer[category]
                         if self._parse_timestamp(a.get('timestamp', '')) > cutoff_time],
                        maxlen=100
                    )
                    if not self.category_buffer[category]:
                        del self.category_buffer[category]
                except Exception as inner_e:
                    logger.warning(f"Error cleaning category buffer for {category}: {inner_e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string with fallback"""
        try:
            if not timestamp_str:
                return datetime.utcnow()
            
            # Try different timestamp formats
            if 'Z' in timestamp_str:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            elif '+' in timestamp_str:
                return datetime.fromisoformat(timestamp_str)
            else:
                return datetime.fromisoformat(timestamp_str)
        except Exception:
            # Fallback to current time if parsing fails
            return datetime.utcnow()
            
    def _get_severity_score(self, severity: str) -> float:
        """Convert severity to numeric score"""
        severity_scores = {
            'critical': 9.0,
            'high': 7.5,
            'medium': 5.0,
            'low': 2.5
        }
        return severity_scores.get(severity, 5.0)
        
    def _get_status_from_score(self, score: float) -> str:
        """Get status based on correlation score"""
        if score >= 85:
            return 'critical'
        elif score >= 75:
            return 'high'
        elif score >= 65:
            return 'medium'
        else:
            return 'low'
            
    async def get_correlation_statistics(self) -> Dict:
        """Get correlation processing statistics"""
        return {
            'active': self.active,
            'processing_interval': self.processing_interval,
            'correlation_window': self.correlation_window,
            'alert_buffer_size': len(self.alert_buffer),
            'entity_buffer_size': len(self.entity_buffer),
            'temporal_buffer_size': len(self.temporal_buffer),
            'source_buffer_size': len(self.source_buffer),
            'category_buffer_size': len(self.category_buffer),
            'thresholds': {
                'entity': self.entity_threshold,
                'temporal': self.temporal_threshold,
                'source': self.source_threshold,
                'category': self.category_threshold
            }
        }

# Global instance
real_time_correlation = RealTimeCorrelationEngine()
