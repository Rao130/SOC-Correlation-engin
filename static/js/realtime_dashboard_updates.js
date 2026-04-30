/**
 * Real-Time Dashboard Updates
 * Fetches and displays live data from SOC APIs
 */

class RealtimeDashboard {
    constructor() {
        this.refreshInterval = 5000; // 5 seconds
        this.isRunning = false;
        this.intervals = {};
    }

    async init() {
        console.log('Starting Real-Time Dashboard Updates...');
        
        // Start all real-time updates
        this.startAlertUpdates();
        this.startKPIUpdates();
        this.startNetworkUpdates();
        this.startLogUpdates();
        this.startAnalyticsUpdates();
        
        this.isRunning = true;
        console.log('Real-Time Dashboard Updates Started!');
    }

    // ALERTS UPDATES
    async startAlertUpdates() {
        // Initial load
        await this.loadAlerts();
        
        // Set interval for updates
        this.intervals.alerts = setInterval(async () => {
            await this.loadAlerts();
        }, this.refreshInterval);
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts/?limit=20');
            const alerts = await response.json();
            
            console.log(`Loaded ${alerts.length} alerts`);
            this.updateAlertsTable(alerts);
            this.updateAlertCounters(alerts);
            
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    updateAlertsTable(alerts) {
        const tbody = document.getElementById('recent-alerts-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        alerts.slice(0, 10).forEach(alert => {
            const row = document.createElement('tr');
            const severity = alert.severity || 'low';
            const severityWidth = this.getSeverityWidth(severity);
            const severityScore = this.getSeverityScore(severity);
            
            row.innerHTML = `
                <td><input type="checkbox"></td>
                <td><span class="severity-bar ${severity}" style="width: ${severityWidth}%"></span> ${severityScore}</td>
                <td>${alert._id || 'N/A'}</td>
                <td>${alert.title || 'No Title'}</td>
                <td><span class="ip-tag">${this.extractIPFromAlert(alert)}</span></td>
                <td>${alert.category || 'Unknown'}</td>
                <td><span class="source-tag">${alert.source || 'Unknown'}</span></td>
                <td><span class="status-tag">${alert.status || 'new'}</span></td>
                <td><button class="action-btn" onclick="viewAlert('${alert._id}')"><i class="fas fa-eye"></i></button></td>
            `;
            tbody.appendChild(row);
        });
    }

    updateAlertCounters(alerts) {
        const severityCounts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };
        
        alerts.forEach(alert => {
            const severity = alert.severity || 'low';
            if (severityCounts.hasOwnProperty(severity)) {
                severityCounts[severity]++;
            }
        });
        
        // Update KPI cards
        Object.entries(severityCounts).forEach(([severity, count]) => {
            const element = document.getElementById(`${severity}-count`);
            if (element) {
                element.textContent = count;
                // Add animation
                element.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            }
        });
        
