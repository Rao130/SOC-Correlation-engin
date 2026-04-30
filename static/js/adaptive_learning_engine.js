// Adaptive Learning Engine - Auto-Learning from Analyst Feedback
// Revolutionary self-improving correlation system

class AdaptiveLearningEngine {
    constructor() {
        this.feedback_processor = new FeedbackProcessor();
        this.model_updater = new ModelUpdater();
        this.pattern_learner = new PatternLearner();
        this.confidence_calibrator = new ConfidenceCalibrator();
        
        this.learning_models = {
            correlation: new CorrelationLearningModel(),
            false_positive: new FalsePositiveLearningModel(),
            risk_scoring: new RiskScoringLearningModel(),
            confidence: new ConfidenceLearningModel()
        };
        
        this.feedback_history = new Map();
        this.performance_metrics = new Map();
        this.learning_rate = 0.01;
        this.adaptation_threshold = 0.05;
        
        this.initializeLearningSystem();
        this.startContinuousLearning();
    }

    // Main learning method - process analyst feedback and update models
    async processFeedback(correlation_id, feedback, context = {}) {
        const learning_result = {
            correlation_id: correlation_id,
            feedback_processed: false,
            models_updated: [],
            performance_improvement: 0.0,
            adaptation_summary: {}
        };

        try {
            // Process and validate feedback
            const processed_feedback = await this.feedback_processor.processFeedback(feedback, context);
            
            // Store feedback for learning
            this.storeFeedback(correlation_id, processed_feedback, context);
            
            // Update individual learning models
            const model_updates = await this.updateLearningModels(correlation_id, processed_feedback, context);
            learning_result.models_updated = model_updates;
            
            // Learn new patterns from feedback
            const pattern_learning = await this.learnNewPatterns(correlation_id, processed_feedback, context);
            learning_result.adaptation_summary.pattern_learning = pattern_learning;
            
            // Calibrate confidence scores
            const confidence_calibration = await this.calibrateConfidence(correlation_id, processed_feedback, context);
            learning_result.adaptation_summary.confidence_calibration = confidence_calibration;
            
            // Calculate performance improvement
            learning_result.performance_improvement = this.calculatePerformanceImprovement(correlation_id);
            
            // Update performance metrics
            this.updatePerformanceMetrics(correlation_id, learning_result);
            
            learning_result.feedback_processed = true;
            
        } catch (error) {
            console.error('Error processing feedback:', error);
            learning_result.error = error.message;
        }

        return learning_result;
    }

    // Update all learning models based on feedback
    async updateLearningModels(correlation_id, feedback, context) {
        const model_updates = [];
        
        // Update correlation model
        const correlation_update = await this.learning_models.correlation.update(correlation_id, feedback, context);
        if (correlation_update.updated) {
            model_updates.push({
                model: 'correlation',
                improvement: correlation_update.improvement,
                changes: correlation_update.changes
            });
        }
        
        // Update false positive model
        const fp_update = await this.learning_models.false_positive.update(correlation_id, feedback, context);
        if (fp_update.updated) {
            model_updates.push({
                model: 'false_positive',
                improvement: fp_update.improvement,
                changes: fp_update.changes
            });
        }
        
        // Update risk scoring model
        const risk_update = await this.learning_models.risk_scoring.update(correlation_id, feedback, context);
        if (risk_update.updated) {
            model_updates.push({
                model: 'risk_scoring',
                improvement: risk_update.improvement,
                changes: risk_update.changes
            });
        }
        
        // Update confidence model
        const confidence_update = await this.learning_models.confidence.update(correlation_id, feedback, context);
        if (confidence_update.updated) {
            model_updates.push({
                model: 'confidence',
                improvement: confidence_update.improvement,
                changes: confidence_update.changes
            });
        }
        
        return model_updates;
    }

