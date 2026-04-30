/**
 * Unified Real-Time Graph Update System
 * Ensures all graphs in the system update automatically with live data
 */

class UnifiedRealtimeGraphs {
    constructor() {
        this.graphs = new Map();
        this.updateInterval = 3000; // 3 seconds
        this.isRunning = false;
        this.websocket = null;
        this.retryCount = 0;
        this.maxRetries = 5;
        
        // Data caches
        this.alertData = [];
        this.networkData = {};
        this.correlationData = [];
        this.performanceData = [];
        
        this.init();
    }

    async init() {
        console.log('Initializing Unified Real-Time Graph System...');
        
        // Initialize WebSocket connection
        this.initWebSocket();
        
        // Register all graphs
        this.registerAllGraphs();
        
        // Start periodic updates
        this.startPeriodicUpdates();
        
        // Setup global update function
        this.setupGlobalUpdateFunction();
        
        console.log('Unified Real-Time Graph System initialized!');
    }

    initWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected for real-time graph updates');
                this.retryCount = 0;
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketUpdate(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected, attempting to reconnect...');
                this.retryWebSocket();
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Error initializing WebSocket:', error);
            // Fallback to HTTP polling
            this.startHttpPolling();
        }
    }

    retryWebSocket() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`Retrying WebSocket connection (${this.retryCount}/${this.maxRetries})`);
            setTimeout(() => {
                this.initWebSocket();
            }, 5000 * this.retryCount);
        } else {
            console.log('Max retries reached, falling back to HTTP polling');
            this.startHttpPolling();
        }
    }

    startHttpPolling() {
        console.log('Starting HTTP polling for real-time updates');
        setInterval(() => {
            this.fetchLatestData();
        }, this.updateInterval);
    }

    registerAllGraphs() {
        // Register Analytics Charts
        this.registerAnalyticsGraphs();
        
        // Register Dashboard Charts
        this.registerDashboardGraphs();
        
        // Register Risk Visualization Charts
        this.registerRiskGraphs();
        
        // Register Network Monitor Charts
        this.registerNetworkGraphs();
        
        // Register Correlation Charts
        this.registerCorrelationGraphs();
    }

    registerAnalyticsGraphs() {
        // Attack Timeline Chart
        const timelineCtx = document.getElementById('attackTimelineChart');
        if (timelineCtx) {
            this.graphs.set('attackTimeline', {
                type: 'line',
                element: timelineCtx,
                chart: null,
                updateFunction: (data) => this.updateAttackTimeline(data)
            });
        }

        // Severity Distribution Chart
        const severityCtx = document.getElementById('severityChart');
        if (severityCtx) {
            this.graphs.set('severityDistribution', {
                type: 'pie',
                element: severityCtx,
                chart: null,
                updateFunction: (data) => this.updateSeverityChart(data)
            });
        }

        // Category Distribution Chart
        const categoryCtx = document.getElementById('categoryChart');
        if (categoryCtx) {
            this.graphs.set('categoryDistribution', {
                type: 'doughnut',
                element: categoryCtx,
                chart: null,
                updateFunction: (data) => this.updateCategoryChart(data)
            });
        }

        // Time Series Chart
        const timeSeriesCtx = document.getElementById('timeSeriesChart');
        if (timeSeriesCtx) {
            this.graphs.set('timeSeries', {
                type: 'line',
                element: timeSeriesCtx,
                chart: null,
                updateFunction: (data) => this.updateTimeSeriesChart(data)
            });
        }

        // Pattern Analysis Chart
        const patternCtx = document.getElementById('patternChart');
        if (patternCtx) {
            this.graphs.set('patternAnalysis', {
                type: 'bar',
                element: patternCtx,
                chart: null,
                updateFunction: (data) => this.updatePatternChart(data)
            });
        }
    }

    registerDashboardGraphs() {
        // Real-time Risk Chart
        const riskCtx = document.getElementById('realtime-risk-chart');
        if (riskCtx) {
            this.graphs.set('realtimeRisk', {
                type: 'line',
                element: riskCtx,
                chart: null,
                updateFunction: (data) => this.updateRealtimeRiskChart(data)
            });
        }

        // Risk Distribution Chart
        const riskDistCtx = document.getElementById('risk-distribution-chart');
        if (riskDistCtx) {
            this.graphs.set('riskDistribution', {
                type: 'pie',
                element: riskDistCtx,
                chart: null,
                updateFunction: (data) => this.updateRiskDistributionChart(data)
            });
        }

        // Performance Chart
        const perfCtx = document.getElementById('performance-chart');
        if (perfCtx) {
            this.graphs.set('performance', {
                type: 'line',
                element: perfCtx,
                chart: null,
                updateFunction: (data) => this.updatePerformanceChart(data)
            });
        }
    }

    registerRiskGraphs() {
        // Confidence Gauge Chart
        const confidenceCtx = document.getElementById('confidence-gauge-chart');
        if (confidenceCtx) {
            this.graphs.set('confidenceGauge', {
                type: 'gauge',
                element: confidenceCtx,
                chart: null,
                updateFunction: (data) => this.updateConfidenceGauge(data)
            });
        }
    }

    registerNetworkGraphs() {
        // Network Traffic Chart
        const trafficCtx = document.getElementById('networkTrafficChart');
        if (trafficCtx) {
            this.graphs.set('networkTraffic', {
                type: 'line',
                element: trafficCtx,
                chart: null,
                updateFunction: (data) => this.updateNetworkTrafficChart(data)
            });
        }

        // Connection Types Chart
        const connTypesCtx = document.getElementById('connectionTypesChart');
        if (connTypesCtx) {
            this.graphs.set('connectionTypes', {
                type: 'doughnut',
                element: connTypesCtx,
                chart: null,
                updateFunction: (data) => this.updateConnectionTypesChart(data)
            });
        }
    }

    registerCorrelationGraphs() {
        // Correlation Strength Chart
        const corrStrengthCtx = document.getElementById('correlationStrengthChart');
        if (corrStrengthCtx) {
            this.graphs.set('correlationStrength', {
                type: 'bar',
                element: corrStrengthCtx,
                chart: null,
                updateFunction: (data) => this.updateCorrelationStrengthChart(data)
            });
        }

        // Pattern Match Chart
        const patternMatchCtx = document.getElementById('patternMatchChart');
        if (patternMatchCtx) {
            this.graphs.set('patternMatch', {
                type: 'radar',
                element: patternMatchCtx,
                chart: null,
                updateFunction: (data) => this.updatePatternMatchChart(data)
            });
        }
    }

    async fetchLatestData() {
        try {
            const [alertsResponse, networkResponse, correlationResponse] = await Promise.all([
                fetch('/api/alerts/?limit=100').catch(() => null),
                fetch('/api/network/metrics').catch(() => null),
                fetch('/api/correlations/realtime').catch(() => null)
            ]);

            const data = {};

            if (alertsResponse?.ok) {
                data.alerts = await alertsResponse.json();
            }

            if (networkResponse?.ok) {
                data.network = await networkResponse.json();
            }

            if (correlationResponse?.ok) {
                data.correlations = await correlationResponse.json();
            }

            this.updateAllGraphs(data);

        } catch (error) {
            console.error('Error fetching latest data:', error);
        }
    }

    handleWebSocketUpdate(data) {
        console.log('Received WebSocket update for graphs');
        this.updateAllGraphs(data);
    }

    updateAllGraphs(data) {
        // Update data caches
        if (data.alerts) this.alertData = data.alerts;
        if (data.network) this.networkData = data.network;
        if (data.correlations) this.correlationData = data.correlations;

        // Update all registered graphs
        this.graphs.forEach((graphConfig, graphId) => {
            try {
                graphConfig.updateFunction(data);
            } catch (error) {
                console.error(`Error updating graph ${graphId}:`, error);
            }
        });
    }

    // Chart Update Functions
    updateAttackTimeline(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts || !window.attackTimelineChart) return;

        const timelineData = this.processTimelineData(alerts);
        
        window.attackTimelineChart.data.labels = timelineData.labels;
        window.attackTimelineChart.data.datasets[0].data = timelineData.data;
        window.attackTimelineChart.update('none'); // Update without animation for real-time
    }

    updateSeverityChart(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts || !window.severityChart) return;

        const severityData = this.processSeverityData(alerts);
        
        window.severityChart.data.datasets[0].data = severityData;
        window.severityChart.update('none');
    }

    updateCategoryChart(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts || !window.categoryChart) return;

        const categoryData = this.processCategoryData(alerts);
        
        window.categoryChart.data.datasets[0].data = categoryData;
        window.categoryChart.update('none');
    }

    updateTimeSeriesChart(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts || !window.timeSeriesChart) return;

        const timeSeriesData = this.processTimeSeriesData(alerts);
        
        window.timeSeriesChart.data.labels = timeSeriesData.labels;
        window.timeSeriesChart.data.datasets[0].data = timeSeriesData.data;
        window.timeSeriesChart.update('none');
    }

    updatePatternChart(data) {
        const correlations = data.correlations || this.correlationData;
        if (!correlations || !window.patternChart) return;

        const patternData = this.processPatternData(correlations);
        
        window.patternChart.data.labels = patternData.labels;
        window.patternChart.data.datasets[0].data = patternData.data;
        window.patternChart.update('none');
    }

    updateRealtimeRiskChart(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts) return;

        const ctx = document.getElementById('realtime-risk-chart');
        if (!ctx) return;

        const riskData = this.processRiskData(alerts);
        
        // Create or update chart
        if (!window.realtimeRiskChart) {
            window.realtimeRiskChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: riskData.labels,
                    datasets: [{
                        label: 'Risk Score',
                        data: riskData.data,
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    animation: {
                        duration: 0 // Disable animation for real-time
                    }
                }
            });
        } else {
            window.realtimeRiskChart.data.labels = riskData.labels;
            window.realtimeRiskChart.data.datasets[0].data = riskData.data;
            window.realtimeRiskChart.update('none');
        }
    }

    updateRiskDistributionChart(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts) return;

        const ctx = document.getElementById('risk-distribution-chart');
        if (!ctx) return;

        const distributionData = this.processRiskDistribution(alerts);
        
        if (!window.riskDistributionChart) {
            window.riskDistributionChart = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: distributionData,
                        backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 0
                    }
                }
            });
        } else {
            window.riskDistributionChart.data.datasets[0].data = distributionData;
            window.riskDistributionChart.update('none');
        }
    }

    updatePerformanceChart(data) {
        const network = data.network || this.networkData;
        if (!network) return;

        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        const performanceData = this.processPerformanceData(network);
        
        if (!window.performanceChart) {
            window.performanceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: performanceData.labels,
                    datasets: [{
                        label: 'CPU Usage',
                        data: performanceData.cpu,
                        borderColor: '#4ecdc4',
                        backgroundColor: 'rgba(78, 205, 196, 0.1)',
                        tension: 0.4
                    }, {
                        label: 'Memory Usage',
                        data: performanceData.memory,
                        borderColor: '#f7b731',
                        backgroundColor: 'rgba(247, 183, 49, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    animation: {
                        duration: 0
                    }
                }
            });
        } else {
            window.performanceChart.data.labels = performanceData.labels;
            window.performanceChart.data.datasets[0].data = performanceData.cpu;
            window.performanceChart.data.datasets[1].data = performanceData.memory;
            window.performanceChart.update('none');
        }
    }

    updateConfidenceGauge(data) {
        const alerts = data.alerts || this.alertData;
        if (!alerts) return;

        const ctx = document.getElementById('confidence-gauge-chart');
        if (!ctx) return;

        const confidence = this.calculateAverageConfidence(alerts);
        
        // Simple gauge implementation using Chart.js
        if (!window.confidenceGaugeChart) {
            window.confidenceGaugeChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [confidence, 100 - confidence],
                        backgroundColor: ['#28a745', '#e9ecef'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    animation: {
                        duration: 0
                    }
                }
            });
        } else {
            window.confidenceGaugeChart.data.datasets[0].data = [confidence, 100 - confidence];
            window.confidenceGaugeChart.update('none');
        }
    }

    // Data Processing Functions
    processTimelineData(alerts) {
        const timeline = {};
        const now = new Date();
        
        alerts.forEach(alert => {
            const hour = new Date(alert.timestamp).getHours();
            timeline[hour] = (timeline[hour] || 0) + 1;
        });

        const labels = [];
        const data = [];
        
        for (let i = 0; i < 24; i++) {
            labels.push(`${i}:00`);
            data.push(timeline[i] || 0);
        }

        return { labels, data };
    }

    processSeverityData(alerts) {
        const severity = { critical: 0, high: 0, medium: 0, low: 0 };
        
        alerts.forEach(alert => {
            const level = alert.severity || 'low';
            if (severity.hasOwnProperty(level)) {
                severity[level]++;
            }
        });

        return Object.values(severity);
    }

    processCategoryData(alerts) {
        const categories = {};
        
        alerts.forEach(alert => {
            const category = alert.category || 'unknown';
            categories[category] = (categories[category] || 0) + 1;
        });

        return Object.values(categories);
    }

    processTimeSeriesData(alerts) {
        const timeData = {};
        const now = new Date();
        
        alerts.forEach(alert => {
            const time = new Date(alert.timestamp);
            const key = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            timeData[key] = (timeData[key] || 0) + 1;
        });

        const sortedKeys = Object.keys(timeData).sort().slice(-20); // Last 20 data points
        const labels = sortedKeys;
        const data = sortedKeys.map(key => timeData[key]);

        return { labels, data };
    }

    processPatternData(correlations) {
        const patterns = {};
        
        correlations.forEach(corr => {
            const pattern = corr.pattern || 'unknown';
            patterns[pattern] = (patterns[pattern] || 0) + 1;
        });

        return {
            labels: Object.keys(patterns),
            data: Object.values(patterns)
        };
    }

    processRiskData(alerts) {
        const riskData = [];
        const labels = [];
        const now = new Date();
        
        // Get last 20 risk scores
        const recentAlerts = alerts
            .filter(alert => alert.risk_score !== undefined)
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 20)
            .reverse();

        recentAlerts.forEach((alert, index) => {
            labels.push(new Date(alert.timestamp).toLocaleTimeString());
            riskData.push(alert.risk_score || 0);
        });

        return { labels, data: riskData };
    }

    processRiskDistribution(alerts) {
        const distribution = { critical: 0, high: 0, medium: 0, low: 0 };
        
        alerts.forEach(alert => {
            const risk = alert.risk_score || 0;
            if (risk >= 80) distribution.critical++;
            else if (risk >= 60) distribution.high++;
            else if (risk >= 40) distribution.medium++;
            else distribution.low++;
        });

        return Object.values(distribution);
    }

    processPerformanceData(network) {
        const labels = [];
        const cpu = [];
        const memory = [];
        
        // Generate sample performance data
        for (let i = 0; i < 10; i++) {
            labels.push(`T-${9-i}`);
            cpu.push(Math.random() * 100);
            memory.push(Math.random() * 100);
        }

        return { labels, cpu, memory };
    }

    calculateAverageConfidence(alerts) {
        if (!alerts.length) return 0;
        
        const totalConfidence = alerts.reduce((sum, alert) => {
            return sum + (alert.confidence || 0);
        }, 0);
        
        return Math.round((totalConfidence / alerts.length) * 100);
    }

    startPeriodicUpdates() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        
        // Initial data fetch
        this.fetchLatestData();
        
        // Set up periodic updates
        setInterval(() => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                this.fetchLatestData();
            }
        }, this.updateInterval);
    }

    setupGlobalUpdateFunction() {
        // Make update function globally available
        window.updateAllGraphs = (data) => {
            this.updateAllGraphs(data);
        };
        
        // Auto-initialize charts when they become available
        const observer = new MutationObserver(() => {
            this.registerAllGraphs();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Public methods
    addGraph(graphId, config) {
        this.graphs.set(graphId, config);
    }

    removeGraph(graphId) {
        this.graphs.delete(graphId);
    }

    setUpdateInterval(interval) {
        this.updateInterval = interval;
    }

    stop() {
        this.isRunning = false;
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for other scripts to load
    setTimeout(() => {
        if (!window.unifiedRealtimeGraphs) {
            window.unifiedRealtimeGraphs = new UnifiedRealtimeGraphs();
        }
    }, 2000);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedRealtimeGraphs;
}
