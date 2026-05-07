// Real-Time Risk Score Calculation Engine
// Revolutionary real-time risk assessment with millisecond-level updates

class RealTimeRiskEngine {
    constructor() {
        this.risk_calculator = new DynamicRiskScoringEngine();
        this.confidence_scorer = new ConfidenceScoringAI();
        this.zero_fp_correlation = new ZeroFalsePositiveCorrelation();
        this.learning_engine = new AdaptiveLearningEngine();
        
        this.realtime_data = new Map();
        this.risk_cache = new Map();
        this.calculation_queue = [];
        this.is_processing = false;
        
        this.update_interval = 100; // 100ms updates
        this.cache_ttl = 5000; // 5 seconds cache TTL
        this.batch_size = 50; // Process 50 items per batch
        
        this.performance_metrics = {
            calculations_per_second: 0,
            average_calculation_time: 0,
            cache_hit_rate: 0,
            queue_size: 0
        };
        
        this.initializeRealTimeEngine();
        this.startRealTimeProcessing();
    }

    // Initialize real-time engine
    initializeRealTimeEngine() {
        console.log('Initializing Real-Time Risk Engine...');
        
        // Set up WebSocket connections for real-time data
        this.setupWebSocketConnections();
        
        // Initialize performance monitoring
        this.initializePerformanceMonitoring();
        
        // Set up cache management
        this.initializeCacheManagement();
    }

    // Main real-time risk calculation method
    async calculateRealTimeRisk(alerts, context = {}) {
        const calculation_start = performance.now();
        
        try {
            // Generate unique calculation ID
            const calculation_id = this.generateCalculationId();
            
            // Check cache first
            const cache_key = this.generateCacheKey(alerts, context);
            const cached_result = this.getFromCache(cache_key);
            
            if (cached_result) {
                this.updatePerformanceMetrics('cache_hit');
                return {
                    ...cached_result,
                    calculation_id: calculation_id,
                    cached: true,
                    calculation_time: performance.now() - calculation_start
                };
            }
            
            // Queue calculation for real-time processing
            const calculation_promise = this.queueCalculation(calculation_id, alerts, context);
            
            // For real-time, we can also provide an immediate estimate
            const immediate_estimate = this.calculateImmediateEstimate(alerts, context);
            
            // Wait for full calculation
            const full_calculation = await calculation_promise;
            
            // Cache the result
            this.cacheResult(cache_key, full_calculation);
            
            const total_time = performance.now() - calculation_start;
            this.updatePerformanceMetrics('calculation', total_time);
            
            return {
                ...full_calculation,
                calculation_id: calculation_id,
                cached: false,
                calculation_time: total_time,
                immediate_estimate: immediate_estimate
            };
            
        } catch (error) {
            console.error('Error in real-time risk calculation:', error);
            throw error;
        }
    }

    // Queue calculation for processing
    queueCalculation(calculation_id, alerts, context) {
        return new Promise((resolve, reject) => {
            const calculation_item = {
                id: calculation_id,
                alerts: alerts,
                context: context,
                resolve: resolve,
                reject: reject,
                timestamp: Date.now(),
                priority: this.calculatePriority(alerts, context)
            };
            
            this.calculation_queue.push(calculation_item);
            this.sortQueueByPriority();
        });
    }

    // Sort queue by priority
    sortQueueByPriority() {
        this.calculation_queue.sort((a, b) => b.priority - a.priority);
    }

    // Calculate priority for queue processing
    calculatePriority(alerts, context) {
        let priority = 50; // Base priority
        
        // Higher priority for critical alerts
        const critical_alerts = alerts.filter(alert => alert.severity === 'critical');
        priority += critical_alerts.length * 20;
        
        // Higher priority for high-value assets
        if (context.asset_criticality) {
            priority += context.asset_criticality * 15;
        }
        
        // Higher priority for recent alerts
        const now = Date.now();
        const recent_alerts = alerts.filter(alert => 
            now - new Date(alert.timestamp).getTime() < 60000 // Last minute
        );
        priority += recent_alerts.length * 10;
        
        return Math.min(100, priority);
    }

