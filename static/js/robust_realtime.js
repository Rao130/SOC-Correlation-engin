/**
 * Robust Real-Time Updates System
 * Ultra-reliable WebSocket and data loading with multiple fallbacks
 */

class RobustRealtimeSystem {
    constructor() {
        this.isRunning = false;
        this.updateInterval = 3000; // 3 seconds
        this.websocket = null;
        this.charts = new Map();
        this.updateCount = 0;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.manualClose = false;
        this.lastDataUpdate = 0;
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        this.init();
    }

    init() {
        console.log('Starting Robust Real-Time System...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
    }

    start() {
        console.log('=== DEBUG: Initializing Robust Real-Time Updates ===');
        
        // Wait for DOM to be fully ready
        if (document.readyState === 'loading') {
            console.log('DOM still loading, waiting...');
            document.addEventListener('DOMContentLoaded', () => {
                setTimeout(() => this.initializeSystem(), 1000);
            });
        } else {
            console.log('DOM ready, initializing immediately');
            setTimeout(() => this.initializeSystem(), 500);
        }
    }

    initializeSystem() {
        console.log('=== DEBUG: Starting system initialization ===');
        
        // Test Chart.js availability
        console.log('Chart.js available:', typeof Chart !== 'undefined');
        console.log('Chart.js version:', Chart?.version || 'unknown');
        
        // Test chart canvases
        const allCanvases = document.querySelectorAll('canvas');
        console.log('Total canvases found:', allCanvases.length);
        
        const chartCanvases = document.querySelectorAll('canvas[id*="chart"], canvas[id*="Chart"], canvas[id*="graph"]');
        console.log('Chart canvases found:', chartCanvases.length);
        chartCanvases.forEach((canvas, index) => {
            console.log(`Chart canvas ${index}:`, {
                id: canvas.id,
                width: canvas.width,
                height: canvas.height,
                hasChart: !!Chart.getChart(canvas)
            });
        });
        
        // Register all existing charts
        this.registerAllCharts();
        
        // Start with HTTP polling first (more reliable)
        this.startPeriodicUpdates();
        
        // Then try WebSocket as enhancement
        setTimeout(() => {
            this.connectWebSocket();
        }, 2000);
        
        this.isRunning = true;
        console.log('=== DEBUG: System initialization complete ===');
    }

    registerAllCharts() {
        console.log('=== DEBUG: Registering all charts ===');
        
        // Check if Chart.js is available
        console.log('Chart.js available:', typeof Chart !== 'undefined');
        if (typeof Chart !== 'undefined') {
            console.log('Chart.js instances:', Chart.instances.length);
        }
        
        // Clear invalid charts first
        this.cleanupInvalidCharts();
        
        // Register Chart.js charts
        if (typeof Chart !== 'undefined') {
            Chart.helpers.each(Chart.instances, (chart, index) => {
                console.log(`Chart instance ${index}:`, {
                    id: chart.canvas?.id,
                    type: chart.config?.type,
                    renderable: this.isChartRenderable(chart),
                    hasData: !!chart.data,
                    datasets: chart.data?.datasets?.length || 0
                });
                
                if (this.isChartRenderable(chart)) {
                    const canvas = chart.canvas;
                    const chartId = canvas.id || `chart_${this.charts.size}`;
                    this.charts.set(chartId, chart);
                    console.log(`✅ Registered chart: ${chartId} (${chart.config?.type})`);
                }
            });
        }

        // Look for specific chart canvases
        const chartCanvases = document.querySelectorAll('canvas[id*="chart"], canvas[id*="Chart"], canvas[id*="graph"]');
        console.log(`Found ${chartCanvases.length} chart canvases:`, Array.from(chartCanvases).map(c => c.id));
        
        chartCanvases.forEach(canvas => {
            if (!this.charts.has(canvas.id)) {
                const chart = Chart.getChart(canvas);
                console.log(`Canvas ${canvas.id} has chart:`, !!chart);
                if (chart && this.isChartRenderable(chart)) {
                    this.charts.set(canvas.id, chart);
                    console.log(`✅ Found additional chart: ${canvas.id}`);
                }
            }
        });

        // Also register dashboard and analytics charts if available
        this.registerSystemCharts();

        console.log(`=== Total charts registered: ${this.charts.size} ===`);
        console.log('Registered chart IDs:', Array.from(this.charts.keys()));
        
        // Update charts immediately after registration
        setTimeout(() => {
            console.log('=== Triggering initial chart update ===');
            this.fetchAndUpdateData();
        }, 1000);
    }

    cleanupInvalidCharts() {
        const invalidCharts = [];
        this.charts.forEach((chart, chartId) => {
            if (!this.isChartRenderable(chart)) {
                invalidCharts.push(chartId);
            }
        });
        
        invalidCharts.forEach(chartId => {
            this.charts.delete(chartId);
            console.log(`Removed invalid chart: ${chartId}`);
        });
    }

    registerSystemCharts() {
        // Register dashboard charts
        if (window.dashboard && window.dashboard.charts) {
            Object.entries(window.dashboard.charts).forEach(([key, chart]) => {
                if (chart && this.isChartRenderable(chart)) {
                    const chartId = `dashboard_${key}`;
                    this.charts.set(chartId, chart);
                    console.log(`Registered dashboard chart: ${chartId}`);
                }
            });
        }

        // Register analytics charts
        if (window.advancedAnalytics && window.advancedAnalytics.charts) {
            Object.entries(window.advancedAnalytics.charts).forEach(([key, chart]) => {
                if (chart && this.isChartRenderable(chart)) {
                    const chartId = `analytics_${key}`;
                    this.charts.set(chartId, chart);
                    console.log(`Registered analytics chart: ${chartId}`);
                }
            });
        }

        // Register analyticsCharts from window
        if (window.analyticsCharts) {
            Object.entries(window.analyticsCharts).forEach(([key, chart]) => {
                if (chart && this.isChartRenderable(chart)) {
                    const chartId = `window_analytics_${key}`;
                    this.charts.set(chartId, chart);
                    console.log(`Registered window analytics chart: ${chartId}`);
                }
            });
        }
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
            
            console.log(`Connecting to WebSocket: ${wsUrl}`);
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected successfully!');
                this.retryCount = 0;
                this.showStatus('WebSocket Connected - Real-time active', 'success');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketUpdate(data);
                } catch (error) {
                    console.warn('WebSocket message parse error:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket closed:', event.code, event.reason);
                this.showStatus('WebSocket Closed - Using HTTP polling', 'warning');
                
                // Try to reconnect after delay
                if (!this.manualClose && this.retryCount < this.maxRetries) {
                    setTimeout(() => {
                        this.retryCount++;
                        console.log(`WebSocket retry ${this.retryCount}/${this.maxRetries}`);
                        this.connectWebSocket();
                    }, 5000);
                }
            };
            
            this.websocket.onerror = (error) => {
                console.warn('WebSocket error:', error);
                // Don't show error for normal network issues
                if (this.websocket.readyState === WebSocket.CONNECTING) {
                    this.showStatus('WebSocket connecting...', 'normal');
                }
            };
            
        } catch (error) {
            console.error('WebSocket connection failed:', error);
            this.showStatus('WebSocket unavailable - HTTP polling active', 'warning');
        }
    }

    handleWebSocketUpdate(data) {
        console.log('WebSocket update received:', data);
        this.updateCount++;
        this.fetchAndUpdateData();
        this.showStatus(`Live Update #${this.updateCount}`, 'success');
    }

    startPeriodicUpdates() {
        console.log('Starting periodic HTTP updates...');
        
        // Update immediately
        setTimeout(() => {
            this.fetchAndUpdateData();
        }, 1000);
        
        // Then set interval
        setInterval(() => {
            // Only update via HTTP if WebSocket is not connected
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                this.fetchAndUpdateData();
                this.showStatus(`HTTP Update #${++this.updateCount}`, 'normal');
            }
        }, this.updateInterval);
    }

    async fetchAndUpdateData() {
        try {
            const now = Date.now();
            
            // Throttle updates to avoid spamming
            if (now - this.lastDataUpdate < 2000) {
                console.log('Update throttled, skipping...');
                return;
            }
            
            this.lastDataUpdate = now;
            console.log('Fetching latest data...');
            
            // Try multiple API endpoints with fallback
            let alerts = [];
            
            // Primary endpoint
            try {
                const response = await this.fetchWithTimeout('/api/alerts/?limit=100', 3000);
                if (response.ok) {
                    const data = await response.json();
                    alerts = Array.isArray(data) ? data : [];
                    console.log(`Loaded ${alerts.length} alerts from primary API`);
                }
            } catch (error) {
                console.warn('Primary API failed:', error.message);
            }
            
            // Fallback to sample data if needed
            if (alerts.length === 0) {
                console.log('Using sample data as fallback');
                alerts = this.generateSampleData();
            }
            
            // Update charts and metrics
            this.updateAllCharts(alerts);
            this.updateMetrics(alerts);
            
            // Update analytics charts
            if (window.advancedAnalytics) {
                window.advancedAnalytics.updateAllCharts();
            }
            
        } catch (error) {
            console.error('Data fetch error:', error);
            // Use sample data as ultimate fallback
            const sampleAlerts = this.generateSampleData();
            this.updateAllCharts(sampleAlerts);
            this.updateMetrics(sampleAlerts);
            this.showStatus('Using sample data', 'warning');
        }
    }

    async fetchWithTimeout(url, timeout = 5000) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);
        
        try {
            const response = await fetch(url, {
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    generateSampleData() {
        const severities = ['critical', 'high', 'medium', 'low'];
        const categories = ['malware', 'network_anomaly', 'unauthorized_access', 'brute_force', 'policy_violation'];
        
        return Array.from({length: 25}, (_, i) => ({
            _id: `sample_${Date.now()}_${i}`,
            title: `Sample Alert ${i + 1}`,
            severity: severities[Math.floor(Math.random() * severities.length)],
            category: categories[Math.floor(Math.random() * categories.length)],
            timestamp: new Date(Date.now() - Math.random() * 3600000).toISOString(),
            source_ip: `192.168.1.${Math.floor(Math.random() * 255)}`,
            risk_score: Math.floor(Math.random() * 100),
            confidence: Math.random(),
            status: 'new'
        }));
    }

    updateAllCharts(alerts) {
        console.log(`Updating ${this.charts.size} charts with ${alerts.length} alerts`);
        const invalidCharts = [];
        
        this.charts.forEach((chart, chartId) => {
            if (!this.isChartRenderable(chart)) {
                console.warn(`Removing invalid or detached chart ${chartId}`);
                invalidCharts.push(chartId);
                return;
            }
            try {
                this.updateChart(chart, alerts, chartId);
            } catch (error) {
                console.error(`Error updating chart ${chartId}:`, error);
            }
        });

        invalidCharts.forEach(chartId => this.charts.delete(chartId));
    }

    isChartRenderable(chart) {
        return !!(
            chart &&
            chart.data &&
            chart.canvas &&
            chart.canvas.ownerDocument &&
            typeof chart.update === 'function'
        );
    }

    updateChart(chart, alerts, chartId) {
        console.log(`=== DEBUG: Updating chart ${chartId} ===`);
        console.log(`Chart renderable:`, this.isChartRenderable(chart));
        console.log(`Alerts available:`, alerts?.length || 0);
        console.log(`Chart type:`, chart.config?.type);
        console.log(`Chart data before update:`, {
            labels: chart.data?.labels?.length || 0,
            datasets: chart.data?.datasets?.length || 0,
            hasData: !!chart.data
        });
        
        if (!this.isChartRenderable(chart)) {
            console.warn(`❌ Chart ${chartId} is not renderable`);
            return;
        }
        
        if (!alerts || !alerts.length) {
            console.warn(`❌ No alerts available for chart ${chartId}`);
            return;
        }
        
        const chartType = chart.config.type;
        
        try {
            console.log(`🔄 Updating ${chartType} chart ${chartId} with ${alerts.length} alerts`);
            
            switch (chartType) {
                case 'line':
                    this.updateLineChart(chart, alerts);
                    break;
                case 'pie':
                case 'doughnut':
                    this.updatePieChart(chart, alerts);
                    break;
                case 'bar':
                    this.updateBarChart(chart, alerts);
                    break;
                default:
                    this.updateGenericChart(chart, alerts);
            }
            
            console.log(`Chart data after update:`, {
                labels: chart.data?.labels?.length || 0,
                datasets: chart.data?.datasets?.length || 0,
                firstDatasetData: chart.data?.datasets?.[0]?.data?.length || 0
            });
            
            // Update chart without animation for better performance
            chart.update('none');
            console.log(`✅ Successfully updated chart ${chartId}`);
            
        } catch (error) {
            console.error(`❌ Chart update error for ${chartId}:`, error);
            console.error('Error details:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            
            // Try to update with sample data as fallback
            try {
                console.log(`🔄 Trying fallback update for ${chartId}`);
                const sampleAlerts = this.generateSampleData();
                this.updateChart(chart, sampleAlerts, chartId);
            } catch (fallbackError) {
                console.error(`❌ Fallback update failed for ${chartId}:`, fallbackError);
            }
        }
    }

    updateLineChart(chart, alerts) {
        if (!alerts.length) return;
        
        const timeData = {};
        alerts.forEach(alert => {
            const time = new Date(alert.timestamp);
            const key = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            timeData[key] = (timeData[key] || 0) + 1;
        });

        const sortedKeys = Object.keys(timeData).sort().slice(-15);
        const labels = sortedKeys;
        const data = sortedKeys.map(key => timeData[key]);

        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
    }

    updatePieChart(chart, alerts) {
        const severityCounts = { critical: 0, high: 0, medium: 0, low: 0 };
        
        alerts.forEach(alert => {
            const severity = alert.severity || 'low';
            if (severityCounts.hasOwnProperty(severity)) {
                severityCounts[severity]++;
            }
        });

        if (chart.data.labels.length === 4) {
            chart.data.datasets[0].data = Object.values(severityCounts);
        } else {
            const categoryCounts = {};
            alerts.forEach(alert => {
                const category = alert.category || 'unknown';
                categoryCounts[category] = (categoryCounts[category] || 0) + 1;
            });

            const categories = Object.keys(categoryCounts);
            chart.data.labels = categories;
            chart.data.datasets[0].data = Object.values(categoryCounts);
        }
    }

    updateBarChart(chart, alerts) {
        const categoryCounts = {};
        alerts.forEach(alert => {
            const category = alert.category || 'unknown';
            categoryCounts[category] = (categoryCounts[category] || 0) + 1;
        });

        const topCategories = Object.entries(categoryCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 8);

        chart.data.labels = topCategories.map(([cat]) => cat);
        chart.data.datasets[0].data = topCategories.map(([, count]) => count);
    }

    updateGenericChart(chart, alerts) {
        if (!alerts.length) return;
        
        const recentAlerts = alerts.slice(0, 10);
        const labels = recentAlerts.map((_, index) => `T${index + 1}`);
        const data = recentAlerts.map(alert => alert.risk_score || Math.random() * 100);

        if (chart.data.labels) {
            chart.data.labels = labels;
        }
        if (chart.data.datasets[0]) {
            chart.data.datasets[0].data = data;
        }
    }

    updateMetrics(alerts) {
        // Update KPI cards if they exist
        const kpis = {
            'total-count': alerts.length,
            'critical-count': alerts.filter(a => a.severity === 'critical').length,
            'high-count': alerts.filter(a => a.severity === 'high').length,
            'medium-count': alerts.filter(a => a.severity === 'medium').length,
            'low-count': alerts.filter(a => a.severity === 'low').length
        };

        Object.entries(kpis).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    showStatus(message, type = 'normal') {
        console.log(`[Status] ${message}`);
        
        // Update status indicator if exists
        const statusElement = document.querySelector('.live-indicator span:last-child');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = type;
        }
    }

    // Public methods
    forceUpdate() {
        console.log('Force updating all charts...');
        this.fetchAndUpdateData();
    }

    addChart(chartId, chart) {
        this.charts.set(chartId, chart);
        console.log(`Added chart: ${chartId}`);
    }

    destroy() {
        this.manualClose = true;
        if (this.websocket) {
            this.websocket.close();
        }
        this.charts.clear();
        this.isRunning = false;
    }
}

// Auto-initialize
window.robustRealtimeSystem = new RobustRealtimeSystem();

// Global functions for manual control
window.forceGraphUpdate = () => {
    window.robustRealtimeSystem.forceUpdate();
};

window.addRealtimeChart = (chartId, chart) => {
    window.robustRealtimeSystem.addChart(chartId, chart);
};

console.log('Robust Real-Time System loaded successfully!');