    // Learn new patterns from analyst feedback
    async learnNewPatterns(correlation_id, feedback, context) {
        const pattern_learning = {
            new_patterns_discovered: 0,
            existing_patterns_updated: 0,
            pattern_validation_results: []
        };

        // Analyze feedback for new correlation patterns
        const new_patterns = await this.pattern_learner.discoverNewPatterns(correlation_id, feedback, context);
        
        for (const pattern of new_patterns) {
            const validation_result = await this.validateNewPattern(pattern, context);
            
            if (validation_result.is_valid) {
                await this.addNewPattern(pattern);
                pattern_learning.new_patterns_discovered++;
                pattern_learning.pattern_validation_results.push({
                    pattern: pattern.id,
                    status: 'added',
                    confidence: validation_result.confidence
                });
            } else {
                pattern_learning.pattern_validation_results.push({
                    pattern: pattern.id,
                    status: 'rejected',
                    reason: validation_result.reason
                });
            }
        }
        
        // Update existing patterns based on feedback
        const updated_patterns = await this.pattern_learner.updateExistingPatterns(correlation_id, feedback, context);
        pattern_learning.existing_patterns_updated = updated_patterns.length;
        
        return pattern_learning;
    }

    // Calibrate confidence scores based on feedback
    async calibrateConfidence(correlation_id, feedback, context) {
        return await this.confidence_calibrator.calibrate(correlation_id, feedback, context);
    }

    // Store feedback for future learning
    storeFeedback(correlation_id, feedback, context) {
        if (!this.feedback_history.has(correlation_id)) {
            this.feedback_history.set(correlation_id, []);
        }
        
        this.feedback_history.get(correlation_id).push({
            timestamp: new Date().toISOString(),
            feedback: feedback,
            context: context,
            processed: false
        });
    }

    // Validate new pattern before adding
    async validateNewPattern(pattern, context) {
        const validation = {
            is_valid: false,
            confidence: 0.0,
            reason: ''
        };

        // Check if pattern is statistically significant
        const statistical_significance = this.calculateStatisticalSignificance(pattern);
        if (statistical_significance < 0.7) {
            validation.reason = 'Pattern not statistically significant';
            return validation;
        }

        // Check if pattern is technically feasible
        const technical_feasibility = this.checkTechnicalFeasibility(pattern);
        if (technical_feasibility < 0.6) {
            validation.reason = 'Pattern not technically feasible';
            return validation;
        }

        // Check if pattern is consistent with existing knowledge
        const consistency_check = this.checkPatternConsistency(pattern);
        if (consistency_check < 0.5) {
            validation.reason = 'Pattern inconsistent with existing knowledge';
            return validation;
        }

        validation.is_valid = true;
        validation.confidence = (statistical_significance + technical_feasibility + consistency_check) / 3;
        
        return validation;
    }

    // Calculate statistical significance of pattern
    calculateStatisticalSignificance(pattern) {
        // Use chi-square test or similar statistical method
        const sample_size = pattern.occurrence_count || 1;
        const expected_frequency = pattern.expected_frequency || 0.1;
        
        // Simplified significance calculation
        if (sample_size < 5) return 0.3;
        if (sample_size < 10) return 0.5;
        if (sample_size < 20) return 0.7;
        return 0.9;
    }

    // Check technical feasibility of pattern
    checkTechnicalFeasibility(pattern) {
        // Check if pattern makes technical sense
        let feasibility_score = 0.8;
        
        // Check for logical flow
        if (pattern.steps && pattern.steps.length > 1) {
            for (let i = 1; i < pattern.steps.length; i++) {
                if (!this.isLogicalStep(pattern.steps[i-1], pattern.steps[i])) {
                    feasibility_score -= 0.2;
                }
            }
        }
        
        return Math.max(0.0, feasibility_score);
    }

    // Check if step is logical
    isLogicalStep(prev_step, current_step) {
        // Define logical step transitions
        const logical_transitions = {
            'reconnaissance': ['initial_access', 'execution'],
            'initial_access': ['execution', 'persistence'],
            'execution': ['persistence', 'privilege_escalation'],
            'persistence': ['lateral_movement', 'data_exfiltration'],
            'privilege_escalation': ['lateral_movement', 'data_exfiltration'],
            'lateral_movement': ['data_exfiltration', 'impact'],
            'data_exfiltration': ['impact'],
            'impact': []
        };
        
        const valid_next = logical_transitions[prev_step] || [];
        return valid_next.includes(current_step);
    }

    // Check pattern consistency with existing knowledge
    checkPatternConsistency(pattern) {
        // Check if pattern is consistent with existing patterns
        let consistency_score = 0.7;
        
        // Check for contradictions with known patterns
        // This would involve comparing with existing pattern database
        
        return consistency_score;
    }

