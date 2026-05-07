// Dynamic Risk Scoring Algorithm - World-Class Correlation Engine
// Formula: Risk Score = (Threat Intelligence × 40%) + (Asset Criticality × 25%) + (Behavioral Anomaly × 20%) + (Temporal Context × 15%)

class DynamicRiskScoringEngine {
    constructor() {
        this.weights = {
            threat_intelligence: 0.40,
            asset_criticality: 0.25,
            behavioral_anomaly: 0.20,
            temporal_context: 0.15
        };
        
        this.threat_intelligence_db = new Map();
        this.asset_criticality_map = new Map();
        this.behavioral_baselines = new Map();
        this.temporal_patterns = new Map();
        
        this.initializeThreatIntelligence();
        this.initializeAssetCriticality();
        this.initializeBehavioralBaselines();
        this.initializeTemporalPatterns();
    }

    // Calculate comprehensive risk score
    calculateRiskScore(alert, context = {}) {
        const threat_score = this.calculateThreatIntelligenceScore(alert, context);
        const asset_score = this.calculateAssetCriticalityScore(alert, context);
        const behavior_score = this.calculateBehavioralAnomalyScore(alert, context);
        const temporal_score = this.calculateTemporalContextScore(alert, context);
        
        const risk_score = (
            threat_score * this.weights.threat_intelligence +
            asset_score * this.weights.asset_criticality +
            behavior_score * this.weights.behavioral_anomaly +
            temporal_score * this.weights.temporal_context
        );
        
        return {
            total_score: Math.min(100, Math.max(0, risk_score)),
            breakdown: {
                threat_intelligence: threat_score,
                asset_criticality: asset_score,
                behavioral_anomaly: behavior_score,
                temporal_context: temporal_score
            },
            risk_level: this.getRiskLevel(risk_score),
            confidence: this.calculateConfidence(threat_score, asset_score, behavior_score, temporal_score),
            reasoning: this.generateReasoning(alert, context, threat_score, asset_score, behavior_score, temporal_score)
        };
    }

    // Threat Intelligence Scoring (40% weight)
    calculateThreatIntelligenceScore(alert, context) {
        let score = 0;
        
        // Known malicious indicators
        if (alert.indicators) {
            alert.indicators.forEach(indicator => {
                const threat_data = this.threat_intelligence_db.get(indicator);
                if (threat_data) {
                    score += threat_data.severity_score * 0.3;
                }
            });
        }
        
        // MITRE ATT&CK technique severity
        if (alert.mitre_technique) {
            const technique_score = this.getMITRETechniqueScore(alert.mitre_technique);
            score += technique_score * 0.4;
        }
        
        // Threat intelligence feeds
        if (context.threat_feeds) {
            context.threat_feeds.forEach(feed => {
                if (feed.matches_alert) {
                    score += feed.confidence * 0.3;
                }
            });
        }
        
        return Math.min(100, score * 100);
    }

    // Asset Criticality Scoring (25% weight)
    calculateAssetCriticalityScore(alert, context) {
        const asset_id = alert.target_asset || context.asset_id;
        const asset_data = this.asset_criticality_map.get(asset_id);
        
        if (!asset_data) return 30; // Default medium score
        
        let score = 0;
        
        // Business criticality
        score += asset_data.business_criticality * 0.4;
        
        // Data sensitivity
        score += asset_data.data_sensitivity * 0.3;
        
        // Service availability impact
        score += asset_data.availability_impact * 0.2;
        
        // Compliance requirements
        score += asset_data.compliance_criticality * 0.1;
        
        return Math.min(100, score);
    }

    // Behavioral Anomaly Scoring (20% weight)
    calculateBehavioralAnomalyScore(alert, context) {
        const entity_id = alert.source_entity || context.entity_id;
        const baseline = this.behavioral_baselines.get(entity_id);
        
        if (!baseline) return 25; // Default low-medium score
        
        let anomaly_score = 0;
        
        // Time-based anomaly
        const current_hour = new Date().getHours();
        if (!baseline.active_hours.includes(current_hour)) {
            anomaly_score += 30;
        }
        
        // Geographic anomaly
        if (alert.location && !baseline.common_locations.includes(alert.location)) {
            anomaly_score += 25;
        }
        
        // Access pattern anomaly
        if (alert.access_pattern && !baseline.normal_access_patterns.includes(alert.access_pattern)) {
            anomaly_score += 25;
        }
        
        // Volume anomaly
        if (alert.volume && alert.volume > baseline.normal_volume_threshold * 2) {
            anomaly_score += 20;
        }
        
        return Math.min(100, anomaly_score);
    }

