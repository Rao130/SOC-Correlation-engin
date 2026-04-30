/**
 * Advanced Analytics Dashboard
 * Enterprise-grade security analytics with real-time visualizations
 */

class AdvancedAnalyticsManager {
    constructor() {
        this.charts = {};
        this.metrics = {};
        this.realtimeData = {};
        this.updateInterval = null;
        this.chartConfigs = this._initializeChartConfigs();
        this.threatMetrics = this._initializeThreatMetrics();
        this.businessMetrics = this._initializeBusinessMetrics();
        
        this.initializeDashboard();
    }

    _initializeChartConfigs() {
        return {
            threatLandscape: {
                type: 'bubble',
                container: 'threat-landscape-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Risk Score' } },
                        y: { title: { display: true, text: 'Confidence' } }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            callbacks: {
                                label: (context) => `${context.raw.label}: Risk ${context.raw.x}, Confidence ${context.raw.y}`
                            }
                        }
                    }
                }
            },
            attackTimeline: {
                type: 'line',
                container: 'attack-timeline-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { type: 'time', time: { unit: 'hour' } },
                        y: { title: { display: true, text: 'Attack Count' } }
                    },
                    plugins: {
                        legend: { position: 'top' }
                    }
                }
            },
            threatIntelligence: {
                type: 'radar',
                container: 'threat-intel-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: { beginAtZero: true, max: 100 }
                    }
                }
            },
            businessImpact: {
                type: 'doughnut',
                container: 'business-impact-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'right' }
                    }
                }
            },
            correlationMatrix: {
                type: 'heatmap',
                container: 'correlation-matrix-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { type: 'category' },
                        y: { type: 'category' }
                    }
                }
            },
            anomalyDetection: {
                type: 'scatter',
                container: 'anomaly-detection-chart',
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Time' } },
                        y: { title: { display: true, text: 'Anomaly Score' } }
                    }
                }
            }
        };
    }

    _initializeThreatMetrics() {
        return {
            totalThreats: 0,
            criticalThreats: 0,
            highRiskThreats: 0,
            threatTrends: [],
            threatTypes: {},
            geographicDistribution: {},
            attackVectors: {},
            mitreTechniques: {}
        };
    }

    _initializeBusinessMetrics() {
        return {
            riskScore: 0,
            businessImpact: 'low',
            financialExposure: 0,
            complianceScore: 0,
            mttr: 0,
            mttD: 0,
            roi: 0,
            riskReduction: 0
        };
    }

    async initializeDashboard() {
        console.log('🎯 Initializing Advanced Analytics Dashboard...');
        
        try {
            // Initialize all charts
            await this._initializeCharts();
            
            // Load initial data
            await this.loadAnalyticsData();
            
            // Start real-time updates
            this.startRealtimeUpdates();
            
            // Setup event listeners
            this._setupEventListeners();
            
            console.log('✅ Advanced Analytics Dashboard initialized');
            
        } catch (error) {
            console.error('❌ Failed to initialize dashboard:', error);
        }
    }

    async _initializeCharts() {
        const chartPromises = Object.keys(this.chartConfigs).map(chartType => {
            return this._createChart(chartType);
        });

        await Promise.all(chartPromises);
    }

    async _createChart(chartType) {
        const config = this.chartConfigs[chartType];
        const container = document.getElementById(config.container);
        
        if (!container) {
            console.warn(`⚠️ Chart container not found: ${config.container}`);
            return;
        }

        try {
            const ctx = container.getContext('2d');
            
            // Create chart based on type
            switch (chartType) {
                case 'threatLandscape':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'bubble',
                        data: this._getThreatLandscapeData(),
                        options: config.options
                    });
                    break;
                    
                case 'attackTimeline':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'line',
                        data: this._getAttackTimelineData(),
                        options: config.options
                    });
                    break;
                    
                case 'threatIntelligence':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'radar',
                        data: this._getThreatIntelData(),
                        options: config.options
                    });
                    break;
                    
                case 'businessImpact':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'doughnut',
                        data: this._getBusinessImpactData(),
                        options: config.options
                    });
                    break;
                    
                case 'correlationMatrix':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'bubble',
                        data: this._getCorrelationMatrixData(),
                        options: config.options
                    });
                    break;
                    
                case 'anomalyDetection':
                    this.charts[chartType] = new Chart(ctx, {
                        type: 'scatter',
                        data: this._getAnomalyDetectionData(),
                        options: config.options
                    });
                    break;
            }
            
            console.log(`✅ Chart created: ${chartType}`);
            
        } catch (error) {
            console.error(`❌ Failed to create chart ${chartType}:`, error);
        }
    }

    _getThreatLandscapeData() {
        return {
            datasets: [{
                label: 'Current Threats',
                data: this._generateThreatBubbles(),
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }]
        };
    }

    _generateThreatBubbles() {
        const threats = [];
        const threatTypes = ['Malware', 'Phishing', 'DDoS', 'Insider', 'APT', 'Zero-Day'];
        
        for (let i = 0; i < 15; i++) {
            threats.push({
                x: Math.random() * 100,
                y: Math.random() * 100,
                r: Math.random() * 20 + 5,
                label: threatTypes[Math.floor(Math.random() * threatTypes.length)]
            });
        }
        
        return threats;
    }

    _getAttackTimelineData() {
        const now = new Date();
        const labels = [];
        const datasets = [];
        
        // Generate last 24 hours
        for (let i = 23; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time);
        }
        
        datasets.push({
            label: 'Critical Attacks',
            data: labels.map(() => Math.floor(Math.random() * 10)),
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            tension: 0.4
        });
        
        datasets.push({
            label: 'High Risk Attacks',
            data: labels.map(() => Math.floor(Math.random() * 20)),
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            tension: 0.4
        });
        
        datasets.push({
            label: 'Medium Risk Attacks',
            data: labels.map(() => Math.floor(Math.random() * 30)),
            borderColor: 'rgb(255, 205, 86)',
            backgroundColor: 'rgba(255, 205, 86, 0.2)',
            tension: 0.4
        });
        
        return { labels, datasets };
    }

    _getThreatIntelData() {
        return {
            labels: ['Network Security', 'Endpoint Protection', 'Data Protection', 'Identity Access', 'Cloud Security', 'Application Security'],
            datasets: [{
                label: 'Current Coverage',
                data: [85, 78, 92, 88, 75, 82],
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgb(54, 162, 235)',
                pointBackgroundColor: 'rgb(54, 162, 235)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(54, 162, 235)'
            }]
        };
    }

    _getBusinessImpactData() {
        return {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [15, 25, 35, 25],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 159, 64, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)'
                ],
                borderWidth: 0
            }]
        };
    }

    _getCorrelationMatrixData() {
        const correlations = [];
        const dimensions = ['Temporal', 'Network', 'Behavioral', 'Threat Intel', 'Asset'];
        
        for (let i = 0; i < dimensions.length; i++) {
            for (let j = 0; j < dimensions.length; j++) {
                if (i !== j) {
                    correlations.push({
                        x: i,
                        y: j,
                        r: Math.random() * 15 + 5,
                        label: `${dimensions[i]}-${dimensions[j]}`
                    });
                }
            }
        }
        
        return {
            datasets: [{
                label: 'Correlation Strength',
                data: correlations,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)'
            }]
        };
    }

    _getAnomalyDetectionData() {
        const anomalies = [];
        const now = Date.now();
        
        for (let i = 0; i < 50; i++) {
            const time = now - (i * 60 * 60 * 1000); // Last 50 hours
            const score = Math.random();
            
            anomalies.push({
                x: new Date(time),
                y: score,
                r: score > 0.7 ? 8 : 4
            });
        }
        
        return {
            datasets: [{
                label: 'Anomalies',
                data: anomalies,
                backgroundColor: anomalies.map(a => 
                    a.y > 0.7 ? 'rgba(255, 99, 132, 0.8)' : 'rgba(75, 192, 192, 0.6)'
                )
            }]
        };
    }

    async loadAnalyticsData() {
        try {
            console.log('📊 Loading analytics data...');
            
            // Load threat metrics
            await this._loadThreatMetrics();
            
            // Load business metrics
            await this._loadBusinessMetrics();
            
            // Load correlation data
            await this._loadCorrelationData();
            
            // Load attack chain data
            await this._loadAttackChainData();
            
            // Update all charts
            this._updateAllCharts();
            
            // Update KPI cards
            this._updateKPICards();
            
            console.log('✅ Analytics data loaded');
            
        } catch (error) {
            console.error('❌ Failed to load analytics data:', error);
        }
    }

    async _loadThreatMetrics() {
        try {
            const response = await fetch('/api/analytics/threat-metrics');
            if (response.ok) {
                this.threatMetrics = await response.json();
            } else {
                // Use mock data for demo
                this.threatMetrics = {
                    totalThreats: 156,
                    criticalThreats: 12,
                    highRiskThreats: 34,
                    threatTrends: this._generateMockTrends(),
                    threatTypes: {
                        'Malware': 45,
                        'Phishing': 32,
                        'DDoS': 28,
                        'Insider': 18,
                        'APT': 15,
                        'Zero-Day': 8
                    },
                    geographicDistribution: {
                        'North America': 45,
                        'Europe': 38,
                        'Asia': 32,
                        'Other': 21
                    },
                    attackVectors: {
                        'Email': 35,
                        'Web': 28,
                        'Network': 25,
                        'Endpoint': 18,
                        'Cloud': 12
                    }
                };
            }
        } catch (error) {
            console.warn('⚠️ Using mock threat metrics data');
            this.threatMetrics = this._getMockThreatMetrics();
        }
    }

    async _loadBusinessMetrics() {
        try {
            const response = await fetch('/api/analytics/business-metrics');
            if (response.ok) {
                this.businessMetrics = await response.json();
            } else {
                // Use mock data for demo
                this.businessMetrics = {
                    riskScore: 67.5,
                    businessImpact: 'medium',
                    financialExposure: 2500000,
                    complianceScore: 82.3,
                    mttr: 45, // minutes
                    mttD: 12, // minutes
                    roi: 285, // percentage
                    riskReduction: 73.2 // percentage
                };
            }
        } catch (error) {
            console.warn('⚠️ Using mock business metrics data');
            this.businessMetrics = this._getMockBusinessMetrics();
        }
    }

    async _loadCorrelationData() {
        try {
            const response = await fetch('/api/analytics/correlations');
            if (response.ok) {
                const correlations = await response.json();
                this._updateCorrelationChart(correlations);
            }
        } catch (error) {
            console.warn('⚠️ Using mock correlation data');
        }
    }

    async _loadAttackChainData() {
        try {
            const response = await fetch('/api/analytics/attack-chains');
            if (response.ok) {
                const attackChains = await response.json();
                this._updateAttackChainVisualization(attackChains);
            }
        } catch (error) {
            console.warn('⚠️ Using mock attack chain data');
        }
    }

    _generateMockTrends() {
        const trends = [];
        const now = new Date();
        
        for (let i = 30; i >= 0; i--) {
            const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
            trends.push({
                date: date.toISOString().split('T')[0],
                threats: Math.floor(Math.random() * 20) + 5,
                critical: Math.floor(Math.random() * 5),
                resolved: Math.floor(Math.random() * 15) + 3
            });
        }
        
        return trends;
    }

    _getMockThreatMetrics() {
        return {
            totalThreats: 156,
            criticalThreats: 12,
            highRiskThreats: 34,
            threatTrends: this._generateMockTrends(),
            threatTypes: {
                'Malware': 45,
                'Phishing': 32,
                'DDoS': 28,
                'Insider': 18,
                'APT': 15,
                'Zero-Day': 8
            },
            geographicDistribution: {
                'North America': 45,
                'Europe': 38,
                'Asia': 32,
                'Other': 21
            },
            attackVectors: {
                'Email': 35,
                'Web': 28,
                'Network': 25,
                'Endpoint': 18,
                'Cloud': 12
            }
        };
    }

    _getMockBusinessMetrics() {
        return {
            riskScore: 67.5,
            businessImpact: 'medium',
            financialExposure: 2500000,
            complianceScore: 82.3,
            mttr: 45,
            mttD: 12,
            roi: 285,
            riskReduction: 73.2
        };
    }

    _updateAllCharts() {
        Object.keys(this.charts).forEach(chartType => {
            this._updateChart(chartType);
        });
    }

    _updateChart(chartType) {
        const chart = this.charts[chartType];
        if (!chart) return;

        try {
            switch (chartType) {
                case 'threatLandscape':
                    chart.data = this._getThreatLandscapeData();
                    break;
                case 'attackTimeline':
                    chart.data = this._getAttackTimelineData();
                    break;
                case 'threatIntelligence':
                    chart.data = this._getThreatIntelData();
                    break;
                case 'businessImpact':
                    chart.data = this._getBusinessImpactData();
                    break;
                case 'correlationMatrix':
                    chart.data = this._getCorrelationMatrixData();
                    break;
                case 'anomalyDetection':
                    chart.data = this._getAnomalyDetectionData();
                    break;
            }
            
            chart.update('none');
            
        } catch (error) {
            console.error(`❌ Failed to update chart ${chartType}:`, error);
        }
    }

    _updateKPICards() {
        this._updateThreatKPIs();
        this._updateBusinessKPIs();
        this._updatePerformanceKPIs();
    }

    _updateThreatKPIs() {
        const elements = {
            'total-threats': this.threatMetrics.totalThreats,
            'critical-threats': this.threatMetrics.criticalThreats,
            'high-risk-threats': this.threatMetrics.highRiskThreats,
            'threat-trend': this._calculateThreatTrend()
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    _updateBusinessKPIs() {
        const elements = {
            'risk-score': this.businessMetrics.riskScore.toFixed(1),
            'financial-exposure': this._formatCurrency(this.businessMetrics.financialExposure),
            'compliance-score': this.businessMetrics.complianceScore.toFixed(1),
            'roi': this.businessMetrics.roi.toFixed(0) + '%'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    _updatePerformanceKPIs() {
        const elements = {
            'mttr': this.businessMetrics.mttR + ' min',
            'mttd': this.businessMetrics.mttD + ' min',
            'risk-reduction': this.businessMetrics.riskReduction.toFixed(1) + '%'
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    _calculateThreatTrend() {
        const trends = this.threatMetrics.threatTrends;
        if (trends.length < 2) return '0%';
        
        const recent = trends.slice(-7);
        const previous = trends.slice(-14, -7);
        
        const recentAvg = recent.reduce((sum, t) => sum + t.threats, 0) / recent.length;
        const previousAvg = previous.reduce((sum, t) => sum + t.threats, 0) / previous.length;
        
        const trend = ((recentAvg - previousAvg) / previousAvg * 100);
        return (trend >= 0 ? '+' : '') + trend.toFixed(1) + '%';
    }

    _formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 0
        }).format(amount);
    }

    startRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }

        this.updateInterval = setInterval(() => {
            this.loadAnalyticsData();
        }, 30000); // Update every 30 seconds

        console.log('🔄 Real-time updates started');
    }

    stopRealtimeUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
            console.log('⏹️ Real-time updates stopped');
        }
    }

    _setupEventListeners() {
        // Chart type selector
        const chartTypeSelector = document.getElementById('chart-type-selector');
        if (chartTypeSelector) {
            chartTypeSelector.addEventListener('change', (e) => {
                this._switchChartType(e.target.value);
            });
        }

        // Time range selector
        const timeRangeSelector = document.getElementById('time-range-selector');
        if (timeRangeSelector) {
            timeRangeSelector.addEventListener('change', (e) => {
                this._changeTimeRange(e.target.value);
            });
        }

        // Export button
        const exportButton = document.getElementById('export-analytics');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this._exportAnalytics();
            });
        }

        // Refresh button
        const refreshButton = document.getElementById('refresh-analytics');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                this.loadAnalyticsData();
            });
        }
    }

    _switchChartType(chartType) {
        // Implementation for switching chart types
        console.log(`🔄 Switching to chart type: ${chartType}`);
        this.loadAnalyticsData();
    }

    _changeTimeRange(timeRange) {
        // Implementation for changing time range
        console.log(`📅 Changing time range to: ${timeRange}`);
        this.loadAnalyticsData();
    }

    async _exportAnalytics() {
        try {
            const analyticsData = {
                threatMetrics: this.threatMetrics,
                businessMetrics: this.businessMetrics,
                timestamp: new Date().toISOString()
            };

            const blob = new Blob([JSON.stringify(analyticsData, null, 2)], {
                type: 'application/json'
            });

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `analytics-export-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            console.log('📊 Analytics data exported');

        } catch (error) {
            console.error('❌ Failed to export analytics:', error);
        }
    }

    _updateCorrelationChart(correlations) {
        if (!this.charts.correlationMatrix) return;

        const data = correlations.map(corr => ({
            x: corr.dimension1,
            y: corr.dimension2,
            r: corr.strength * 20,
            label: `${corr.dimension1}-${corr.dimension2}`
        }));

        this.charts.correlationMatrix.data.datasets[0].data = data;
        this.charts.correlationMatrix.update('none');
    }

    _updateAttackChainVisualization(attackChains) {
        // Implementation for updating attack chain visualization
        console.log('🔗 Updating attack chain visualization:', attackChains.length);
    }

    // Advanced analytics methods

    async generatePredictiveAnalytics() {
        try {
            console.log('🔮 Generating predictive analytics...');

            const response = await fetch('/api/analytics/predictive');
            if (response.ok) {
                const predictions = await response.json();
                this._displayPredictions(predictions);
            }

        } catch (error) {
            console.error('❌ Failed to generate predictive analytics:', error);
        }
    }

    _displayPredictions(predictions) {
        const container = document.getElementById('predictions-container');
        if (!container) return;

        const html = predictions.map(pred => `
            <div class="prediction-card">
                <h4>${pred.type}</h4>
                <p>Probability: ${(pred.probability * 100).toFixed(1)}%</p>
                <p>Timeframe: ${pred.timeframe}</p>
                <p>Risk Level: ${pred.risk_level}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async generateThreatHuntingInsights() {
        try {
            console.log('🕵️ Generating threat hunting insights...');

            const response = await fetch('/api/analytics/hunting-insights');
            if (response.ok) {
                const insights = await response.json();
                this._displayHuntingInsights(insights);
            }

        } catch (error) {
            console.error('❌ Failed to generate hunting insights:', error);
        }
    }

    _displayHuntingInsights(insights) {
        const container = document.getElementById('hunting-insights-container');
        if (!container) return;

        const html = insights.map(insight => `
            <div class="insight-card">
                <h4>${insight.title}</h4>
                <p>${insight.description}</p>
                <p>Priority: ${insight.priority}</p>
                <p>Recommended Actions: ${insight.recommended_actions.join(', ')}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    // Public API methods

    refreshCharts() {
        this._updateAllCharts();
    }

    getMetrics() {
        return {
            threat: this.threatMetrics,
            business: this.businessMetrics
        };
    }

    destroy() {
        this.stopRealtimeUpdates();
        
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.destroy();
            }
        });
        
        this.charts = {};
        console.log('🗑️ Advanced Analytics Dashboard destroyed');
    }
}

// Initialize advanced analytics when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.advancedAnalytics = new AdvancedAnalyticsManager();
    console.log('🎯 Advanced Analytics Manager initialized globally');
});

// Global functions for external access
function refreshAnalytics() {
    if (window.advancedAnalytics) {
        window.advancedAnalytics.loadAnalyticsData();
    }
}

function exportAnalyticsData() {
    if (window.advancedAnalytics) {
        window.advancedAnalytics._exportAnalytics();
    }
}

function generatePredictions() {
    if (window.advancedAnalytics) {
        window.advancedAnalytics.generatePredictiveAnalytics();
    }
}

function generateHuntingInsights() {
    if (window.advancedAnalytics) {
        window.advancedAnalytics.generateThreatHuntingInsights();
    }
}