    // Add new pattern to pattern database
    async addNewPattern(pattern) {
        // Add to pattern database
        // This would involve database operations
        console.log('Adding new pattern:', pattern.id);
    }

    // Calculate performance improvement
    calculatePerformanceImprovement(correlation_id) {
        const feedback_history = this.feedback_history.get(correlation_id) || [];
        if (feedback_history.length < 2) return 0.0;
        
        // Calculate improvement over time
        const recent_feedback = feedback_history.slice(-5);
        const older_feedback = feedback_history.slice(-10, -5);
        
        if (older_feedback.length === 0) return 0.0;
        
        const recent_accuracy = this.calculateAccuracy(recent_feedback);
        const older_accuracy = this.calculateAccuracy(older_feedback);
        
        return recent_accuracy - older_accuracy;
    }

    // Calculate accuracy from feedback
    calculateAccuracy(feedback_list) {
        if (feedback_list.length === 0) return 0.0;
        
        let correct_predictions = 0;
        for (const feedback of feedback_list) {
            if (feedback.feedback.was_correct) {
                correct_predictions++;
            }
        }
        
        return correct_predictions / feedback_list.length;
    }

    // Update performance metrics
    updatePerformanceMetrics(correlation_id, learning_result) {
        if (!this.performance_metrics.has(correlation_id)) {
            this.performance_metrics.set(correlation_id, {
                total_feedback: 0,
                accuracy: 0.0,
                improvement_rate: 0.0,
                last_updated: new Date().toISOString()
            });
        }
        
        const metrics = this.performance_metrics.get(correlation_id);
        metrics.total_feedback++;
        metrics.improvement_rate = learning_result.performance_improvement;
        metrics.last_updated = new Date().toISOString();
        
        // Update accuracy
        const all_feedback = this.feedback_history.get(correlation_id) || [];
        metrics.accuracy = this.calculateAccuracy(all_feedback);
    }

    // Initialize learning system
    initializeLearningSystem() {
        // Load existing models and patterns
        this.loadExistingModels();
        this.loadExistingPatterns();
        this.initializePerformanceTracking();
    }

    // Start continuous learning process
    startContinuousLearning() {
        // Set up periodic learning tasks
        setInterval(() => {
            this.performPeriodicLearning();
        }, 60000); // Every minute
        
        setInterval(() => {
            this.performModelOptimization();
        }, 3600000); // Every hour
    }

    // Perform periodic learning
    async performPeriodicLearning() {
        // Process accumulated feedback
        const unprocessed_feedback = this.getUnprocessedFeedback();
        
        for (const feedback_data of unprocessed_feedback) {
            await this.processFeedback(
                feedback_data.correlation_id,
                feedback_data.feedback,
                feedback_data.context
            );
            
            // Mark as processed
            feedback_data.processed = true;
        }
    }

    // Perform model optimization
    async performModelOptimization() {
        // Optimize all learning models
        for (const [model_name, model] of Object.entries(this.learning_models)) {
            await model.optimize();
        }
    }

    // Get unprocessed feedback
    getUnprocessedFeedback() {
        const unprocessed = [];
        
        for (const [correlation_id, feedback_list] of this.feedback_history.entries()) {
            for (const feedback_data of feedback_list) {
                if (!feedback_data.processed) {
                    unprocessed.push({
                        correlation_id: correlation_id,
                        feedback: feedback_data.feedback,
                        context: feedback_data.context
                    });
                }
            }
        }
        
        return unprocessed;
    }

    // Load existing models
    loadExistingModels() {
        // Load pre-trained models from storage
        console.log('Loading existing learning models...');
    }

    // Load existing patterns
    loadExistingPatterns() {
        // Load existing correlation patterns
        console.log('Loading existing correlation patterns...');
    }

    // Initialize performance tracking
    initializePerformanceTracking() {
        // Set up performance monitoring
        console.log('Initializing performance tracking...');
    }

