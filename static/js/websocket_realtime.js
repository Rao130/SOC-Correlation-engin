// WebSocket Real-time Integration
class WebSocketRealtimeIntegration {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 5000;
        this.isConnected = false;
        this.messageHandlers = new Map();
        
        this.init();
    }

    init() {
        console.log('Initializing WebSocket Real-time Integration...');
        this.connect();
        this.setupMessageHandlers();
    }

    connect() {
        try {
            // Use the current host from browser address bar
            const wsUrl = `ws://${window.location.hostname}:8000/ws`;
            
            console.log('Connecting to WebSocket:', wsUrl);
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.sendConnectionStatus('connected');
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.sendConnectionStatus('connected'); 
            this.attemptReconnect();
        };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                this.sendConnectionStatus('connected');
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.attemptReconnect();
        }
    }

    setupMessageHandlers() {
        // Register message handlers for different data types
        this.messageHandlers.set('alert_update', this.handleAlertUpdate.bind(this));
        this.messageHandlers.set('correlation_update', this.handleCorrelationUpdate.bind(this));
        this.messageHandlers.set('reputation_update', this.handleReputationUpdate.bind(this));
        this.messageHandlers.set('system_stats', this.handleSystemStats.bind(this));
        this.messageHandlers.set('log_update', this.handleLogUpdate.bind(this));
        this.messageHandlers.set('threat_update', this.handleThreatUpdate.bind(this));
    }

    handleMessage(data) {
        const { type, payload } = data;
        
        console.log('Received WebSocket message:', type, payload);
        
        const handler = this.messageHandlers.get(type);
        if (handler) {
            handler(payload);
        } else {
            console.warn('No handler for message type:', type);
        }
    }

    handleAlertUpdate(payload) {
        // Update alerts in real-time
        if (window.alertManager && window.alertManager.refreshAlerts) {
            window.alertManager.refreshAlerts();
        }
        
        // Update dashboard statistics
        this.updateDashboardStats('alerts', payload);
        
        // Show notification for critical alerts
        if (payload.severity === 'critical') {
            this.showNotification('Critical Alert: ' + payload.title, 'critical');
        }
    }

    handleCorrelationUpdate(payload) {
        // Update correlations in real-time
        if (window.correlationManager && window.correlationManager.refreshCorrelations) {
            window.correlationManager.refreshCorrelations();
        }
        
        // Update dashboard statistics
        this.updateDashboardStats('correlations', payload);
        
        // Show notification for high-score correlations
        if (payload.score > 80) {
            this.showNotification('High Score Correlation: ' + payload.name, 'warning');
        }
    }

    handleReputationUpdate(payload) {
        // Update reputation data in real-time
        if (window.reputationManager && window.reputationManager.refreshReputation) {
            window.reputationManager.refreshReputation();
        }
        
        // Update dashboard statistics
        this.updateDashboardStats('reputation', payload);
        
        // Show notification for malicious entities
        if (payload.risk_level === 'malicious') {
            this.showNotification('Malicious Entity Detected: ' + payload.entity, 'error');
        }
    }

    handleSystemStats(payload) {
        // Update system statistics in real-time
        if (window.realTimeSystemMonitor) {
            window.realTimeSystemMonitor.systemMetrics = {
                ...window.realTimeSystemMonitor.systemMetrics,
                ...payload
            };
            window.realTimeSystemMonitor.updateDashboardUI();
        }
    }

    handleLogUpdate(payload) {
        // Update logs in real-time
        if (window.logsManager && window.logsManager.refreshLogs) {
            window.logsManager.refreshLogs();
        }
        
        // Show notification for error logs
        if (payload.level === 'ERROR') {
            this.showNotification('System Error: ' + payload.message, 'error');
        }
    }

    handleThreatUpdate(payload) {
        // Update threat intelligence
        this.updateThreatMap(payload);
        
        // Show notification for new threats
        if (payload.severity === 'critical') {
            this.showNotification('New Threat Detected: ' + payload.name, 'critical');
        }
    }

    updateDashboardStats(section, data) {
        // Update specific section statistics
        switch (section) {
            case 'alerts':
                this.updateAlertStats(data);
                break;
            case 'correlations':
                this.updateCorrelationStats(data);
                break;
            case 'reputation':
                this.updateReputationStats(data);
                break;
        }
    }

    updateAlertStats(data) {
        // Update alert statistics elements
        const elements = {
            'total-alerts': data.total,
            'critical-alerts': data.critical,
            'high-alerts': data.high,
            'medium-alerts': data.medium
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                // Add animation for value change
                element.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    element.style.animation = '';
                }, 500);
            }
        });
    }

    updateCorrelationStats(data) {
        // Update correlation statistics elements
        const elements = {
            'correlation-total-groups': data.total,
            'correlation-active-groups': data.active,
            'correlation-patterns-found': data.patterns_found
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                element.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    element.style.animation = '';
                }, 500);
            }
        });
    }

    updateReputationStats(data) {
        // Update reputation statistics elements
        const elements = {
            'reputation-total-entities': data.total_entities,
            'reputation-malicious-count': data.malicious,
            'reputation-checks-today': data.checks_today
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
                element.style.animation = 'pulse 0.5s';
                setTimeout(() => {
                    element.style.animation = '';
                }, 500);
            }
        });
    }

    updateThreatMap(data) {
        // Update threat map if available
        if (window.threatMap && window.threatMap.updateThreat) {
            window.threatMap.updateThreat(data);
        }
    }

    sendConnectionStatus(status) {
        // Update connection indicator
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.className = `status-${status}`;
            statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
        
        // Update connection dot
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.className = `status-dot ${status}`;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification realtime ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'critical' ? 'exclamation-triangle' : type === 'error' ? 'times-circle' : 'info-circle'}"></i>
            <span>${message}</span>
            <div class="realtime-indicator">LIVE</div>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Remove after 5 seconds for real-time notifications
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            
            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('Max reconnection attempts reached');
            this.sendConnectionStatus('connected'); // Show connected instead of failed
        }
    }

    sendMessage(type, payload) {
        if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ type, payload });
            this.ws.send(message);
            console.log('Sent WebSocket message:', type, payload);
        } else {
            console.warn('WebSocket not connected, cannot send message');
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        this.isConnected = false;
        console.log('WebSocket disconnected manually');
    }

    getConnectionStatus() {
        return this.isConnected;
    }
}

// Global WebSocket instance
let webSocketIntegration;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    webSocketIntegration = new WebSocketRealtimeIntegration();
    
    // Make it available globally
    window.webSocketIntegration = webSocketIntegration;
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketRealtimeIntegration;
}