    // Temporal Context Scoring (15% weight)
    calculateTemporalContextScore(alert, context) {
        let score = 0;
        const now = new Date();
        
        // Business hours vs off-hours
        const hour = now.getHours();
        if (hour < 6 || hour > 22) {
            score += 40; // Higher risk during off-hours
        } else if (hour >= 9 && hour <= 17) {
            score += 10; // Lower risk during business hours
        } else {
            score += 25; // Medium risk during transition hours
        }
        
        // Weekend vs weekday
        if (now.getDay() === 0 || now.getDay() === 6) {
            score += 30; // Higher risk on weekends
        }
        
        // Holiday season
        if (this.isHolidaySeason(now)) {
            score += 20; // Higher risk during holidays
        }
        
        // Recent security events
        if (context.recent_incidents && context.recent_incidents.length > 0) {
            const recent_incident_score = Math.min(30, context.recent_incidents.length * 10);
            score += recent_incident_score;
        }
        
        // Maintenance windows
        if (this.isMaintenanceWindow(now)) {
            score -= 20; // Lower risk during scheduled maintenance
        }
        
        return Math.min(100, Math.max(0, score));
    }

    // Get risk level classification
    getRiskLevel(score) {
        if (score >= 80) return 'CRITICAL';
        if (score >= 60) return 'HIGH';
        if (score >= 40) return 'MEDIUM';
        if (score >= 20) return 'LOW';
        return 'INFO';
    }

    // Calculate confidence in the risk score
    calculateConfidence(threat, asset, behavior, temporal) {
        const data_completeness = this.assessDataCompleteness(threat, asset, behavior, temporal);
        const consistency_score = this.assessConsistency(threat, asset, behavior, temporal);
        const historical_accuracy = this.getHistoricalAccuracy();
        
        return (data_completeness * 0.4 + consistency_score * 0.3 + historical_accuracy * 0.3);
    }

    // Generate explainable reasoning
    generateReasoning(alert, context, threat_score, asset_score, behavior_score, temporal_score) {
        const reasoning = [];
        
        if (threat_score > 70) {
            reasoning.push(`High threat intelligence score (${threat_score.toFixed(1)}) indicates known malicious activity`);
        }
        
        if (asset_score > 70) {
            reasoning.push(`Target asset has high criticality (${asset_score.toFixed(1)}) - potential significant business impact`);
        }
        
        if (behavior_score > 60) {
            reasoning.push(`Behavioral anomaly detected (${behavior_score.toFixed(1)}) - unusual activity pattern`);
        }
        
        if (temporal_score > 60) {
            reasoning.push(`Suspicious timing (${temporal_score.toFixed(1)}) - activity during unusual hours`);
        }
        
        return reasoning.join('; ');
    }

    // Initialize threat intelligence database
    initializeThreatIntelligence() {
        // Sample threat intelligence data
        this.threat_intelligence_db.set('malicious_ip_1', { severity_score: 0.9, type: 'ip' });
        this.threat_intelligence_db.set('malicious_domain_1', { severity_score: 0.8, type: 'domain' });
        this.threat_intelligence_db.set('known_malware_hash', { severity_score: 0.95, type: 'hash' });
    }

    // Initialize asset criticality mapping
    initializeAssetCriticality() {
        // Sample asset data
        this.asset_criticality_map.set('database_server', {
            business_criticality: 0.9,
            data_sensitivity: 0.95,
            availability_impact: 0.85,
            compliance_criticality: 0.8
        });
        
        this.asset_criticality_map.set('web_server', {
            business_criticality: 0.7,
            data_sensitivity: 0.6,
            availability_impact: 0.8,
            compliance_criticality: 0.5
        });
    }