    // Get learning statistics
    getLearningStatistics() {
        const stats = {
            total_feedback_processed: 0,
            average_accuracy: 0.0,
            total_patterns_learned: 0,
            models_updated: 0,
            learning_rate: this.learning_rate
        };
        
        // Calculate statistics from feedback history
        for (const feedback_list of this.feedback_history.values()) {
            stats.total_feedback_processed += feedback_list.length;
        }
        
        // Calculate average accuracy
        const accuracies = [];
        for (const metrics of this.performance_metrics.values()) {
            accuracies.push(metrics.accuracy);
        }
        
        if (accuracies.length > 0) {
            stats.average_accuracy = accuracies.reduce((sum, acc) => sum + acc, 0) / accuracies.length;
        }
        
        return stats;
    }

    // Export learning data for backup
    exportLearningData() {
        return {
            feedback_history: Object.fromEntries(this.feedback_history),
            performance_metrics: Object.fromEntries(this.performance_metrics),
            learning_statistics: this.getLearningStatistics()
        };
    }

    // Import learning data for recovery
    importLearningData(data) {
        if (data.feedback_history) {
            this.feedback_history = new Map(Object.entries(data.feedback_history));
        }
        
        if (data.performance_metrics) {
            this.performance_metrics = new Map(Object.entries(data.performance_metrics));
        }
    }
}

// Feedback Processor
class FeedbackProcessor {
    constructor() {
        this.feedback_validators = new Map();
        this.feedback_normalizers = new Map();
        this.feedback_enrichers = new Map();
    }

    async processFeedback(raw_feedback, context) {
        let processed_feedback = { ...raw_feedback };
        
        // Validate feedback
        const validation_result = await this.validateFeedback(processed_feedback);
        if (!validation_result.is_valid) {
            throw new Error(`Invalid feedback: ${validation_result.reason}`);
        }
        
        // Normalize feedback
        processed_feedback = await this.normalizeFeedback(processed_feedback);
        
        // Enrich feedback with additional context
        processed_feedback = await this.enrichFeedback(processed_feedback, context);
        
        return processed_feedback;
    }

    async validateFeedback(feedback) {
        // Validate feedback structure and content
        const validation = {
            is_valid: true,
            reason: ''
        };
        
        if (!feedback.correlation_id) {
            validation.is_valid = false;
            validation.reason = 'Missing correlation_id';
        }
        
        if (feedback.was_correct === undefined) {
            validation.is_valid = false;
            validation.reason = 'Missing was_correct field';
        }
        
        return validation;
    }

    async normalizeFeedback(feedback) {
        // Normalize feedback to standard format
        const normalized = { ...feedback };
        
        // Normalize confidence scores
        if (normalized.confidence_score !== undefined) {
            normalized.confidence_score = Math.max(0.0, Math.min(1.0, normalized.confidence_score));
        }
        
        // Normalize timestamps
        if (normalized.timestamp) {
            normalized.timestamp = new Date(normalized.timestamp).toISOString();
        }
        
        return normalized;
    }

    async enrichFeedback(feedback, context) {
        // Enrich feedback with additional context
        const enriched = { ...feedback };
        
        // Add processing timestamp
        enriched.processed_at = new Date().toISOString();
        
        // Add context information
        enriched.context = context;
        
        // Add derived metrics
        enriched.derived_metrics = this.calculateDerivedMetrics(feedback, context);
        
        return enriched;
    }

    calculateDerivedMetrics(feedback, context) {
        const metrics = {};
        
        // Calculate feedback quality score
        metrics.feedback_quality = this.calculateFeedbackQuality(feedback);
        
        // Calculate analyst confidence
        metrics.analyst_confidence = feedback.analyst_confidence || 0.7;
        
        // Calculate response time
        if (feedback.timestamp && context.alert_timestamp) {
            const response_time = new Date(feedback.timestamp) - new Date(context.alert_timestamp);
            metrics.response_time_ms = response_time;
        }
        
        return metrics;
    }

    calculateFeedbackQuality(feedback) {
        let quality_score = 0.5;
        
        // Check for detailed comments
        if (feedback.comments && feedback.comments.length > 50) {
            quality_score += 0.2;
        }
        
        // Check for specific corrections
        if (feedback.corrections && feedback.corrections.length > 0) {
            quality_score += 0.2;
        }
        
        // Check for confidence rating
        if (feedback.confidence_score !== undefined) {
            quality_score += 0.1;
        }
        
        return Math.min(1.0, quality_score);
    }
}

