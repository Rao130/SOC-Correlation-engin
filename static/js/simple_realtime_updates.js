/**
 * Simple Real-Time Graph Updates
 * Direct and effective real-time updates for all charts
 */

class SimpleRealtimeUpdates {
    constructor() {
        this.isRunning = false;
        this.updateInterval = 3000; // 3 seconds
        this.websocket = null;
        this.charts = new Map();
        this.updateCount = 0;
        
        this.init();
    }

    init() {
        console.log('Starting Simple Real-Time Updates...');
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.start());
        } else {
            this.start();
        }
    }

    start() {
        console.log('Initializing Simple Real-Time Updates');
        
        // Register all existing charts
        this.registerAllCharts();
        
        // Start WebSocket connection
        this.connectWebSocket();
        
        // Start periodic updates as backup
        this.startPeriodicUpdates();
        
        this.isRunning = true;
    }

    registerAllCharts() {
        console.log('Registering all charts...');
        
        // Register Chart.js charts
        Chart.helpers.each(Chart.instances, (chart) => {
            const canvas = chart.canvas;
            const chartId = canvas.id || `chart_${this.charts.size}`;
            this.charts.set(chartId, chart);
            console.log(`Registered chart: ${chartId}`);
        });

        // Look for specific chart canvases
        const chartCanvases = document.querySelectorAll('canvas[id*="chart"], canvas[id*="Chart"], canvas[id*="graph"]');
        chartCanvases.forEach(canvas => {
            if (!this.charts.has(canvas.id)) {
                const chart = Chart.getChart(canvas);
                if (chart) {
                    this.charts.set(canvas.id, chart);
                    console.log(`Found additional chart: ${canvas.id}`);
                }
            }
        });

        console.log(`Total charts registered: ${this.charts.size}`);
    }

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            console.log(`Connecting to WebSocket: ${wsUrl}`);
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected successfully!');
                this.showStatus('Connected - Real-time updates active', 'success');
                this.retryCount = 0;
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleUpdate(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error, event.data);
                }
            };
            
            this.websocket.onclose = (event) => {
                console.log('WebSocket disconnected, code:', event.code, 'reason:', event.reason);
                this.showStatus('Disconnected - Using periodic updates', 'warning');
                
                // Try to reconnect after 3 seconds
                if (!this.manualClose) {
                    setTimeout(() => {
                        this.retryWebSocket();
                    }, 3000);
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showStatus('Connection error - Using fallback', 'error');
                
                // Don't show error for normal closure
                if (this.websocket && this.websocket.readyState === WebSocket.CLOSED) {
                    this.showStatus('Connection closed - Reconnecting...', 'warning');
                }
            };
            
        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.showStatus('WebSocket failed - Using HTTP polling', 'error');
        }
    }

    retryWebSocket() {
        if (this.retryCount < 5) {
            this.retryCount++;
            console.log(`Retrying WebSocket connection (${this.retryCount}/5)`);
            this.connectWebSocket();
        } else {
            console.log('Max WebSocket retries reached, using HTTP polling only');
            this.showStatus('WebSocket unavailable - Using HTTP polling', 'warning');
        }
    }

    async handleUpdate(data) {
        this.updateCount++;
        console.log(`Received update #${this.updateCount}:`, data);
        
        // Fetch fresh data
        await this.fetchAndUpdateData();
        
        // Update status
        this.showStatus(`Updated - ${this.updateCount} updates received`, 'success');
    }

    async fetchAndUpdateData() {
        try {
            console.log('Fetching latest data...');
            
            // Fetch latest alerts with timeout
            const alertsResponse = await Promise.race([
                fetch('/api/alerts/?limit=100'),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))
            ]);
            
            let alerts = [];
            if (alertsResponse.ok) {
                try {
                    alerts = await alertsResponse.json();
                    console.log(`Loaded ${alerts.length} alerts`);
                } catch (parseError) {
                    console.error('Error parsing alerts JSON:', parseError);
                    alerts = [];
                }
            } else {
                console.warn('Alerts API responded with status:', alertsResponse.status);
                // No sample data - show empty state
                alerts = [];
            }
            
            // Update all charts with new data
            if (alerts && alerts.length > 0) {
                this.updateAllCharts(alerts);
                this.updateMetrics(alerts);
            } else {
                console.log('No alerts data available - showing empty state');
                this.updateAllCharts([]);
                this.updateMetrics([]);
            }
            
        } catch (error) {
            console.error('Error fetching data:', error);
            // Show empty state on error
            this.updateAllCharts([]);
            this.updateMetrics([]);
            this.showStatus('No data available - API error', 'warning');
        }
    }

    // getSampleAlerts() function removed - no mock data in production

    updateAllCharts(alerts) {
        console.log(`Updating ${this.charts.size} charts with ${alerts.length} alerts`);
        
        this.charts.forEach((chart, chartId) => {
            try {
                this.updateChart(chart, alerts, chartId);
            } catch (error) {
                console.error(`Error updating chart ${chartId}:`, error);
            }
        });
    }

    updateChart(chart, alerts, chartId) {
        if (!chart || !chart.data) return;
        
        const chartType = chart.config.type;
        
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
        
        // Update without animation for smooth real-time updates
        chart.update('none');
    }

    updateLineChart(chart, alerts) {
        if (!alerts.length) return;
        
        // Create time series data
        const timeData = {};
        alerts.forEach(alert => {
            const time = new Date(alert.timestamp);
            const key = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            timeData[key] = (timeData[key] || 0) + 1;
        });

        const sortedKeys = Object.keys(timeData).sort().slice(-20);
        const labels = sortedKeys;
        const data = sortedKeys.map(key => timeData[key]);

        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
    }

    updatePieChart(chart, alerts) {
        // Update severity distribution
        const severityCounts = { critical: 0, high: 0, medium: 0, low: 0 };
        
        alerts.forEach(alert => {
            const severity = alert.severity || 'low';
            if (severityCounts.hasOwnProperty(severity)) {
                severityCounts[severity]++;
            }
        });

        if (chart.data.labels.length === 4 && 
            chart.data.labels.includes('Critical') && 
            chart.data.labels.includes('High')) {
            // Severity chart
            chart.data.datasets[0].data = Object.values(severityCounts);
        } else {
            // Category chart
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
        // Update category or pattern data
        const categoryCounts = {};
        alerts.forEach(alert => {
            const category = alert.category || 'unknown';
            categoryCounts[category] = (categoryCounts[category] || 0) + 1;
        });

        const topCategories = Object.entries(categoryCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);

        chart.data.labels = topCategories.map(([cat]) => cat);
        chart.data.datasets[0].data = topCategories.map(([, count]) => count);
    }

    updateGenericChart(chart, alerts) {
        // Generic update for any chart type
        const data = alerts.slice(0, 20).map((alert, index) => ({
            x: new Date(alert.timestamp).toLocaleTimeString(),
            y: alert.risk_score || Math.random() * 100
        }));

        if (chart.data.labels) {
            chart.data.labels = data.map(d => d.x);
        }
        if (chart.data.datasets[0]) {
            chart.data.datasets[0].data = data.map(d => d.y);
        }
    }

    updateMetrics(alerts) {
        // Update KPI cards
        const totalElement = document.getElementById('total-count');
        if (totalElement) {
            totalElement.textContent = alerts.length;
        }

        const criticalElement = document.getElementById('critical-count');
        if (criticalElement) {
            const count = alerts.filter(a => a.severity === 'critical').length;
            criticalElement.textContent = count;
        }

        const highElement = document.getElementById('high-count');
        if (highElement) {
            const count = alerts.filter(a => a.severity === 'high').length;
            highElement.textContent = count;
        }

        const mediumElement = document.getElementById('medium-count');
        if (mediumElement) {
            const count = alerts.filter(a => a.severity === 'medium').length;
            mediumElement.textContent = count;
        }

        const lowElement = document.getElementById('low-count');
        if (lowElement) {
            const count = alerts.filter(a => a.severity === 'low').length;
            lowElement.textContent = count;
        }

        // Update analytics KPIs
        this.updateAnalyticsKPIs(alerts);
    }

    updateAnalyticsKPIs(alerts) {
        const kpis = {
            'access-notables': alerts.filter(a => a.category === 'unauthorized_access').length,
            'endpoint-notables': alerts.filter(a => a.category === 'malware').length,
            'network-notables': alerts.filter(a => a.category === 'network_anomaly').length,
            'identity-notables': alerts.filter(a => a.category === 'brute_force').length,
            'audit-notables': alerts.filter(a => a.category === 'policy_violation').length,
            'threat-notables': alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length,
            'uba-notables': alerts.filter(a => a.category === 'anomaly').length
        };

        Object.entries(kpis).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                // Add pulse animation
                element.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    element.style.animation = '';
                }, 500);
            }
        });
    }

    startPeriodicUpdates() {
        // Start periodic updates as backup
        setInterval(async () => {
            if (!this.websocket || this.websocket.readyState !== WebSocket.OPEN) {
                console.log('Running periodic update...');
                await this.fetchAndUpdateData();
            }
        }, this.updateInterval);

        // Initial data fetch
        setTimeout(async () => {
            await this.fetchAndUpdateData();
        }, 1000);
    }

    showStatus(message, type) {
        // Update status indicator if exists
        const statusElement = document.querySelector('.live-indicator span:last-child');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = type;
        }

        // Log to console
        console.log(`[Real-Time Status] ${message}`);
    }

    // Public methods
    forceUpdate() {
        console.log('Force updating all charts...');
        this.fetchAndUpdateData();
    }

    addChart(chartId, chart) {
        this.charts.set(chartId, chart);
        console.log(`Added new chart: ${chartId}`);
    }

    removeChart(chartId) {
        this.charts.delete(chartId);
        console.log(`Removed chart: ${chartId}`);
    }
}

// Auto-initialize
window.simpleRealtimeUpdates = new SimpleRealtimeUpdates();

// Global functions for manual control
window.forceGraphUpdate = () => {
    window.simpleRealtimeUpdates.forceUpdate();
};

window.addRealtimeChart = (chartId, chart) => {
    window.simpleRealtimeUpdates.addChart(chartId, chart);
};

// Add CSS for status indicators
const style = document.createElement('style');
style.textContent = `
.live-indicator span.success { color: #4caf50; }
.live-indicator span.warning { color: #ff9800; }
.live-indicator span.error { color: #f44336; }

@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
}
`;
document.head.appendChild(style);

console.log('Simple Real-Time Updates loaded successfully!');
