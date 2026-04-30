"""
Business Impact Validation Service - Phase 2
Validates correlations based on business impact and criticality
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
from app.core.logging import logger

class BusinessImpactValidator:
    """Business impact validation for correlation analysis"""
    
    def __init__(self):
        self.business_rules = {
            'critical_assets': [
                'dc-01', 'db-server-01', 'file-server-01', 
                'app-server-01', 'api-gateway', 'fw-01'
            ],
            'business_hours': {
                'start': '09:00',
                'end': '17:00',
                'timezone': 'UTC'
            },
            'impact_weights': {
                'critical': 1.0,
                'high': 0.8,
                'medium': 0.6,
                'low': 0.4
            },
            'business_contexts': {
                'production': 1.0,
                'staging': 0.7,
                'development': 0.5,
                'testing': 0.3
            }
        }
        
        self.impact_thresholds = {
            'high_impact_score': 7.5,
            'critical_impact_score': 9.0,
            'business_risk_threshold': 0.7
        }
    
    async def validate(self, technical_groups: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate technical correlations for business impact"""
        validated_groups = []
        
        for group in technical_groups:
            try:
                business_validation = await self._assess_business_impact(group, context)
                
                if business_validation['is_business_relevant']:
                    validated_group = {
                        **group,
                        'business_validation': business_validation,
                        'business_confidence': business_validation['confidence'],
                        'business_impact_score': business_validation['impact_score'],
                        'business_priority': business_validation['priority']
                    }
                    validated_groups.append(validated_group)
                    logger.info(f"Business validation passed: {group.get('name', 'Unknown')}")
                else:
                    logger.info(f"Business validation filtered: {group.get('name', 'Unknown')} - Low business impact")
                    
            except Exception as e:
                logger.error(f"Business validation error: {e}")
                # Include with low confidence if validation fails
                validated_group = {
                    **group,
                    'business_validation': {'error': str(e)},
                    'business_confidence': 0.3,
                    'business_impact_score': 2.0,
                    'business_priority': 'low'
                }
                validated_groups.append(validated_group)
        
        return validated_groups
    
    async def _assess_business_impact(self, group: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess business impact of a correlation group"""
        
        # Extract entities from group
        entities = group.get('entities', [])
        alerts = group.get('alerts', [])
        
        # Calculate impact scores
        asset_impact = self._calculate_asset_impact(entities)
        timing_impact = self._calculate_timing_impact(alerts)
        severity_impact = self._calculate_severity_impact(alerts)
        context_impact = self._calculate_context_impact(context)
        
        # Calculate overall business impact score
        impact_score = (
            asset_impact * 0.35 +      # 35% weight for asset criticality
            timing_impact * 0.25 +      # 25% weight for timing
            severity_impact * 0.25 +     # 25% weight for severity
            context_impact * 0.15         # 15% weight for business context
        )
        
        # Determine business relevance
        is_business_relevant = impact_score >= self.impact_thresholds['business_risk_threshold'] * 10
        
        # Calculate confidence based on impact consistency
        confidence = self._calculate_business_confidence(impact_score, entities, alerts)
        
        # Determine priority
        priority = self._determine_business_priority(impact_score, is_business_relevant)
        
        # Generate business reasoning
        reasoning = self._generate_business_reasoning(
            asset_impact, timing_impact, severity_impact, context_impact, impact_score
        )
        
        return {
            'is_business_relevant': is_business_relevant,
            'impact_score': round(impact_score, 2),
            'confidence': round(confidence, 2),
            'priority': priority,
            'reasoning': reasoning,
            'asset_impact': asset_impact,
            'timing_impact': timing_impact,
            'severity_impact': severity_impact,
            'context_impact': context_impact,
            'validation_timestamp': datetime.utcnow().isoformat()
        }
    
    def _calculate_asset_impact(self, entities: List[Dict[str, Any]]) -> float:
        """Calculate impact based on affected assets"""
        if not entities:
            return 2.0  # Low default impact
        
        max_impact = 2.0
        
        for entity in entities:
            entity_value = entity.get('value', '').lower()
            
            # Check if entity matches critical assets
            for critical_asset in self.business_rules['critical_assets']:
                if critical_asset.lower() in entity_value:
                    max_impact = max(max_impact, 10.0)
                    break
            
            # Check for high-value asset types
            high_value_patterns = ['db', 'database', 'dc', 'domain', 'controller', 'gateway', 'firewall']
            if any(pattern in entity_value for pattern in high_value_patterns):
                max_impact = max(max_impact, 8.0)
            
            # Check for medium-value asset types
            medium_value_patterns = ['server', 'app', 'application', 'web', 'mail']
            if any(pattern in entity_value for pattern in medium_value_patterns):
                max_impact = max(max_impact, 6.0)
        
        return max_impact
    
    def _calculate_timing_impact(self, alerts: List[Dict[str, Any]]) -> float:
        """Calculate impact based on timing of alerts"""
        if not alerts:
            return 2.0
        
        current_time = datetime.utcnow()
        business_hours_impact = 0.0
        
        for alert in alerts:
            alert_time = alert.get('timestamp', current_time)
            if isinstance(alert_time, str):
                try:
                    alert_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00'))
                except:
                    continue
            
            # Check if alert occurred during business hours
            if self._is_business_hours(alert_time):
                business_hours_impact += 1.0
        
        # Calculate timing impact score
        if len(alerts) == 0:
            return 2.0
        
        business_hours_ratio = business_hours_impact / len(alerts)
        
        # Higher impact if more alerts during business hours
        if business_hours_ratio >= 0.8:
            return 10.0
        elif business_hours_ratio >= 0.6:
            return 8.0
        elif business_hours_ratio >= 0.4:
            return 6.0
        elif business_hours_ratio >= 0.2:
            return 4.0
        else:
            return 2.0
    
    def _calculate_severity_impact(self, alerts: List[Dict[str, Any]]) -> float:
        """Calculate impact based on alert severity distribution"""
        if not alerts:
            return 2.0
        
        severity_weights = self.business_rules['impact_weights']
        total_weight = 0.0
        
        for alert in alerts:
            severity = alert.get('severity', 'low').lower()
            weight = severity_weights.get(severity, 0.4)
            total_weight += weight
        
        # Calculate average severity impact
        avg_impact = total_weight / len(alerts)
        
        # Scale to 2-10 range
        return min(10.0, max(2.0, avg_impact * 10))
    
    def _calculate_context_impact(self, context: Dict[str, Any]) -> float:
        """Calculate impact based on business context"""
        context_score = 5.0  # Default medium impact
        
        # Check business context
        business_context = context.get('business_context', 'unknown').lower()
        if business_context in self.business_rules['business_contexts']:
            context_score = self.business_rules['business_contexts'][business_context] * 10
        
        # Check for special conditions
        if context.get('is_maintenance_window', False):
            context_score *= 0.5  # Reduce impact during maintenance
        
        if context.get('is_holiday_period', False):
            context_score *= 0.7  # Reduce impact during holidays
        
        if context.get('has_executive_presence', False):
            context_score *= 1.3  # Increase impact with executive presence
        
        return min(10.0, max(2.0, context_score))
    
    def _is_business_hours(self, timestamp: datetime) -> bool:
        """Check if timestamp is within business hours"""
        business_hours = self.business_rules['business_hours']
        
        # Convert to UTC time
        utc_time = timestamp
        
        # Parse business hours (simplified - assuming UTC)
        try:
            start_hour = int(business_hours['start'].split(':')[0])
            end_hour = int(business_hours['end'].split(':')[0])
            
            return start_hour <= utc_time.hour <= end_hour
        except:
            return True  # Default to business hours if parsing fails
    
    def _calculate_business_confidence(self, impact_score: float, entities: List[Dict[str, Any]], alerts: List[Dict[str, Any]]) -> float:
        """Calculate business confidence score"""
        base_confidence = min(1.0, impact_score / 10.0)
        
        # Adjust confidence based on data quality
        entity_factor = min(1.0, len(entities) / 3.0)  # More entities = higher confidence
        alert_factor = min(1.0, len(alerts) / 5.0)   # More alerts = higher confidence
        
        # Combine factors
        confidence = base_confidence * 0.6 + entity_factor * 0.2 + alert_factor * 0.2
        
        return min(1.0, max(0.1, confidence))
    
    def _determine_business_priority(self, impact_score: float, is_relevant: bool) -> str:
        """Determine business priority"""
        if not is_relevant:
            return 'low'
        
        if impact_score >= self.impact_thresholds['critical_impact_score']:
            return 'critical'
        elif impact_score >= self.impact_thresholds['high_impact_score']:
            return 'high'
        elif impact_score >= 6.0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_business_reasoning(self, asset_impact: float, timing_impact: float, 
                                   severity_impact: float, context_impact: float, 
                                   overall_score: float) -> str:
        """Generate business impact reasoning"""
        reasoning_parts = []
        
        # Asset impact reasoning
        if asset_impact >= 8.0:
            reasoning_parts.append("Critical business assets affected")
        elif asset_impact >= 6.0:
            reasoning_parts.append("Important business assets affected")
        elif asset_impact >= 4.0:
            reasoning_parts.append("Business assets affected")
        
        # Timing impact reasoning
        if timing_impact >= 8.0:
            reasoning_parts.append("Primarily during business hours")
        elif timing_impact >= 6.0:
            reasoning_parts.append("Partially during business hours")
        
        # Severity impact reasoning
        if severity_impact >= 8.0:
            reasoning_parts.append("High severity alert concentration")
        elif severity_impact >= 6.0:
            reasoning_parts.append("Medium-high severity alerts")
        
        # Context impact reasoning
        if context_impact >= 8.0:
            reasoning_parts.append("Production environment impact")
        elif context_impact >= 6.0:
            reasoning_parts.append("Business-critical context")
        
        # Overall assessment
        if overall_score >= 8.0:
            reasoning_parts.append("Overall: HIGH business impact")
        elif overall_score >= 6.0:
            reasoning_parts.append("Overall: MEDIUM business impact")
        else:
            reasoning_parts.append("Overall: LOW business impact")
        
        return "; ".join(reasoning_parts)

# Global business impact validator instance
business_impact_validator = BusinessImpactValidator()