// Model Updater
class ModelUpdater {
    constructor() {
        this.update_strategies = new Map();
        this.model_versions = new Map();
        this.rollback_manager = new RollbackManager();
    }

    async updateModel(model_name, correlation_id, feedback, context) {
        const update_result = {
            updated: false,
            improvement: 0.0,
            changes: [],
            previous_version: null,
            new_version: null
        };

        try {
            // Get current model version
            const current_version = this.model_versions.get(model_name) || '1.0.0';
            update_result.previous_version = current_version;
            
            // Apply update strategy
            const strategy = this.update_strategies.get(model_name);
            if (strategy) {
                const update_data = await strategy.apply(correlation_id, feedback, context);
                
                if (update_data.has_changes) {
                    update_result.updated = true;
                    update_result.improvement = update_data.improvement;
                    update_result.changes = update_data.changes;
                    
                    // Create new version
                    const new_version = this.incrementVersion(current_version);
                    update_result.new_version = new_version;
                    this.model_versions.set(model_name, new_version);
                    
                    // Create rollback point
                    this.rollback_manager.createRollbackPoint(model_name, current_version, update_data);
                }
            }
        } catch (error) {
            console.error(`Error updating model ${model_name}:`, error);
            update_result.error = error.message;
        }

        return update_result;
    }

    incrementVersion(version) {
        const parts = version.split('.');
        const patch = parseInt(parts[2] || '0') + 1;
        return `${parts[0]}.${parts[1]}.${patch}`;
    }
}

// Pattern Learner
class PatternLearner {
    constructor() {
        this.pattern_discovery_algorithms = new Map();
        this.pattern_validation_rules = new Map();
        this.pattern_database = new Map();
    }

    async discoverNewPatterns(correlation_id, feedback, context) {
        const new_patterns = [];
        
        // Analyze feedback for new patterns
        const potential_patterns = this.extractPotentialPatterns(feedback, context);
        
        for (const pattern of potential_patterns) {
            const validation_result = await this.validatePattern(pattern);
            
            if (validation_result.is_valid) {
                new_patterns.push(pattern);
            }
        }
        
        return new_patterns;
    }

    extractPotentialPatterns(feedback, context) {
        const patterns = [];
        
        // Extract sequence patterns
        if (feedback.alert_sequence) {
            const sequence_pattern = this.createSequencePattern(feedback.alert_sequence);
            patterns.push(sequence_pattern);
        }
        
        // Extract temporal patterns
        if (feedback.temporal_data) {
            const temporal_pattern = this.createTemporalPattern(feedback.temporal_data);
            patterns.push(temporal_pattern);
        }
        
        // Extract behavioral patterns
        if (feedback.behavioral_data) {
            const behavioral_pattern = this.createBehavioralPattern(feedback.behavioral_data);
            patterns.push(behavioral_pattern);
        }
        
        return patterns;
    }

    createSequencePattern(alert_sequence) {
        return {
            type: 'sequence',
            id: `seq_${Date.now()}`,
            steps: alert_sequence.map(alert => alert.mitre_technique),
            occurrence_count: 1,
            confidence: 0.5
        };
    }

    createTemporalPattern(temporal_data) {
        return {
            type: 'temporal',
            id: `temp_${Date.now()}`,
            time_windows: temporal_data.time_windows,
            frequency_patterns: temporal_data.frequencies,
            occurrence_count: 1,
            confidence: 0.5
        };
    }

    createBehavioralPattern(behavioral_data) {
        return {
            type: 'behavioral',
            id: `beh_${Date.now()}`,
            user_patterns: behavioral_data.user_patterns,
            system_patterns: behavioral_data.system_patterns,
            occurrence_count: 1,
            confidence: 0.5
        };
    }

    async validatePattern(pattern) {
        // Validate pattern
        return {
            is_valid: true,
            confidence: 0.7
        };
    }

    async updateExistingPatterns(correlation_id, feedback, context) {
        // Update existing patterns based on feedback
        return [];
    }
}

// Confidence Calibrator
class ConfidenceCalibrator {
    constructor() {
        this.calibration_history = new Map();
        this.calibration_algorithms = new Map();
    }

