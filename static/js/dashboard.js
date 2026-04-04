// Dashboard JavaScript
class Dashboard {
    constructor() {
        this.ws = null;
        this.charts = {};
        this.currentSection = 'dashboard';
        this.refreshInterval = null;
        this.alerts = [];
        this.correlations = [];
        this.reputationData = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initCharts();
        this.connectWebSocket();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Section navigation
        document.querySelectorAll('.nav-item a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('href').substring(1);
                this.showSection(section);
            });
        });

        // Search functionality
        document.getElementById('alert-search')?.addEventListener('input', (e) => {
            this.filterAlerts(e.target.value);
        });

        document.getElementById('reputation-search')?.addEventListener('input', (e) => {
            this.filterReputation(e.target.value);
        });

        // Filters
        document.getElementById('severity-filter')?.addEventListener('change', (e) => {
            this.filterAlertsBySeverity(e.target.value);
        });

        document.getElementById('time-range')?.addEventListener('change', (e) => {
            this.updateTimeRange(e.target.value);
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(`${sectionName}-section`);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const activeNavItem = document.querySelector(`[href="#${sectionName}"]`);
        if (activeNavItem) {
            activeNavItem.parentElement.classList.add('active');
        }

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    loadSectionData(section) {
        switch(section) {
            case 'dashboard':
                this.loadDashboardData();
                break;
            case 'alerts':
                this.loadAlerts();
                break;
            case 'correlation':
                this.loadCorrelations();
                break;
            case 'reputation':
                this.loadReputation();
                break;
            case 'maps':
                this.loadMapData();
                break;
            case 'analytics':
                this.loadAnalytics();
                break;
        }
    }

    async loadInitialData() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            this.updateSystemStats(data);
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadDashboardData() {
        try {
            const [alertsResponse, correlationsResponse, threatsResponse] = await Promise.all([
                fetch('/api/alerts?limit=10&sort=timestamp:desc'),
                fetch('/api/correlation?limit=5'),
                fetch('/api/threats/summary')
            ]);

            const alerts = await alertsResponse.json();
            const correlations = await correlationsResponse.json();
            const threats = await threatsResponse.json();

            this.updateRecentAlerts(alerts.data || []);
            this.updateKPIs(alerts, correlations, threats);
            this.updateCharts(alerts, threats);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts?limit=50');
            const data = await response.json();
            this.alerts = data.data || [];
            this.renderAlerts();
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    async loadCorrelations() {
        try {
            const response = await fetch('/api/correlation?limit=50');
            const data = await response.json();
            this.correlations = data.data || [];
            this.renderCorrelations();
        } catch (error) {
            console.error('Error loading correlations:', error);
        }
    }

    async loadReputation() {
        try {
            const response = await fetch('/api/reputation?limit=50');
            const data = await response.json();
            this.reputationData = data.data || [];
            this.renderReputation();
        } catch (error) {
            console.error('Error loading reputation data:', error);
        }
    }

    updateSystemStats(stats) {
        document.getElementById('active-alerts').textContent = stats.alerts?.new || 0;
        document.getElementById('correlations').textContent = stats.correlations?.active || 0;
        
        const threatLevel = this.calculateThreatLevel(stats);
        const threatElement = document.getElementById('threat-level');
        threatElement.textContent = threatLevel.text;
        threatElement.className = `stat-value threat-level-${threatLevel.level}`;
    }

    calculateThreatLevel(stats) {
        const criticalAlerts = stats.alerts?.critical || 0;
        const highAlerts = stats.alerts?.high || 0;
        const totalScore = (criticalAlerts * 4) + (highAlerts * 3);

        if (totalScore >= 20) return { level: 'critical', text: 'Critical' };
        if (totalScore >= 10) return { level: 'high', text: 'High' };
        if (totalScore >= 5) return { level: 'medium', text: 'Medium' };
        return { level: 'low', text: 'Low' };
    }

    updateKPIs(alerts, correlations, threats) {
        const criticalCount = alerts.data?.filter(a => a.severity === 'critical').length || 0;
        const threatsDetected = threats?.total || 0;
        const correlationsFound = correlations.data?.length || 0;
        const falsePositives = alerts.data?.filter(a => a.status === 'false_positive').length || 0;

        this.animateNumber('critical-alerts', criticalCount);
        this.animateNumber('threats-detected', threatsDetected);
        this.animateNumber('correlations-found', correlationsFound);
        this.animateNumber('false-positives', falsePositives);
    }

    animateNumber(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = parseInt(element.textContent) || 0;
        const duration = 1000;
        const startTime = performance.now();

        const updateNumber = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            
            element.textContent = currentValue;

            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };

        requestAnimationFrame(updateNumber);
    }

    updateRecentAlerts(alerts) {
        const tbody = document.getElementById('recent-alerts-tbody');
        if (!tbody) return;

        tbody.innerHTML = alerts.map(alert => `
            <tr>
                <td>${alert.alert_id}</td>
                <td>${alert.title}</td>
                <td><span class="severity-badge severity-${alert.severity}">${alert.severity}</span></td>
                <td><span class="status-badge status-${alert.status}">${alert.status}</span></td>
                <td>${this.formatTime(alert.timestamp)}</td>
                <td>
                    <button class="btn btn-sm" onclick="dashboard.showAlertDetails('${alert.alert_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    renderAlerts() {
        const grid = document.getElementById('alerts-grid');
        if (!grid) return;

        grid.innerHTML = this.alerts.map(alert => `
            <div class="alert-card" onclick="dashboard.showAlertDetails('${alert.alert_id}')">
                <div class="alert-card-header">
                    <div>
                        <div class="alert-card-title">${alert.title}</div>
                        <div class="alert-card-description">${alert.description}</div>
                    </div>
                    <span class="severity-badge severity-${alert.severity}">${alert.severity}</span>
                </div>
                <div class="alert-card-meta">
                    <span>${this.formatTime(alert.timestamp)}</span>
                    <span class="status-badge status-${alert.status}">${alert.status}</span>
                </div>
            </div>
        `).join('');

        // Update badge
        const badge = document.getElementById('alert-badge');
        if (badge) {
            const activeCount = this.alerts.filter(a => a.status === 'new').length;
            badge.textContent = activeCount;
            badge.style.display = activeCount > 0 ? 'inline-block' : 'none';
        }
    }

    renderCorrelations() {
        const grid = document.getElementById('correlation-grid');
        if (!grid) return;

        grid.innerHTML = this.correlations.map(correlation => `
            <div class="correlation-card">
                <div class="correlation-card-header">
                    <div>
                        <div class="correlation-card-title">${correlation.name}</div>
                        <div class="correlation-card-description">${correlation.description}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromScore(correlation.correlation_score)}">
                        Score: ${correlation.correlation_score}
                    </span>
                </div>
                <div class="correlation-card-meta">
                    <span>${correlation.metrics?.alert_count || 0} alerts</span>
                    <span>Confidence: ${correlation.confidence}%</span>
                </div>
            </div>
        `).join('');
    }

    renderReputation() {
        const grid = document.getElementById('reputation-grid');
        if (!grid) return;

        grid.innerHTML = this.reputationData.map(rep => `
            <div class="reputation-card">
                <div class="reputation-card-header">
                    <div>
                        <div class="reputation-card-title">${rep.entity}</div>
                        <div class="reputation-card-description">Type: ${rep.entity_type}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromRiskLevel(rep.risk_level)}">
                        ${rep.risk_level}
                    </span>
                </div>
                <div class="reputation-card-meta">
                    <span>Score: ${rep.aggregated_score}</span>
                    <span>Alerts: ${rep.metrics?.alert_count || 0}</span>
                </div>
            </div>
        `).join('');
    }

    getSeverityFromScore(score) {
        if (score >= 80) return 'critical';
        if (score >= 60) return 'high';
        if (score >= 40) return 'medium';
        return 'low';
    }

    getSeverityFromRiskLevel(riskLevel) {
        switch(riskLevel) {
            case 'malicious': return 'critical';
            case 'suspicious': return 'high';
            case 'benign': return 'low';
            default: return 'medium';
        }
    }

    initCharts() {
        // Alert Timeline Chart
        const timelineCtx = document.getElementById('alert-timeline-chart');
        if (timelineCtx) {
            this.charts.timeline = new Chart(timelineCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Alerts',
                        data: [],
                        borderColor: '#00d4ff',
                        backgroundColor: 'rgba(0, 212, 255, 0.1)',
                        tension: 0.4
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

        // Threat Distribution Chart
        const distributionCtx = document.getElementById('threat-distribution-chart');
        if (distributionCtx) {
            this.charts.distribution = new Chart(distributionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#d32f2f', '#f44336', '#ff9800', '#4caf50']
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
    }

    updateCharts(alerts, threats) {
        // Update timeline chart
        if (this.charts.timeline && alerts?.data) {
            const timelineData = this.processTimelineData(alerts.data);
            this.charts.timeline.data.labels = timelineData.labels;
            this.charts.timeline.data.datasets[0].data = timelineData.data;
            this.charts.timeline.update();
        }

        // Update distribution chart
        if (this.charts.distribution && alerts?.data) {
            const severityCounts = this.countBySeverity(alerts.data);
            this.charts.distribution.data.datasets[0].data = [
                severityCounts.critical,
                severityCounts.high,
                severityCounts.medium,
                severityCounts.low
            ];
            this.charts.distribution.update();
        }
    }

    processTimelineData(alerts) {
        const hourlyCounts = {};
        const now = new Date();
        
        // Initialize last 24 hours
        for (let i = 23; i >= 0; i--) {
            const hour = new Date(now - i * 60 * 60 * 1000);
            const key = hour.getHours().toString().padStart(2, '0') + ':00';
            hourlyCounts[key] = 0;
        }

        // Count alerts by hour
        alerts.forEach(alert => {
            const alertTime = new Date(alert.timestamp);
            const key = alertTime.getHours().toString().padStart(2, '0') + ':00';
            if (hourlyCounts.hasOwnProperty(key)) {
                hourlyCounts[key]++;
            }
        });

        return {
            labels: Object.keys(hourlyCounts),
            data: Object.values(hourlyCounts)
        };
    }

    countBySeverity(alerts) {
        const counts = { critical: 0, high: 0, medium: 0, low: 0 };
        alerts.forEach(alert => {
            if (counts.hasOwnProperty(alert.severity)) {
                counts[alert.severity]++;
            }
        });
        return counts;
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('WebSocket connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connectWebSocket(), 5000);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleWebSocketMessage(data) {
        switch(data.type) {
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
                this.updateSystemStats(data.stats);
                break;
        }
    }

    handleNewAlert(alert) {
        // Add to alerts array
        this.alerts.unshift(alert);
        
        // Update UI if on alerts section
        if (this.currentSection === 'alerts') {
            this.renderAlerts();
        }
        
        // Update dashboard stats
        this.updateSystemStats({
            alerts: { new: this.alerts.filter(a => a.status === 'new').length }
        });
        
        // Show notification
        this.showNotification(`New Alert: ${alert.title}`, 'warning');
    }

    handleCorrelationUpdate(correlation) {
        this.correlations.unshift(correlation);
        
        if (this.currentSection === 'correlation') {
            this.renderCorrelations();
        }
        
        this.showNotification(`New Correlation: ${correlation.name}`, 'info');
    }

    handleReputationUpdate(reputation) {
        const existingIndex = this.reputationData.findIndex(r => r.entity === reputation.entity);
        
        if (existingIndex >= 0) {
            this.reputationData[existingIndex] = reputation;
        } else {
            this.reputationData.unshift(reputation);
        }
        
        if (this.currentSection === 'reputation') {
            this.renderReputation();
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${this.getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.remove()">&times;</button>
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

    getNotificationIcon(type) {
        switch(type) {
            case 'warning': return 'exclamation-triangle';
            case 'error': return 'times-circle';
            case 'success': return 'check-circle';
            default: return 'info-circle';
        }
    }

    filterAlerts(searchTerm) {
        const filtered = this.alerts.filter(alert => 
            alert.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            alert.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderFilteredAlerts(filtered);
    }

    filterAlertsBySeverity(severity) {
        const filtered = severity ? 
            this.alerts.filter(alert => alert.severity === severity) :
            this.alerts;
        this.renderFilteredAlerts(filtered);
    }

    filterReputation(searchTerm) {
        const filtered = this.reputationData.filter(rep => 
            rep.entity.toLowerCase().includes(searchTerm.toLowerCase())
        );
        this.renderFilteredReputation(filtered);
    }

    renderFilteredAlerts(alerts) {
        // Similar to renderAlerts but with filtered data
        const grid = document.getElementById('alerts-grid');
        if (!grid) return;

        grid.innerHTML = alerts.map(alert => `
            <div class="alert-card" onclick="dashboard.showAlertDetails('${alert.alert_id}')">
                <div class="alert-card-header">
                    <div>
                        <div class="alert-card-title">${alert.title}</div>
                        <div class="alert-card-description">${alert.description}</div>
                    </div>
                    <span class="severity-badge severity-${alert.severity}">${alert.severity}</span>
                </div>
                <div class="alert-card-meta">
                    <span>${this.formatTime(alert.timestamp)}</span>
                    <span class="status-badge status-${alert.status}">${alert.status}</span>
                </div>
            </div>
        `).join('');
    }

    renderFilteredReputation(reputation) {
        // Similar to renderReputation but with filtered data
        const grid = document.getElementById('reputation-grid');
        if (!grid) return;

        grid.innerHTML = reputation.map(rep => `
            <div class="reputation-card">
                <div class="reputation-card-header">
                    <div>
                        <div class="reputation-card-title">${rep.entity}</div>
                        <div class="reputation-card-description">Type: ${rep.entity_type}</div>
                    </div>
                    <span class="severity-badge severity-${this.getSeverityFromRiskLevel(rep.risk_level)}">
                        ${rep.risk_level}
                    </span>
                </div>
                <div class="reputation-card-meta">
                    <span>Score: ${rep.aggregated_score}</span>
                    <span>Alerts: ${rep.metrics?.alert_count || 0}</span>
                </div>
            </div>
        `).join('');
    }

    async showAlertDetails(alertId) {
        try {
            const response = await fetch(`/api/alerts/${alertId}`);
            const alert = await response.json();
            
            this.showModal('alert-modal', this.renderAlertDetails(alert));
        } catch (error) {
            console.error('Error loading alert details:', error);
        }
    }

    renderAlertDetails(alert) {
        return `
            <div class="alert-details">
                <h3>${alert.title}</h3>
                <div class="detail-row">
                    <label>Severity:</label>
                    <span class="severity-badge severity-${alert.severity}">${alert.severity}</span>
                </div>
                <div class="detail-row">
                    <label>Status:</label>
                    <span class="status-badge status-${alert.status}">${alert.status}</span>
                </div>
                <div class="detail-row">
                    <label>Description:</label>
                    <p>${alert.description}</p>
                </div>
                <div class="detail-row">
                    <label>Time:</label>
                    <span>${this.formatTime(alert.timestamp)}</span>
                </div>
                <div class="detail-row">
                    <label>Entities:</label>
                    <div class="entities-list">
                        ${alert.entities?.map(entity => 
                            `<span class="entity-tag">${entity.type}: ${entity.value}</span>`
                        ).join('') || 'None'}
                    </div>
                </div>
                <div class="detail-actions">
                    <button class="btn btn-primary" onclick="dashboard.updateAlertStatus('${alert.alert_id}', 'investigating')">
                        Mark as Investigating
                    </button>
                    <button class="btn btn-secondary" onclick="dashboard.updateAlertStatus('${alert.alert_id}', 'resolved')">
                        Mark as Resolved
                    </button>
                </div>
            </div>
        `;
    }

    async updateAlertStatus(alertId, status) {
        try {
            const response = await fetch(`/api/alerts/${alertId}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            
            if (response.ok) {
                this.closeModal('alert-modal');
                this.showNotification('Alert status updated', 'success');
                this.loadAlerts(); // Reload alerts
            }
        } catch (error) {
            console.error('Error updating alert status:', error);
        }
    }

    showModal(modalId, content) {
        const modal = document.getElementById(modalId);
        const body = modal.querySelector('.modal-body');
        body.innerHTML = content;
        modal.style.display = 'block';
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.style.display = 'none';
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadSectionData(this.currentSection);
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    updateTimeRange(range) {
        // Implement time range filtering logic
        console.log('Time range changed to:', range);
        this.loadDashboardData();
    }

    async createAlert() {
        // Implement alert creation logic
        console.log('Create new alert');
    }

    async runCorrelationAnalysis() {
        try {
            const response = await fetch('/api/correlation/analyze', { method: 'POST' });
            const result = await response.json();
            
            this.showNotification('Correlation analysis started', 'info');
            this.loadCorrelations();
        } catch (error) {
            console.error('Error running correlation analysis:', error);
        }
    }

    async checkReputation() {
        const searchInput = document.getElementById('reputation-search');
        const entity = searchInput?.value.trim();
        
        if (!entity) {
            this.showNotification('Please enter an entity to check', 'warning');
            return;
        }

        try {
            const response = await fetch(`/api/reputation/check`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ entity })
            });
            
            const result = await response.json();
            this.showNotification(`Reputation check completed for ${entity}`, 'success');
            this.loadReputation();
        } catch (error) {
            console.error('Error checking reputation:', error);
        }
    }

    loadMapData() {
        // This will be handled by maps.js
        if (window.mapManager) {
            window.mapManager.loadThreatData();
        }
    }

    loadAnalytics() {
        // This will be handled by analytics.js
        if (window.analyticsManager) {
            window.analyticsManager.loadAnalyticsData();
        }
    }
}