    // Process calculation queue
    async processCalculationQueue() {
        if (this.is_processing || this.calculation_queue.length === 0) {
            return;
        }
        
        this.is_processing = true;
        
        try {
            const batch = this.calculation_queue.splice(0, this.batch_size);
            
            // Process batch in parallel
            const batch_promises = batch.map(item => this.processCalculationItem(item));
            const results = await Promise.allSettled(batch_promises);
            
            // Handle results
            results.forEach((result, index) => {
                const item = batch[index];
                if (result.status === 'fulfilled') {
                    item.resolve(result.value);
                } else {
                    item.reject(result.reason);
                }
            });
            
        } catch (error) {
            console.error('Error processing calculation queue:', error);
        } finally {
            this.is_processing = false;
        }
    }

    // Process individual calculation item
    async processCalculationItem(calculation_item) {
        const { alerts, context } = calculation_item;
        
        // Step 1: Correlate alerts with zero false positive approach
        const correlations = await this.zero_fp_correlation.correlateAlerts(alerts, context);
        
        // Step 2: Calculate dynamic risk scores for each correlation
        const risk_assessments = [];
        for (const correlation of correlations) {
            const risk_assessment = this.risk_calculator.calculateRiskScore(correlation, context);
            risk_assessments.push(risk_assessment);
        }
        
        // Step 3: Calculate confidence scores with explainable AI
        const confidence_assessments = [];
        for (let i = 0; i < correlations.length; i++) {
            const confidence_assessment = await this.confidence_scorer.calculateConfidence(
                correlations[i], 
                context
            );
            confidence_assessments.push(confidence_assessment);
        }
        
        // Step 4: Combine risk and confidence scores
        const combined_assessments = this.combineRiskAndConfidence(
            correlations, 
            risk_assessments, 
            confidence_assessments
        );
        
        // Step 5: Generate real-time recommendations
        const recommendations = this.generateRealTimeRecommendations(combined_assessments);
        
        return {
            correlations: correlations,
            risk_assessments: risk_assessments,
            confidence_assessments: confidence_assessments,
            combined_assessments: combined_assessments,
            recommendations: recommendations,
            timestamp: new Date().toISOString(),
            processing_time: performance.now()
        };
    }

    // Combine risk and confidence scores
    combineRiskAndConfidence(correlations, risk_assessments, confidence_assessments) {
        const combined = [];
        
        for (let i = 0; i < correlations.length; i++) {
            const risk_score = risk_assessments[i];
            const confidence_score = confidence_assessments[i];
            
            // Calculate weighted combined score
            const combined_score = (
                risk_score.total_score * 0.6 + 
                confidence_score.overall_confidence * 0.4
            );
            
            combined.push({
                correlation: correlations[i],
                risk_score: risk_score,
                confidence_score: confidence_score,
                combined_score: combined_score,
                priority_level: this.getPriorityLevel(combined_score),
                requires_immediate_action: combined_score >= 80
            });
        }
        
        // Sort by combined score (highest first)
        combined.sort((a, b) => b.combined_score - a.combined_score);
        
        return combined;
    }

    // Get priority level based on combined score
    getPriorityLevel(combined_score) {
        if (combined_score >= 90) return 'CRITICAL';
        if (combined_score >= 75) return 'HIGH';
        if (combined_score >= 60) return 'MEDIUM';
        if (combined_score >= 40) return 'LOW';
        return 'INFO';
    }