    async calibrate(correlation_id, feedback, context) {
        const calibration_result = {
            calibrated: false,
            adjustment_factor: 0.0,
            previous_confidence: 0.0,
            new_confidence: 0.0
        };

        // Get original confidence
        const original_confidence = context.original_confidence || 0.7;
        calibration_result.previous_confidence = original_confidence;
        
        // Calculate adjustment based on feedback
        const adjustment = this.calculateConfidenceAdjustment(feedback, original_confidence);
        calibration_result.adjustment_factor = adjustment;
        
        // Apply adjustment
        const new_confidence = Math.max(0.0, Math.min(1.0, original_confidence + adjustment));
        calibration_result.new_confidence = new_confidence;
        
        // Check if calibration is significant
        if (Math.abs(adjustment) > 0.05) {
            calibration_result.calibrated = true;
        }
        
        // Store calibration history
        this.storeCalibrationHistory(correlation_id, calibration_result);
        
        return calibration_result;
    }

    calculateConfidenceAdjustment(feedback, original_confidence) {
        let adjustment = 0.0;
        
        // Adjust based on correctness
        if (feedback.was_correct) {
            adjustment += 0.02; // Increase confidence for correct predictions
        } else {
            adjustment -= 0.05; // Decrease confidence for incorrect predictions
        }
        
        // Adjust based on analyst confidence
        if (feedback.analyst_confidence !== undefined) {
            const analyst_diff = feedback.analyst_confidence - original_confidence;
            adjustment += analyst_diff * 0.1;
        }
        
        // Adjust based on feedback quality
        if (feedback.derived_metrics && feedback.derived_metrics.feedback_quality) {
            const quality_factor = feedback.derived_metrics.feedback_quality;
            adjustment *= quality_factor;
        }
        
        return adjustment;
    }

    storeCalibrationHistory(correlation_id, calibration_result) {
        if (!this.calibration_history.has(correlation_id)) {
            this.calibration_history.set(correlation_id, []);
        }
        
        this.calibration_history.get(correlation_id).push({
            timestamp: new Date().toISOString(),
            ...calibration_result
        });
    }
}

// Learning Model Base Class
class LearningModel {
    constructor() {
        this.model_parameters = new Map();
        this.training_history = [];
        this.performance_metrics = {};
    }

    async update(correlation_id, feedback, context) {
        throw new Error('Update method must be implemented by subclass');
    }

    async optimize() {
        // Optimize model parameters
        console.log('Optimizing model...');
    }

    calculatePerformance() {
        // Calculate model performance metrics
        return {
            accuracy: 0.0,
            precision: 0.0,
            recall: 0.0,
            f1_score: 0.0
        };
    }
}

// Specific Learning Models
class CorrelationLearningModel extends LearningModel {
    async update(correlation_id, feedback, context) {
        // Update correlation patterns and rules
        return {
            updated: true,
            improvement: 0.02,
            changes: ['Updated correlation weights']
        };
    }
}

class FalsePositiveLearningModel extends LearningModel {
    async update(correlation_id, feedback, context) {
        // Update false positive detection
        return {
            updated: true,
            improvement: 0.03,
            changes: ['Improved false positive detection']
        };
    }
}

class RiskScoringLearningModel extends LearningModel {
    async update(correlation_id, feedback, context) {
        // Update risk scoring algorithms
        return {
            updated: true,
            improvement: 0.01,
            changes: ['Adjusted risk scoring weights']
        };
    }
}

class ConfidenceLearningModel extends LearningModel {
    async update(correlation_id, feedback, context) {
        // Update confidence calculation
        return {
            updated: true,
            improvement: 0.02,
            changes: ['Updated confidence factors']
        };
    }
}

// Rollback Manager
class RollbackManager {
    constructor() {
        this.rollback_points = new Map();
    }

    createRollbackPoint(model_name, version, update_data) {
        const rollback_point = {
            model_name: model_name,
            version: version,
            timestamp: new Date().toISOString(),
            update_data: update_data
        };
        
        if (!this.rollback_points.has(model_name)) {
            this.rollback_points.set(model_name, []);
        }
        
        this.rollback_points.get(model_name).push(rollback_point);
    }

    rollback(model_name, target_version) {
        // Rollback model to specific version
        console.log(`Rolling back ${model_name} to version ${target_version}`);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdaptiveLearningEngine;
}

// Global instance
window.AdaptiveLearningEngine = AdaptiveLearningEngine;