        // Update total alerts
        const totalElement = document.getElementById('total-count');
        if (totalElement) {
            totalElement.textContent = alerts.length;
        }
    }

    // KPI UPDATES
    async startKPIUpdates() {
        await this.loadKPIs();
        
        this.intervals.kpis = setInterval(async () => {
            await this.loadKPIs();
        }, this.refreshInterval);
    }

    async loadKPIs() {
        try {
            // Load alerts for KPI calculation
            const response = await fetch('/api/alerts/?limit=1000');
            const alerts = await response.json();
            
            this.updateMainKPIs(alerts);
            
        } catch (error) {
            console.error('Error loading KPIs:', error);
        }
    }

    updateMainKPIs(alerts) {
        // Calculate KPIs based on real data
        const kpis = {
            'access-notables': alerts.filter(a => a.category === 'unauthorized_access').length,
            'endpoint-notables': alerts.filter(a => a.category === 'malware').length,
            'network-notables': alerts.filter(a => a.category === 'network_anomaly').length,
            'identity-notables': alerts.filter(a => a.category === 'brute_force').length,
            'audit-notables': alerts.filter(a => a.category === 'policy_violation').length,
            'threat-notables': alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length,
            'uba-notables': alerts.filter(a => a.category === 'anomaly').length
        };
        
        // Update KPI elements
        Object.entries(kpis).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                // Add pulse animation for changes
                if (value > 0) {
                    element.style.animation = 'pulse 1s';
                    setTimeout(() => {
                        element.style.animation = '';
                    }, 1000);
                }
            }
        });
    }

    // NETWORK UPDATES
    async startNetworkUpdates() {
        await this.loadNetworkData();
        
        this.intervals.network = setInterval(async () => {
            await this.loadNetworkData();
        }, this.refreshInterval);
    }

    async loadNetworkData() {
        try {
            const [metricsResponse, connectionsResponse] = await Promise.all([
                fetch('/api/network/metrics'),
                fetch('/api/network/connections')
            ]);
            
            const metrics = await metricsResponse.json();
            const connections = await connectionsResponse.json();
            
            this.updateNetworkMetrics(metrics, connections);
            
        } catch (error) {
            console.error('Error loading network data:', error);
        }
    }

    updateNetworkMetrics(metrics, connections) {
        // Update network metrics display
        const metricsContainer = document.getElementById('network-metrics');
        if (metricsContainer) {
            metricsContainer.innerHTML = `
                <div class="metric-item">
                    <span class="metric-label">Active Connections:</span>
                    <span class="metric-value">${metrics.active_connections || 0}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Bytes Sent:</span>
                    <span class="metric-value">${this.formatBytes(metrics.bytes_sent || 0)}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Bytes Received:</span>
                    <span class="metric-value">${this.formatBytes(metrics.bytes_recv || 0)}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Packets Sent:</span>
                    <span class="metric-value">${metrics.packets_sent || 0}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Packets Received:</span>
                    <span class="metric-value">${metrics.packets_recv || 0}</span>
                </div>
            `;
        }
        
        // Update connections display
        const connectionsContainer = document.getElementById('network-connections');
        if (connectionsContainer && connections.connections) {
            connectionsContainer.innerHTML = connections.connections.slice(0, 5).map(conn => `
                <div class="connection-item">
                    <span class="connection-local">${conn.local_address}</span>
                    <span class="connection-arrow">-></span>
                    <span class="connection-remote">${conn.remote_address}</span>
                    <span class="connection-status">${conn.status}</span>
                </div>
            `).join('');
        }
    }

    // LOG UPDATES
    async startLogUpdates() {
        await this.loadLogs();
        
        this.intervals.logs = setInterval(async () => {
            await this.loadLogs();
        }, this.refreshInterval);
    }

    async loadLogs() {
        try {
            const response = await fetch('/api/logs/realtime?limit=20');
            const data = await response.json();
            
            this.updateLogsDisplay(data.logs || []);
            
        } catch (error) {
            console.error('Error loading logs:', error);
        }
    }

    updateLogsDisplay(logs) {
        const logsContainer = document.getElementById('logs-container');
        if (!logsContainer) return;
        
        logsContainer.innerHTML = logs.slice(0, 10).map(log => `
            <div class="log-entry ${log.severity?.toLowerCase()}">
                <span class="log-timestamp">${new Date(log.timestamp).toLocaleTimeString()}</span>
                <span class="log-source">[${log.source}]</span>
                <span class="log-severity">${log.severity}</span>
                <span class="log-message">${log.message}</span>
            </div>
        `).join('');
    }

    // ANALYTICS UPDATES
    async startAnalyticsUpdates() {
        await this.loadAnalytics();
        
        this.intervals.analytics = setInterval(async () => {
            await this.loadAnalytics();
        }, this.refreshInterval * 2); // Update analytics less frequently
    }

    async loadAnalytics() {
        try {
            const [statsResponse, timelineResponse] = await Promise.all([
                fetch('/api/analytics/realtime-stats'),
                fetch('/api/analytics/attack-timeline')
            ]);
            
            const stats = await statsResponse.json();
            const timeline = await timelineResponse.json();
            
            this.updateAnalyticsDisplay(stats, timeline);
            
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    updateAnalyticsDisplay(stats, timeline) {
        // Update statistics
        if (stats.alert_statistics) {
            const alertStats = stats.alert_statistics;
            this.updateAnalyticsStats(alertStats);
        }
        
        // Update timeline chart if exists
        if (window.attackTimelineChart && timeline.timeline) {
            this.updateTimelineChart(timeline.timeline);
        }
    }

    updateAnalyticsStats(stats) {
        // Update correlation stats
        const elements = {
            'correlation-total-groups': stats.total || 0,
            'correlation-active-groups': stats.last_hour || 0,
            'correlation-patterns-found': Object.keys(stats.by_category || {}).length,
            'correlation-avg-score': Math.round((stats.by_severity?.high || 0) / 10 * 100) / 10
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    updateTimelineChart(timelineData) {
        if (!window.attackTimelineChart) return;
        
        const labels = timelineData.map(item => 
            new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        );
        const data = timelineData.map(item => item.total);
        
        window.attackTimelineChart.data.labels = labels;
        window.attackTimelineChart.data.datasets[0].data = data;
        window.attackTimelineChart.update();
    }

    // UTILITY FUNCTIONS
    getSeverityWidth(severity) {
        const widths = {
            critical: 90,
            high: 70,
            medium: 50,
            low: 30
        };
        return widths[severity] || 30;
    }

    getSeverityScore(severity) {
        const scores = {
            critical: 9,
            high: 7,
            medium: 5,
            low: 3
        };
        return scores[severity] || 1;
    }

    extractIPFromAlert(alert) {
        if (alert.entities && Array.isArray(alert.entities)) {
            const ipEntity = alert.entities.find(entity => entity.type === 'ip_address');
            if (ipEntity) {
                return ipEntity.value;
            }
        }
        return 'N/A';
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // STOP ALL UPDATES
    stop() {
        Object.values(this.intervals).forEach(interval => {
            clearInterval(interval);
        });
        this.isRunning = false;
        console.log('Real-Time Dashboard Updates Stopped');
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Wait a bit for other scripts to load
    setTimeout(() => {
        window.realtimeDashboard = new RealtimeDashboard();
        window.realtimeDashboard.init();
    }, 1000);
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); }
}

.log-entry {
    padding: 8px;
    margin: 2px 0;
    border-left: 3px solid #ccc;
    font-family: monospace;
    font-size: 12px;
    background: #f9f9f9;
}

.log-entry.critical { border-left-color: #dc2626; background: #fef2f2; }
.log-entry.high { border-left-color: #ea580c; background: #fff7ed; }
.log-entry.medium { border-left-color: #d97706; background: #fffbeb; }
.log-entry.low { border-left-color: #10b981; background: #f0fdf4; }

.log-timestamp { color: #6b7280; margin-right: 8px; }
.log-source { color: #374151; margin-right: 8px; font-weight: bold; }
.log-severity { color: #059669; margin-right: 8px; }
.log-message { color: #111827; }

.metric-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px solid #e5e7eb;
}

.metric-label { color: #6b7280; }
.metric-value { font-weight: bold; color: #111827; }

.connection-item {
    display: flex;
    align-items: center;
    padding: 4px 0;
    font-family: monospace;
    font-size: 12px;
}

.connection-local { color: #059669; }
.connection-arrow { color: #6b7280; margin: 0 8px; }
.connection-remote { color: #dc2626; }
.connection-status { color: #374151; margin-left: 8px; }
`;
document.head.appendChild(style);