    // Generate real-time recommendations
    generateRealTimeRecommendations(combined_assessments) {
        const recommendations = [];
        
        for (const assessment of combined_assessments) {
            const recommendation = {
                correlation_id: assessment.correlation.id,
                priority: assessment.priority_level,
                actions: [],
                reasoning: []
            };
            
            // Generate actions based on risk level
            if (assessment.combined_score >= 90) {
                recommendation.actions.push({
                    type: 'immediate_response',
                    action: 'Initiate automated incident response',
                    priority: 'critical'
                });
                recommendation.actions.push({
                    type: 'notification',
                    action: 'Alert senior security team',
                    priority: 'critical'
                });
            } else if (assessment.combined_score >= 75) {
                recommendation.actions.push({
                    type: 'investigation',
                    action: 'Assign to senior analyst',
                    priority: 'high'
                });
            } else if (assessment.combined_score >= 60) {
                recommendation.actions.push({
                    type: 'monitoring',
                    action: 'Increase monitoring frequency',
                    priority: 'medium'
                });
            }
            
            // Add reasoning
            recommendation.reasoning.push(`Risk score: ${assessment.risk_score.total_score.toFixed(1)}`);
            recommendation.reasoning.push(`Confidence: ${(assessment.confidence_score.overall_confidence * 100).toFixed(1)}%`);
            recommendation.reasoning.push(`Combined: ${assessment.combined_score.toFixed(1)}`);
            
            recommendations.push(recommendation);
        }
        
        return recommendations;
    }

    // Calculate immediate estimate for real-time response
    calculateImmediateEstimate(alerts, context) {
        // Quick estimation for immediate response
        let estimated_risk = 0.0;
        let estimated_confidence = 0.7;
        
        // Base risk on alert severity
        const severity_weights = { critical: 0.9, high: 0.7, medium: 0.5, low: 0.3, info: 0.1 };
        
        for (const alert of alerts) {
            estimated_risk += severity_weights[alert.severity] || 0.5;
        }
        
        // Normalize
        estimated_risk = Math.min(100, (estimated_risk / alerts.length) * 100);
        
        // Adjust for context
        if (context.asset_criticality) {
            estimated_risk *= (1 + context.asset_criticality * 0.2);
        }
        
        return {
            estimated_risk: estimated_risk,
            estimated_confidence: estimated_confidence,
            estimated_priority: this.getPriorityLevel(estimated_risk),
            is_estimate: true
        };
    }

    // Start real-time processing loop
    startRealTimeProcessing() {
        // Process queue every update_interval
        setInterval(() => {
            this.processCalculationQueue();
        }, this.update_interval);
        
        // Update performance metrics every second
        setInterval(() => {
            this.updatePerformanceMetrics();
        }, 1000);
        
        // Clean cache every cache_ttl
        setInterval(() => {
            this.cleanCache();
        }, this.cache_ttl);
    }

    // Setup WebSocket connections
    setupWebSocketConnections() {
        // Connect to real-time data sources
        if (window.webSocketIntegration) {
            window.webSocketIntegration.messageHandlers.set('realtime_risk_update', 
                this.handleRealtimeUpdate.bind(this));
        }
    }

    // Handle real-time updates
    handleRealtimeUpdate(data) {
        const { alerts, context } = data;
        
        // Trigger real-time risk calculation
        this.calculateRealTimeRisk(alerts, context)
            .then(result => {
                // Send result back through WebSocket
                if (window.webSocketIntegration) {
                    window.webSocketIntegration.sendMessage('risk_calculation_result', result);
                }
            })
            .catch(error => {
                console.error('Error in real-time risk update:', error);
            });
    }

    // Cache management
    generateCacheKey(alerts, context) {
        const alert_hashes = alerts.map(alert => 
            `${alert.id}_${alert.timestamp}_${alert.severity}`
        ).sort().join('|');
        
        const context_hash = JSON.stringify(context);
        
        return btoa(alert_hashes + '|' + context_hash);
    }

    getFromCache(cache_key) {
        const cached = this.risk_cache.get(cache_key);
        
        if (!cached) {
            return null;
        }
        
        // Check if cache is still valid
        if (Date.now() - cached.timestamp > this.cache_ttl) {
            this.risk_cache.delete(cache_key);
            return null;
        }
        
        return cached.result;
    }

