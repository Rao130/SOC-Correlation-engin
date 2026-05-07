/**
 * Real-time Dashboard Controller
 * Manages WebSocket connections and live data updates for SOC dashboard
 */

class RealtimeDashboard {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnectDelay = 3000;
        this.isConnected = false;
        this.clientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        this.heartbeatInterval = null;
        this.updateCallbacks = new Map();
        
        // Dashboard state
        this.currentAlerts = [];
        this.alertStats = {};
        this.networkStatus = {};
        
        console.log(`RealtimeDashboard initialized with client ID: ${this.clientId}`);
    }
    
    async connect() {
        try {
            console.log('Connecting to WebSocket...');
            
            // Determine WebSocket URL
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${this.clientId}`;
            
            console.log(`WebSocket URL: ${wsUrl}`);
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected successfully');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.startHeartbeat();
                this.updateConnectionStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    this.handleMessage(message);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket connection closed:', event.code, event.reason);
                this.isConnected = false;
                this.stopHeartbeat();
                this.updateConnectionStatus(false);
                
                // Don't reconnect on normal closure
                if (event.code !== 1000) {
                    this.handleReconnect();
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };
            
            // Set connection timeout
            setTimeout(() => {
                if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
                    console.log('WebSocket connection timeout');
                    this.ws.close();
                    this.handleReconnect();
                }
            }, 10000);
            
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.handleReconnect();
        }
    }
    
    handleMessage(message) {
        console.log('Received WebSocket message:', message.type);
        
        switch (message.type) {
            case 'initial_data':
                this.handleInitialData(message.data);
                break;
            case 'new_alert':
                this.handleNewAlert(message.data);
                break;
            case 'metrics_update':
                this.handleMetricsUpdate(message.data);
                break;
            case 'analytics_update':
                this.handleAnalyticsUpdate(message.data);
                break;
            case 'alerts_response':
                this.handleAlertsResponse(message.data);
                break;
            case 'stats_response':
                this.handleStatsResponse(message.data);
                break;
            case 'pong':
                // Heartbeat response
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    handleInitialData(data) {
        console.log('Received initial data');
        
        this.currentAlerts = data.recent_alerts || [];
        this.alertStats = data.alert_stats || {};
        this.networkStatus = data.network_status || {};
        
        // Update all dashboard components
        this.updateAlertsTable(this.currentAlerts);
        this.updateKPIs(this.alertStats);
        this.updateNetworkStatus(this.networkStatus);
        
        // Trigger callbacks
        this.triggerCallbacks('initial_data', data);
    }
    
    handleNewAlert(alert) {
        console.log('New alert received:', alert.title);
        
        // Add to current alerts
        this.currentAlerts.unshift(alert);
        
        // Keep only last 100 alerts
        if (this.currentAlerts.length > 100) {
            this.currentAlerts = this.currentAlerts.slice(0, 100);
        }
        
        // Update UI
        this.updateAlertsTable(this.currentAlerts);
        this.updateAlertCounters();
        
        // Show notification
        this.showAlertNotification(alert);
        
        // Trigger callbacks
        this.triggerCallbacks('new_alert', alert);
    }
    
    handleMetricsUpdate(metrics) {
        console.log('Metrics update received');
        this.networkStatus = metrics;
        this.updateNetworkStatus(metrics);
        this.triggerCallbacks('metrics_update', metrics);
    }
    
    handleAnalyticsUpdate(analytics) {
        console.log('Analytics update received');
        
        if (analytics.alert_statistics) {
            this.alertStats = analytics.alert_statistics;
            this.updateKPIs(this.alertStats);
        }
        
        this.triggerCallbacks('analytics_update', analytics);
    }
    
    handleAlertsResponse(alerts) {
        console.log('Alerts response received:', alerts.length);
        this.currentAlerts = alerts;
        this.updateAlertsTable(alerts);
        this.triggerCallbacks('alerts_response', alerts);
    }
    
    handleStatsResponse(stats) {
        console.log('Stats response received');
        this.alertStats = stats;
        this.updateKPIs(stats);
        this.triggerCallbacks('stats_response', stats);
    }
    
    updateAlertsTable(alerts) {
        const tbody = document.getElementById('recent-alerts-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        alerts.slice(0, 10).forEach(alert => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><input type="checkbox"></td>
                <td><span class="severity-bar ${alert.severity}" style="width: ${this.getSeverityWidth(alert.severity)}%"></span> ${this.getSeverityScore(alert.severity)}</td>
                <td>${alert._id || 'N/A'}</td>
                <td>${alert.title || 'N/A'}</td>
                <td><span class="ip-tag">${this.extractIPFromAlert(alert)}</span></td>
                <td>${alert.category || 'N/A'}</td>
                <td><span class="source-tag">${alert.source || 'N/A'}</span></td>
                <td><span class="status-tag">${alert.status || 'new'}</span></td>
                <td><button class="action-btn" onclick="viewAlert('${alert._id}')"><i class="fas fa-eye"></i></button></td>
            `;
            tbody.appendChild(row);
        });
    }
    
    updateKPIs(stats) {
        // Update KPI cards
        const kpiElements = {
            'critical-count': stats.by_severity?.critical || 0,
            'high-count': stats.by_severity?.high || 0,
            'medium-count': stats.by_severity?.medium || 0,
            'low-count': stats.by_severity?.low || 0,
            'total-count': stats.total || 0
        };
        
        Object.entries(kpiElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                // Add animation
                element.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            }
        });
    }
    
    updateNetworkStatus(status) {
        // Update network monitoring status
        const statusElement = document.querySelector('.live-indicator');
        if (statusElement) {
            const dot = statusElement.querySelector('.live-dot');
            if (status.monitoring_active) {
                dot.style.backgroundColor = '#10b981';
            } else {
                dot.style.backgroundColor = '#ef4444';
            }
        }
        
        // Update network metrics if available
        if (status.memory_alerts_count !== undefined) {
            const networkAlertsElement = document.getElementById('network-notables');
            if (networkAlertsElement) {
                networkAlertsElement.textContent = status.memory_alerts_count;
            }
        }
    }
    
    updateAlertCounters() {
        const severityCounts = {
            critical: 0,
            high: 0,
            medium: 0,
            low: 0
        };
        
        this.currentAlerts.forEach(alert => {
            if (severityCounts.hasOwnProperty(alert.severity)) {
                severityCounts[alert.severity]++;
            }
        });
        
        Object.entries(severityCounts).forEach(([severity, count]) => {
            const element = document.getElementById(`${severity}-count`);
            if (element) {
                element.textContent = count;
            }
        });
    }
    
    showAlertNotification(alert) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert-notification ${alert.severity}`;
        notification.innerHTML = `
            <div class="notification-content">
                <strong>${alert.title}</strong>
                <p>${alert.description}</p>
                <small>${new Date(alert.timestamp).toLocaleString()}</small>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.querySelector('.live-indicator span:last-child');
        if (statusElement) {
            statusElement.textContent = connected ? 'Live Data' : 'Disconnected';
        }
    }
    
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Send ping every 30 seconds
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }
    
    handleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.updateConnectionStatus(false);
        }
    }
    
    // Public methods for manual data requests
    requestAlerts(limit = 50) {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'request_alerts',
                limit: limit
            }));
        }
    }
    
    requestStats() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'request_stats'
            }));
        }
    }
    
    generateAlerts(count = 5) {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'generate_alerts',
                count: count
            }));
        }
    }
    
    // Callback registration
    on(event, callback) {
        if (!this.updateCallbacks.has(event)) {
            this.updateCallbacks.set(event, []);
        }
        this.updateCallbacks.get(event).push(callback);
    }
    
    off(event, callback) {
        if (this.updateCallbacks.has(event)) {
            const callbacks = this.updateCallbacks.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }
    
    triggerCallbacks(event, data) {
        if (this.updateCallbacks.has(event)) {
            this.updateCallbacks.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error('Error in callback:', error);
                }
            });
        }
    }
    
    // Utility methods
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
    
    disconnect() {
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
    }
}

// Global instance
window.realtimeDashboard = new RealtimeDashboard();

// Auto-connect when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeDashboard.connect();
});

// Add notification styles
const notificationStyles = `
<style>
.alert-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: white;
    border-left: 4px solid #ef4444;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    padding: 16px;
    max-width: 400px;
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
}

.alert-notification.critical {
    border-left-color: #dc2626;
}

.alert-notification.high {
    border-left-color: #ea580c;
}

.alert-notification.medium {
    border-left-color: #d97706;
}

.alert-notification.low {
    border-left-color: #65a30d;
}

.notification-content strong {
    display: block;
    margin-bottom: 4px;
    color: #1f2937;
}

.notification-content p {
    margin: 4px 0;
    color: #6b7280;
    font-size: 14px;
}

.notification-content small {
    color: #9ca3af;
    font-size: 12px;
}

.notification-close {
    position: absolute;
    top: 8px;
    right: 8px;
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #9ca3af;
}

.notification-close:hover {
    color: #6b7280;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', notificationStyles);
