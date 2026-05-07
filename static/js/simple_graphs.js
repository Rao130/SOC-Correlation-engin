// Simple Graph System - New and Working with Real-time Updates
class SimpleGraphSystem {
    constructor() {
        this.charts = {};
        this.alerts = [];
        this.ws = null;
        this.isConnected = false;
        this.init();
    }

    init() {
        console.log('Starting Simple Graph System with Real-time Updates...');
        this.loadAlerts();
        this.initAllCharts();
        this.startAutoUpdate();
        this.initWebSocket();
    }

    async loadAlerts() {
        try {
            console.log('Loading alerts from API...');
            const response = await fetch('/api/alerts/?limit=1000');
            if (response.ok) {
                this.alerts = await response.json();
                console.log('✅ Loaded', this.alerts.length, 'alerts from API');
                console.log('Sample alert:', this.alerts[0]);
                this.updateAllCharts();
            } else {
                console.log('❌ API failed, using sample data');
                this.alerts = this.getSampleData();
                this.updateAllCharts();
            }
        } catch (error) {
            console.log('❌ Error loading data, using sample:', error);
            this.alerts = this.getSampleData();
            this.updateAllCharts();
        }
    }

    getSampleData() {
        return [
            { severity: 'critical', category: 'Network', assigned_to: 'John', timestamp: new Date() },
            { severity: 'high', category: 'Malware', assigned_to: 'Sarah', timestamp: new Date() },
            { severity: 'medium', category: 'Phishing', assigned_to: 'Mike', timestamp: new Date() },
            { severity: 'low', category: 'Policy', assigned_to: 'John', timestamp: new Date() },
            { severity: 'critical', category: 'DDoS', assigned_to: 'Sarah', timestamp: new Date() },
            { severity: 'high', category: 'SQL Injection', assigned_to: 'Mike', timestamp: new Date() },
            { severity: 'medium', category: 'XSS', assigned_to: 'John', timestamp: new Date() },
            { severity: 'low', category: 'Brute Force', assigned_to: 'Sarah', timestamp: new Date() }
        ];
    }

    initAllCharts() {
        this.createMagnitudeChart();
        this.createAssigneeChart();
        this.createTypeChart();
        this.createUrgencyChart();
        this.createTimeChart();
        console.log('All charts initialized');
    }