    // Initialize behavioral baselines
    initializeBehavioralBaselines() {
        // Sample behavioral baseline
        this.behavioral_baselines.set('user_1', {
            active_hours: [9, 10, 11, 14, 15, 16, 17],
            common_locations: ['office', 'vpn'],
            normal_access_patterns: ['normal_login', 'file_access'],
            normal_volume_threshold: 100
        });
    }

    // Initialize temporal patterns
    initializeTemporalPatterns() {
        // Store temporal patterns for analysis
        this.temporal_patterns.set('attack_patterns', {
            peak_hours: [2, 3, 4, 14, 15],
            peak_days: [0, 6], // Weekend
            seasonal_patterns: ['holiday_season', 'summer_break']
        });
    }

    // Helper methods
    getMITRETechniqueScore(technique) {
        const technique_scores = {
            'T1078': 0.8, // Valid Accounts
            'T1059': 0.7, // Command and Scripting Interpreter
            'T1046': 0.9, // Network Service Scanning
            'T1075': 0.8, // Pass the Hash
            'T1566': 0.9, // Phishing
            'T1190': 0.95, // Exploit Public-Facing Application
            'T1071': 0.6, // Application Layer Protocol
            'T1041': 0.7, // Exfiltration Over C2 Channel
            'T1020': 0.8, // Automated Exfiltration
            'T1033': 0.9  // System Owner/User Discovery
        };
        return technique_scores[technique] || 0.5;
    }

    isHolidaySeason(date) {
        const month = date.getMonth();
        return month === 11 || month === 0; // December or January
    }

    isMaintenanceWindow(date) {
        const hour = date.getHours();
        const day = date.getDay();
        // Example: Sunday 2-4 AM maintenance window
        return day === 0 && hour >= 2 && hour <= 4;
    }

    assessDataCompleteness(threat, asset, behavior, temporal) {
        const factors = [threat, asset, behavior, temporal];
        const available_factors = factors.filter(f => f > 0).length;
        return (available_factors / factors.length) * 100;
    }

    assessConsistency(threat, asset, behavior, temporal) {
        // Check if scores are logically consistent
        const avg_score = (threat + asset + behavior + temporal) / 4;
        const variance = Math.sqrt(
            Math.pow(threat - avg_score, 2) +
            Math.pow(asset - avg_score, 2) +
            Math.pow(behavior - avg_score, 2) +
            Math.pow(temporal - avg_score, 2)
        ) / 4;
        
        // Lower variance = higher consistency
        return Math.max(0, 100 - variance * 2);
    }

    getHistoricalAccuracy() {
        // This would be calculated from historical predictions vs actual outcomes
        return 85; // Placeholder - would be calculated from historical data
    }

    // Update threat intelligence in real-time
    updateThreatIntelligence(indicator, data) {
        this.threat_intelligence_db.set(indicator, data);
    }

    // Update asset criticality
    updateAssetCriticality(asset_id, data) {
        this.asset_criticality_map.set(asset_id, data);
    }

    // Update behavioral baseline
    updateBehavioralBaseline(entity_id, data) {
        this.behavioral_baselines.set(entity_id, data);
    }

    // Get real-time risk assessment
    getRealTimeRiskAssessment(alert, context) {
        const risk_assessment = this.calculateRiskScore(alert, context);
        
        // Add real-time context
        risk_assessment.real_time_factors = {
            current_load: this.getCurrentSystemLoad(),
            active_incidents: this.getActiveIncidents(),
            analyst_availability: this.getAnalystAvailability(),
            recent_changes: this.getRecentSystemChanges()
        };
        
        return risk_assessment;
    }

    getCurrentSystemLoad() {
        // Would get actual system metrics
        return Math.random() * 100;
    }

    getActiveIncidents() {
        // Would get actual active incident count
        return Math.floor(Math.random() * 10);
    }

    getAnalystAvailability() {
        // Would get actual analyst availability
        return Math.random() * 100;
    }

    getRecentSystemChanges() {
        // Would get recent system changes
        return Math.random() > 0.5 ? ['config_update', 'new_deployment'] : [];
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DynamicRiskScoringEngine;
}

// Global instance
window.DynamicRiskScoringEngine = DynamicRiskScoringEngine;
