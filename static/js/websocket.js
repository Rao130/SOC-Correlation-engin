// WebSocket client for real-time updates
class WebSocketManager {
    constructor() {
        this.ws = null;
        this.reconnectInterval = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect(url) {
        try {
            this.ws = new WebSocket(url);
            
            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.reconnectAttempts = 0;
                if (this.reconnectInterval) {
                    clearInterval(this.reconnectInterval);
                    this.reconnectInterval = null;
                }
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected:', event.code, event.reason);
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.attemptReconnect();
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.attemptReconnect();
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            this.reconnectInterval = setTimeout(() => {
                this.connect(this.url);
            }, 3000); // Wait 3 seconds before reconnecting
        } else {
            console.error('Max reconnection attempts reached');
            if (this.reconnectInterval) {
                clearInterval(this.reconnectInterval);
            }
        }
    }

    handleMessage(data) {
        // Handle different types of WebSocket messages
        switch (data.type) {
            case 'new_alert':
                this.handleNewAlert(data.alert);
                break;
            case 'correlation_update':
                this.handleCorrelationUpdate(data.correlation);
                break;
            case 'reputation_update':
                this.handleReputationUpdate(data.reputation);
                break;
            case 'system_stats':
                this.handleSystemStats(data.stats);
                break;
            case 'notification':
                this.showNotification(data.message, data.level);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    handleNewAlert(alert) {
        // Update dashboard with new alert
        if (window.updateDashboardAlerts) {
            window.updateDashboardAlerts(alert);
        }
        
        // Show notification
        this.showNotification(`New Alert: ${alert.title}`, 'warning');
    }

    handleCorrelationUpdate(correlation) {
        // Update correlation section
        if (window.updateCorrelations) {
            window.updateCorrelations(correlation);
        }
    }

    handleReputationUpdate(reputation) {
        // Update reputation section
        if (window.updateReputation) {
            window.updateReputation(reputation);
        }
    }

    handleSystemStats(stats) {
        // Update system statistics
        if (window.updateSystemStats) {
            window.updateSystemStats(stats);
        }
    }

    showNotification(message, level = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${level}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(level)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
        `;
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    getNotificationIcon(level) {
        switch (level) {
            case 'error': return 'times-circle';
            case 'warning': return 'exclamation-triangle';
            case 'success': return 'check-circle';
            default: return 'info-circle';
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.reconnectInterval) {
            clearInterval(this.reconnectInterval);
            this.reconnectInterval = null;
        }
    }
}

// Global WebSocket manager
const wsManager = new WebSocketManager();

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    wsManager.connect(wsUrl);
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    wsManager.disconnect();
});