    createMagnitudeChart() {
        const ctx = document.getElementById('magnitudeChart');
        if (!ctx) return;

        this.charts.magnitude = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Alerts by Severity',
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#dc2626', '#ea580c', '#f59e0b', '#22c55e']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    createAssigneeChart() {
        const ctx = document.getElementById('assigneeChart');
        if (!ctx) return;

        this.charts.assignee = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    createTypeChart() {
        const ctx = document.getElementById('typeChart');
        if (!ctx) return;

        this.charts.type = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    createUrgencyChart() {
        const ctx = document.getElementById('urgencyChart');
        if (!ctx) return;

        this.charts.urgency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Events by Urgency',
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#dc2626', '#ea580c', '#d97706', '#65a30d']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    createTimeChart() {
        const ctx = document.getElementById('timeChart');
        if (!ctx) return;

        this.charts.time = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Alerts Over Time',
                    data: [],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    updateAllCharts() {
        console.log('🔄 Updating all charts with', this.alerts.length, 'alerts');
        this.updateMagnitudeChart();
        this.updateAssigneeChart();
        this.updateTypeChart();
        this.updateUrgencyChart();
        this.updateTimeChart();
        console.log('✅ All charts updated');
    }

    updateMagnitudeChart() {
        if (!this.charts.magnitude) return;

        const counts = this.countSeverity();
        console.log('📊 Severity counts:', counts);
        this.charts.magnitude.data.datasets[0].data = [
            counts.critical,
            counts.high,
            counts.medium,
            counts.low
        ];
        this.charts.magnitude.update();
    }

    updateAssigneeChart() {
        if (!this.charts.assignee) return;

        const counts = this.countByField('assigned_to');
        console.log('👥 Assignee counts:', counts);
        this.charts.assignee.data.labels = Object.keys(counts);
        this.charts.assignee.data.datasets[0].data = Object.values(counts);
        this.charts.assignee.update();
    }

    updateTypeChart() {
        if (!this.charts.type) return;

        const counts = this.countByField('category');
        console.log('📋 Category counts:', counts);
        this.charts.type.data.labels = Object.keys(counts);
        this.charts.type.data.datasets[0].data = Object.values(counts);
        this.charts.type.update();
    }

    updateUrgencyChart() {
        if (!this.charts.urgency) return;

        const counts = this.countSeverity();
        this.charts.urgency.data.datasets[0].data = [
            counts.critical,
            counts.high,
            counts.medium,
            counts.low
        ];
        this.charts.urgency.update();
    }

    updateTimeChart() {
        if (!this.charts.time) return;

        const timeData = this.getTimeData();
        this.charts.time.data.labels = timeData.labels;
        this.charts.time.data.datasets[0].data = timeData.data;
        this.charts.time.update();
    }

    countSeverity() {
        const counts = { critical: 0, high: 0, medium: 0, low: 0 };
        this.alerts.forEach(alert => {
            if (counts.hasOwnProperty(alert.severity)) {
                counts[alert.severity]++;
            }
        });
        return counts;
    }

    countByField(field) {
        const counts = {};
        this.alerts.forEach(alert => {
            let value = alert[field] || 'Unknown';
            if (value === null || value === undefined || value === '') {
                value = 'Unassigned';
            }
            counts[value] = (counts[value] || 0) + 1;
        });
        return counts;
    }

    getTimeData() {
        const hourly = {};
        const now = new Date();
        
        // Last 24 hours
        for (let i = 23; i >= 0; i--) {
            const hour = new Date(now - i * 60 * 60 * 1000);
            const key = hour.getHours().toString().padStart(2, '0') + ':00';
            hourly[key] = 0;
        }

        // Count alerts
        this.alerts.forEach(alert => {
            const alertTime = new Date(alert.timestamp);
            const key = alertTime.getHours().toString().padStart(2, '0') + ':00';
            if (hourly.hasOwnProperty(key)) {
                hourly[key]++;
            }
        });

        return {
            labels: Object.keys(hourly),
            data: Object.values(hourly)
        };
    }

    startAutoUpdate() {
        // Update every 30 seconds as backup
        setInterval(() => {
            if (!this.isConnected) {
                console.log('WebSocket not connected, using API fallback');
                this.loadAlerts();
            }
        }, 30000);
    }

    startHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // Send ping every 30 seconds
    }

    initWebSocket() {
        try {
            const clientId = 'graphs_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            const wsUrl = `ws://${window.location.hostname}:8000/ws/${clientId}`;
            
            console.log('🔌 Connecting WebSocket for real-time graph updates:', wsUrl);
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ WebSocket connected for real-time graph updates');
                this.isConnected = true;
                
                // Start heartbeat
                this.startHeartbeat();
                
                // Request initial data
                this.ws.send(JSON.stringify({
                    type: 'request_alerts',
                    limit: 1000
                }));
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = () => {
                console.log('❌ WebSocket disconnected');
                this.isConnected = false;
                
                // Attempt to reconnect after 5 seconds
                setTimeout(() => {
                    this.initWebSocket();
                }, 5000);
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
            };
            
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data.type);
        
        switch(data.type) {
            case 'initial_data':
                console.log('📊 Received initial data via WebSocket');
                if (data.recent_alerts && Array.isArray(data.recent_alerts)) {
                    this.alerts = data.recent_alerts;
                    this.updateAllCharts();
                }
                break;
                
            case 'new_alert':
                console.log('🚨 New alert received:', data.alert?.title);
                if (data.alert) {
                    // Add new alert to the beginning
                    this.alerts.unshift(data.alert);
                    
                    // Keep only last 1000 alerts
                    if (this.alerts.length > 1000) {
                        this.alerts = this.alerts.slice(0, 1000);
                    }
                    
                    // Update charts immediately
                    this.updateAllCharts();
                    
                    // Show notification
                    this.showAlertNotification(data.alert);
                }
                break;
                
            case 'alerts_response':
                console.log('📋 Alerts response received');
                if (data.alerts && Array.isArray(data.alerts)) {
                    this.alerts = data.alerts;
                    this.updateAllCharts();
                }
                break;
                
            case 'analytics_update':
                console.log('📈 Analytics update received');
                // Refresh data when analytics update comes
                this.loadAlerts();
                break;
                
            case 'metrics_update':
                console.log('📊 Metrics update received');
                // Refresh data when metrics update comes
                this.loadAlerts();
                break;
                
            case 'pong':
                // Heartbeat response - do nothing
                break;
                
            default:
                console.log('🔍 Unknown WebSocket message type:', data.type, data);
        }
    }

    showAlertNotification(alert) {
        // Create a simple notification for new alerts
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ef4444;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
            max-width: 300px;
        `;
        notification.innerHTML = `
            <strong>New Alert!</strong><br>
            <small>${alert.title}</small>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }
}

// Auto-start when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Simple Graph System with Real-time Updates...');
    window.simpleGraphs = new SimpleGraphSystem();
});