    cacheResult(cache_key, result) {
        this.risk_cache.set(cache_key, {
            result: result,
            timestamp: Date.now()
        });
    }

    cleanCache() {
        const now = Date.now();
        
        for (const [key, value] of this.risk_cache.entries()) {
            if (now - value.timestamp > this.cache_ttl) {
                this.risk_cache.delete(key);
            }
        }
    }

    // Performance monitoring
    initializePerformanceMonitoring() {
        this.performance_metrics = {
            calculations_per_second: 0,
            average_calculation_time: 0,
            cache_hit_rate: 0,
            queue_size: 0,
            total_calculations: 0,
            cache_hits: 0,
            calculation_times: []
        };
    }

    updatePerformanceMetrics(type = 'periodic', value = 0) {
        switch (type) {
            case 'calculation':
                this.performance_metrics.total_calculations++;
                this.performance_metrics.calculation_times.push(value);
                
                // Keep only last 100 calculation times
                if (this.performance_metrics.calculation_times.length > 100) {
                    this.performance_metrics.calculation_times.shift();
                }
                
                // Calculate average
                const sum = this.performance_metrics.calculation_times.reduce((a, b) => a + b, 0);
                this.performance_metrics.average_calculation_time = sum / this.performance_metrics.calculation_times.length;
                break;
                
            case 'cache_hit':
                this.performance_metrics.cache_hits++;
                break;
                
            case 'periodic':
                // Calculate calculations per second
                this.performance_metrics.calculations_per_second = this.performance_metrics.total_calculations;
                
                // Calculate cache hit rate
                const total_requests = this.performance_metrics.total_calculations + this.performance_metrics.cache_hits;
                this.performance_metrics.cache_hit_rate = total_requests > 0 ? 
                    (this.performance_metrics.cache_hits / total_requests) * 100 : 0;
                
                // Update queue size
                this.performance_metrics.queue_size = this.calculation_queue.length;
                
                // Reset counters for next period
                this.performance_metrics.total_calculations = 0;
                this.performance_metrics.cache_hits = 0;
                break;
        }
    }

    // Get performance metrics
    getPerformanceMetrics() {
        return { ...this.performance_metrics };
    }

    // Generate unique calculation ID
    generateCalculationId() {
        return `calc_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    // Get real-time status
    getRealTimeStatus() {
        return {
            is_processing: this.is_processing,
            queue_size: this.calculation_queue.length,
            cache_size: this.risk_cache.size,
            performance_metrics: this.getPerformanceMetrics(),
            uptime: Date.now() - (this.start_time || Date.now())
        };
    }

    // Emergency stop for critical situations
    emergencyStop() {
        this.is_processing = false;
        this.calculation_queue = [];
        console.warn('Real-time risk engine emergency stop activated');
    }

    // Resume processing after emergency stop
    resumeProcessing() {
        this.is_processing = false;
        console.log('Real-time risk engine resumed processing');
    }

    // Configure engine parameters
    configure(config) {
        if (config.update_interval) {
            this.update_interval = config.update_interval;
        }
        
        if (config.cache_ttl) {
            this.cache_ttl = config.cache_ttl;
        }
        
        if (config.batch_size) {
            this.batch_size = config.batch_size;
        }
        
        console.log('Real-time risk engine configuration updated:', config);
    }

    // Export engine state for backup
    exportState() {
        return {
            performance_metrics: this.performance_metrics,
            configuration: {
                update_interval: this.update_interval,
                cache_ttl: this.cache_ttl,
                batch_size: this.batch_size
            },
            cache_size: this.risk_cache.size,
            queue_size: this.calculation_queue.length
        };
    }

    // Import engine state for recovery
    importState(state) {
        if (state.configuration) {
            this.configure(state.configuration);
        }
        
        if (state.performance_metrics) {
            this.performance_metrics = { ...state.performance_metrics };
        }
        
        console.log('Real-time risk engine state imported');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealTimeRiskEngine;
}

// Global instance
window.RealTimeRiskEngine = RealTimeRiskEngine;