// Global functions
function showSection(section) {
    dashboard.showSection(section);
}

function refreshDashboard() {
    dashboard.loadSectionData(dashboard.currentSection);
}

function closeModal(modalId) {
    dashboard.closeModal(modalId);
}

function createAlert() {
    dashboard.createAlert();
}

function runCorrelationAnalysis() {
    dashboard.runCorrelationAnalysis();
}

function checkReputation() {
    dashboard.checkReputation();
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// Close modals when clicking outside
window.addEventListener('click', (event) => {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
});

// Add notification styles
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(26, 26, 62, 0.95);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 1rem 1.5rem;
        color: white;
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 1rem;
        min-width: 300px;
        animation: slideInRight 0.3s ease;
    }
    
    .notification-info { border-left: 4px solid #00d4ff; }
    .notification-warning { border-left: 4px solid #ff9800; }
    .notification-error { border-left: 4px solid #f44336; }
    .notification-success { border-left: 4px solid #4caf50; }
    
    .notification button {
        background: none;
        border: none;
        color: white;
        font-size: 1.2rem;
        cursor: pointer;
        margin-left: auto;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .alert-details .detail-row {
        margin-bottom: 1rem;
    }
    
    .alert-details label {
        font-weight: bold;
        color: #00d4ff;
        display: inline-block;
        width: 100px;
    }
    
    .entities-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    
    .entity-tag {
        background: rgba(0, 212, 255, 0.2);
        color: #00d4ff;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    
    .detail-actions {
        margin-top: 1.5rem;
        display: flex;
        gap: 1rem;
    }
    
    .btn-sm {
        padding: 0.5rem 1rem;
        font-size: 0.8rem;
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);
